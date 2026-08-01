# FR4 7 阶交指滤波器搜索算法改进方案

Status: Active
Domain: OPT
Canonical: `docs/opt/FR4交指滤波器搜索算法改进方案.md`
Related: `docs/README.md`, `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`, `docs/devices/交指带通滤波器回波损耗影响因素.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`
Last updated: 2026-08-01
Owner: ADS Automation

## 1. 当前六轮搜索暴露的问题

六轮搜索后，最佳结果仍是初始模板：

| 候选 | S21@5G | S21@6G | S21@8G | 6-8G 最差 S11 | 6-8G 最差 S22 | 纹波 |
|---|---:|---:|---:|---:|---:|---:|
| `i7_fr4_r3_base/r4_base/r5_base/r6_base` | -27.15 dB | -2.13 dB | -4.28 dB | -5.55 dB | -5.98 dB | 2.83 dB |

它满足 `S21@5G <= -25 dB`、`S21@6/8G >= -5 dB`、纹波约束，但 `S11` 距离 `-6 dB` 目标还差约 `0.45 dB`，`S22` 仅差约 `0.02 dB`。

低效的根本原因不是 ADS 仿真慢，而是候选点选择方式低效：

- 过去主要是一维或少量组合扫描，参数之间强耦合时很容易“一个指标改善，另一个指标越界”。
- 交指滤波器的回损由外部 Q、抽头位置、馈线过渡、端部加载、相邻谐振器耦合共同决定，不适合只看单变量趋势。
- 当前可行区域很窄。`L`、`feed_tip_w`、`feed_len`、`W0` 的已有结果表明，稍微偏离基线就可能破坏 5 GHz 阻带、8 GHz 通带边缘或回损。
- 数据量仍偏小，直接训练神经网络会过拟合；现在更适合代理模型、信赖域和主动学习。

## 2. 不建议直接使用普通梯度下降

ADS FEM 对这里的优化来说是黑盒函数：

```text
layout vector x -> ADS/RFPro FEM -> S 参数曲线 -> 指标/评分
```

这个函数昂贵、不可解析求导，且可能有网格误差和非光滑响应。普通梯度下降需要稳定梯度，直接用于 FEM 闭环并不合适。

更合适的是以下两类算法：

- `MADS/Pattern Search`：适合昂贵黑盒；有当前最好点时，沿参数方向轮询；如果无改进就缩小步长。
- `Bayesian/Surrogate Optimization`：用历史仿真点训练代理模型，在虚拟候选池上计算期望改进，再挑少量点进入 ADS。

本项目当前建议采用混合方案：

```text
历史 ADS 数据 -> 训练集 -> 约束评分 -> 代理模型 -> 信赖域候选池 -> EI 排序 -> 少量 ADS 仿真 -> 回填训练集
```

## 3. 参数向量化

当前先使用对称参数，避免同时引入过多自由度：

```text
x = [
  L_mm,
  tap_mm,
  Egap_mm,
  S1S6_mm,
  S2S5_mm,
  S3S4_mm,
  W0_mm,
  feed_len_mm,
  feed_taper_len_mm,
  feed_tip_w_mm,
  feed_overlap_mm
]
```

导出到版图时展开为：

```text
S1 = S6 = S1S6
S2 = S5 = S2S5
S3 = S4 = S3S4
```

后续如果 S11/S22 明显不对称，再打开非对称参数：

```text
S1_delta = S1 - S6
S2_delta = S2 - S5
S3_delta = S3 - S4
```

## 4. 评分函数

当前目标为：

```text
S21@5G <= -25 dB
S21@6G >= -5 dB
S21@8G >= -5 dB
passband_min_s21 >= -5 dB
passband_ripple <= 4 dB
worst S11/S22 in 6-8G <= -6 dB
```

评分原则：

- 先硬约束：阻带、通带边缘、通带最小插损、纹波不能被牺牲。
- 再优化回损：在硬约束满足后，优先降低 `max(S11, S22)`。
- 对 `S11/S22` 的轻微违规给较大惩罚，但不完全丢弃，因为当前最好点只差很小。

新增脚本 `SIM\tools\build_i7_fr4_optimization_dataset.py` 会计算：

- 每个约束的 dB 余量；
- `hard_constraints_ok`；
- `rl6_ok`；
- `objective_score`；
- `geometry_key`，用于识别重复几何。

## 5. 当前实现的搜索算法

新增脚本：

```text
SIM\tools\propose_i7_fr4_surrogate_candidates.py
```

算法流程：

1. 读取 `interdigital_7o_fr4_training_dataset.csv`。
2. 合并重复几何，保留平均指标。
3. 用 bootstrap 线性岭回归建立代理模型集成。
4. 在基线附近生成大量对称信赖域候选。
5. 对每个候选预测 S 参数关键指标。
6. 计算相对当前最好分数的 `Expected Improvement`。
7. 过滤明显违反阻带/通带硬约束的点。
8. 用距离约束保证不重复、不远离训练区。
9. 输出少量 round7 候选和预测报告。

这里暂不使用神经网络。原因是现有唯一几何只有约 39 个，远不足以支撑神经网络泛化。等累积到 150-300 个仿真点后，可以升级为：

- ExtraTrees/RandomForest 代理；
- Gaussian Process；
- 小型 MLP ensemble；
- 多输出神经网络加不确定度估计。

## 6. 已生成的 round7 文件

训练集：

```text
SIM\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_training_dataset.csv
```

round7 候选参数：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round7.csv
```

round7 版图输出：

```text
SIM\projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7
```

round7 代理模型预测：

```text
SIM\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_round7_predictions.csv
```

当前 round7 候选不是“代理模型已经确信优于基线”的点，而是“在硬约束附近、EI 最高、最值得补充 FEM 数据”的点。预测概率 `P+` 只有约 `0.10-0.16`，说明当前模型仍缺数据，不能盲目扩大搜索。

## 7. 下一轮推荐执行方式

先仿真 EI 排名前 3-4 个，而不是一次跑完所有点：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe SIM\tools\run_ads_filter_sweep.py --profile home --template-cell BFP --target-profile fr4_25db_rl6 --plan SIM\projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round7.csv --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7 --results-dir SIM\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7 --summary SIM\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7\sweep_summary.csv --skip-generate --continue-on-error --candidates i7_fr4_r7_bo04 i7_fr4_r7_bo01 i7_fr4_r7_bo03 i7_fr4_r7_bo05
```

仿真完成后：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe SIM\tools\build_i7_fr4_optimization_dataset.py
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe SIM\tools\propose_i7_fr4_surrogate_candidates.py --round-name round8 --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round8 --plan SIM\projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round8.csv --prediction-report SIM\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_round8_predictions.csv
```

如果 round7 没有任何点改善基线，则不要扩大边界，应缩小信赖域并优先补以下方向：

- `feed_tip_w_mm` 在 `0.18-0.20` 的更密局部；
- `feed_overlap_mm` 在 `0.055-0.066`；
- `tap_mm` 在 `1.94-1.96`；
- `Egap_mm` 用于补偿 5 GHz 阻带；
- 内部 gap 暂时只做对称小扰动，避免同时破坏通带纹波。







