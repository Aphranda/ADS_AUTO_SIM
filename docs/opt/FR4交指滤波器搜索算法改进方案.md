# FR4 7 阶交指滤波器搜索算法改进方案

Status: Active
Domain: OPT
Canonical: `docs/opt/FR4交指滤波器搜索算法改进方案.md`
Related: `docs/README.md`, `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`, `docs/devices/交指带通滤波器回波损耗影响因素.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`
Last updated: 2026-08-02
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

round7 仍以 ridge surrogate 为低成本基线。原因是当时唯一几何只有约 39 个，直接训练一个不带物理约束的通用神经网络容易过拟合。后续不再等待 150-300 个点后才启用神经网络，而是采用第 8 节的“细化参数网络”：把交指滤波器拆成谐振器、间隙、馈电和物理派生特征几个通道，在 legacy 最佳点附近做窄信赖域主动学习。

随着 RFPro 数据增加，可并行保留以下非神经网络基线用于交叉验证：

- ExtraTrees/RandomForest 代理；
- Gaussian Process；
- 小型 MLP ensemble；
- Gaussian Process / ExtraTrees 不确定度估计；
- 细化参数神经网络加 ensemble 方差估计。

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

## 8. 细化参数网络方案

2026-08-02 起，交指分支从“少量指标的 ridge surrogate”升级为“细化参数 S 参数曲线 surrogate”。迁移基点采用 legacy 报告 `projects/bfp_6_8g_i7_fr4/reports/legacy/6-8G_7O滤波器设计优化报告.html` 中的当前推荐候选：

```text
i7_fr4_r1_l555_taper / 后续 r3-r6 base 复测等价几何
L_mm              = 5.55
tap_mm            = 1.95
Egap_mm           = 0.4823
S1/S6             = 0.1176
S2/S5             = 0.1750
S3/S4             = 0.1857
W0_mm             = 0.3648
feed_len_mm       = 3.0
feed_taper_len_mm = 0.60
feed_tip_w_mm     = 0.18
feed_overlap_mm   = 0.06
via_diameter_mm   = 0.254
```

该基点的 FEM 结果为：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 通带最差 | Ripple | S11/S22 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `i7_fr4_r3/r4/r5/r6_base` | -27.15 | -2.13 | -2.43 | -4.28 | -58.64 | -4.28 | 2.83 | -5.55 / -5.98 |

这个点已经满足 5 GHz 阻带、6/8 GHz 通带边缘和纹波阶段目标，主要短板是 `S11/S22` 只在约 `-6 dB` 附近。神经网络优化的第一目标不是重新发现拓扑，而是在这个窄信赖域内学习 `tap/taper/feed/gap` 对曲线的连续影响，优先改善匹配，同时不得破坏 `S21@5G` 带阻和 `6-8 GHz` 通带。

### 8.1 为什么采用细化参数网络

交指滤波器不是二维码像素拓扑问题。它的几何自由度少、参数连续、物理分组明确：谐振器长度决定中心频率，间隙决定相邻耦合，抽头和馈线决定外部耦合，线宽和过孔影响损耗与阻抗。普通 MLP 把所有参数揉成一个向量，数据少时很容易学到偶然相关；细化参数网络先按物理通道编码，再融合预测 S 参数曲线，更适合当前几十到一百多个 RFPro 样本的主动学习场景。

该方案仍不是用神经网络替代 ADS/RFPro。网络只负责在 legacy 最佳点附近筛选候选、估计趋势和排序；最终有效性以 ADS/RFPro 的 `1-10 GHz` S 参数为准。

### 8.2 输入通道设计

输入不只保留原始几何参数，还显式加入对称压缩、非对称微调和物理派生特征。这样做的价值是让网络同时看到“真实版图变量”和“滤波器设计中更有意义的组合变量”。

**谐振器 / 基础几何通道**

```text
L_mm
W0_mm
via_diameter_mm
via_pad_mm            # 若版图生成器已有该字段则纳入，否则第一版留空
Egap_mm
```

该通道主要对应中心频率、微带阻抗、端部寄生和接地过孔影响。`L_mm` 是最敏感的中心频率变量，`W0_mm` 同时影响阻抗、损耗和耦合强度，`Egap_mm` 用于调低边阻带和端部寄生。

**耦合间隙通道**

```text
S1_mm, S2_mm, S3_mm, S4_mm, S5_mm, S6_mm
S1S6_mean = (S1_mm + S6_mm) / 2
S2S5_mean = (S2_mm + S5_mm) / 2
S3S4_mean = (S3_mm + S4_mm) / 2
S1S6_delta = S1_mm - S6_mm
S2S5_delta = S2_mm - S5_mm
S3S4_delta = S3_mm - S4_mm
```

第一轮 round8 建议锁定 `delta = 0`，只搜索对称 gap。等 `S11/S22` 出现明显不对称、或者模型显示某侧 gap 对匹配有稳定收益后，再释放 `S1S6_delta/S2S5_delta/S3S4_delta` 做小范围非对称微调。

**外部耦合 / 馈电通道**

```text
tap_mm
tap_over_L = tap_mm / L_mm
feed_len_mm
feed_taper_len_mm
feed_tip_w_mm
feed_overlap_mm
feed_tip_over_W0 = feed_tip_w_mm / W0_mm
feed_overlap_over_W0 = feed_overlap_mm / W0_mm
```

该通道是改善 `S11/S22` 的主通道。当前基点的 `S21` 已经不错，匹配短板更可能来自外部 Q 和馈电耦合强度不合适，因此 `tap_mm/feed_tip_w_mm/feed_overlap_mm/feed_taper_len_mm` 应作为 round8 的重点变量。

**物理派生特征通道**

```text
L_over_lambda_g_7g
gap_i_over_W0 = S_i / W0_mm
min_gap_over_W0
max_gap_over_W0
gap_gradient_12 = S2_mm - S1_mm
gap_gradient_23 = S3_mm - S2_mm
gap_gradient_34 = S4_mm - S3_mm
gap_gradient_45 = S5_mm - S4_mm
gap_gradient_56 = S6_mm - S5_mm
coupling_proxy_i = exp(-S_i / W0_mm) 或 W0_mm / S_i
feed_external_Q_proxy = f(tap_over_L, feed_tip_over_W0, feed_overlap_over_W0)
```

这些派生特征是辅助网络学习的弱物理先验，不替代 ADS，也不作为最终评价依据。第一版可以先实现 `W0 / S_i` 类型的稳定 proxy，后续样本变多后再比较 `exp(-S_i / W0)` 是否更有用。

### 8.3 网络架构

已有脚手架：

```text
src/simads/nn/interdigital_surrogate.py
```

下一步把当前 residual MLP 拆成多分支编码器：

```text
resonator_encoder(x_resonator) -> z_res
gap_encoder(x_gap_raw + x_gap_sym + x_gap_delta) -> z_gap
feed_encoder(x_feed) -> z_feed
derived_encoder(x_derived) -> z_phy

concat(z_res, z_gap, z_feed, z_phy)
-> residual MLP trunk
-> curve_head: S11/S21/S22 over fixed frequency grid
-> feature_head: passband_min/ripple/S21@5/6/8/9/high_stop/max_return
```

第一版采用固定频点输出，优先兼容现有 RFPro CSV 和 SVG 曲线生成。等数据量增加后，可以增加 frequency-query head：

```text
geometry latent + freq embedding -> S11/S21/S22 at queried frequency
```

frequency-query head 的优势是能自然支持 `4-10 GHz` 历史数据和 `1-10 GHz` 新数据混合训练，但第一版实现复杂度更高，暂不作为 round8 的阻塞项。

### 8.4 数据集格式

现有数据来自：

```text
projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_training_dataset.csv
projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/
```

第一版构建 NPZ 数据集，建议字段如下：

```text
x_raw             # 原始几何参数，含 L/tap/Egap/S1-S6/W0/feed/via
x_sym             # S1S6_mean/S2S5_mean/S3S4_mean 等对称压缩特征
x_delta           # S1S6_delta/S2S5_delta/S3S4_delta，round8 可全为 0
x_derived         # lambda_g、gap ratio、coupling proxy、feed proxy
y_s_db            # [sample, port, freq]，port 顺序 S11/S21/S22
valid_s_mask      # 缺失频点或缺失端口的 mask
freq_ghz          # 训练频率网格
candidate_names   # 候选名，便于追溯版图和 RFPro CSV
metadata_json     # 数据来源、round、仿真配置、归一化统计
```

历史 `4-10 GHz` 数据可以先插值到统一网格；round8 到 round11b 曾统一使用 `1-10 GHz`，用于确认 1-4 GHz 低边阻带是否存在异常。实测显示当前 7 阶交指结构在 1-4 GHz 稳定处于深阻带，后续常规闭环改回 `4-10 GHz`，重点覆盖 5 GHz 带阻、6-8 GHz 通带和 9-10 GHz 高边阻带。所有结果目录继续输出 `filter_features.csv` 和 SVG S 曲线，SVG 至少包含 `S11/S21/S22` 叠加图。

### 8.5 损失函数和排序目标

交指分支不同于二维码分支：当前 baseline 的 `S21@5G` 和高边阻带已经有价值，真正瓶颈在通带匹配。因此训练仍保留 `S11/S22` 曲线，且权重应高于二维码分支，但 `S21` 仍是主反馈。

初始曲线拟合权重：

```text
S11:S21:S22 = 0.25:1.0:0.25
```

如果数轮后回损改善停滞，可调整为：

```text
S11:S21:S22 = 0.3:1.0:0.3
```

候选排序使用硬约束加软奖励：

```text
强惩罚：S21@5G > -25 dB
强惩罚：S21@6G < -5 dB
强惩罚：S21@8G < -5 dB
强惩罚：passband_min_s21 < -5 dB
强惩罚：passband_ripple > 4 dB

主奖励：worst(S11,S22) in 6-8G 更负
阶段目标：worst(S11,S22) 先稳定 <= -6 dB，再向 -10 dB 推进
辅助保护：S21@9G / high-side stopband 不得明显退化
```

这里的 `S11/S22` 不是主硬指标，但必须参与训练和排序，否则模型会只优化插损与阻带，继续停留在 `-6 dB` 左右的匹配水平。

### 8.6 round8 候选生成策略

第一批 NN 候选不要扩大参数边界。建议围绕 legacy 最佳点做窄信赖域，并先保持 gap 对称：

```text
L_mm:              5.535 - 5.565
tap_mm:            1.93  - 1.97
Egap_mm:           0.462 - 0.502
S1/S6:             0.112 - 0.124
S2/S5:             0.168 - 0.182
S3/S4:             0.180 - 0.192
W0_mm:             0.350 - 0.375
feed_taper_len_mm: 0.45  - 0.75
feed_tip_w_mm:     0.17  - 0.22
feed_overlap_mm:   0.052 - 0.070
```

主动学习循环：

```text
历史 round2-round7 RFPro CSV
-> build interdigital S-curve NPZ dataset
-> train refined-parameter NN surrogate
-> 在 i7_fr4_r1_l555_taper 附近生成 5-10 万虚拟候选
-> NN 预测 S11/S21/S22 曲线和关键特征
-> 按硬约束、匹配收益、模型不确定度和参数距离排序
-> 选 6-8 个代表候选进入 ADS/RFPro
-> 刷新 SVG S 曲线、filter_features.csv、训练集
-> 下一轮缩小、偏移信赖域，必要时释放 gap delta
```

round8 的建议顺序是先训练和排名，再只仿真 6-8 个候选。候选应覆盖三类：预测最优点、预测稳健点、探索点。探索点不应远离 legacy 基点，只用于补足模型对 `tap/feed/gap` 局部梯度的判断。

### 8.7 频点数和仿真时间策略

round8 结果暴露出一个数据质量问题：部分 RFPro CSV 只有 20 个频点，SVG 曲线会明显折线化，`passband_min_s21/ripple/worst_s11/worst_s22` 也可能因为漏采窄谷或窄峰而失真。20 点数据仍可用于粗筛和趋势判断，但不应作为高置信训练标签。

基于 round8 的真实耗时记录：

```text
20 点 Adaptive:   约 56-114 s / candidate
1000 点 Adaptive: 约 60-140 s / candidate
round8 top8 总耗时约 777 s
```

上述数据不能直接证明 `Linear 1001` 也同样快，因为 Adaptive 可能只求解少量关键频点。round10/round11b 的 `Linear 46, 1-10 GHz` 并发闭环均约 `8.1 min / top8`，单候选平均约 `115 s`。综合 round11b 结果，1-4 GHz 平均 S21 约 `-60 dB`，对当前 7 阶交指滤波器已足够稳定，后续采用分级策略：

```text
粗筛/快速排错：Adaptive 20-40 点，只看响应大类，不进高质量训练集
常规闭环 top8：Linear 40 点，4-10 GHz，约 153.846 MHz 间隔
候选复核/出图：Linear 201 点，4-10 GHz，约 30 MHz 间隔
最终确认/高质量训练：Linear 601 点，4-10 GHz，约 10 MHz 间隔
```

`Linear 40, 4-10 GHz` 不会正好落在 5/6/8/9 GHz，评分脚本必须继续用插值计算关键频点。如果需要关键整数 GHz 精确落点，可切换到 `Linear 31/41/61`，分别对应 200/150/100 MHz 间隔。round12 实测 `Linear 40, 4-10 GHz` 的单候选平均耗时约 `105.7 s`，比 round11b 的 `Linear 46, 1-10 GHz` 平均 `115.1 s` 降低约 8%，但 top8 wall time 仍约 `485 s`，说明当前瓶颈主要是 FEM 固定开销和 `workers=2` 长尾调度。

训练集构建脚本需要记录源 CSV 的频点数、全频最大步进、6-8 GHz 最大步进，并默认跳过 6-8 GHz 内步进过大的样本。SVG 可以做显示插值，但评分和训练必须以真实仿真频点质量为准。

### 8.8 ADS 模板工程、层叠命名和并发验证

为支持后续交指滤波器并发迭代，已新建独立 ADS workspace：

```text
D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR
```

命名规则分两层：

```text
workspace      = SIMADS_EM_PAR
library        = SIMADS_EM_PAR_lib
template cell  = SIMADS_EM_TEMPLATE_2PORT_FEM
stackup/subst  = FR4_210UM
profile        = home_simads_em_parallel
```

模板 cell 保持通用，只表达“2 端口 FEM 模板”；层叠是专用资产，必须把材料和厚度写入 substrate 命名。当前层叠使用 `FR4_210UM.subst`，profile 中引用 `SIMADS_EM_PAR_lib:FR4_210UM`。旧候选参数中的 `substrate4` 只作为历史兼容字段，不再优先决定 emSetup 的层叠引用。

初始化模板 workspace 时必须同步复制：

```text
FR4_210UM.subst       # 由源 substrate4.subst 复制并规范命名
materials.matdb       # 包含 FR_4 材料定义
em%Setup              # 来自已验证模板，只 patch workspace/library/cell/substrate
lib.defs              # 必须无 BOM；ADS lib.defs 解析器不接受 UTF-8 BOM
```

已验证的问题和结论：

| 项目 | 结论 |
|---|---|
| `lib.defs` UTF-8 BOM | 会导致 ADS 打开 workspace 报 `Unexpected token, "INCLUDE"`；必须写无 BOM UTF-8/ASCII。 |
| 只复制 `.subst` 不复制 `materials.matdb` | RFPro 创建 view 会报 `Could not find material "FR_4"`。 |
| 2 worker `--skip-fem` | 已通过，同一 workspace 下两个候选可并发完成布局复用、emSetup 克隆和 RFPro view 准备。 |
| 单候选 `Linear 91` | `i7_fr4_r9_asym0237` 在新 workspace 完成真实 FEM，耗时约 `205 s / 3.42 min`。 |
| 2 worker 真实 FEM | `i7_fr4_r9_asym0237/i7_fr4_r9_asym0272` 同时完成，wall time `290.2 s`；两颗串行按 `205 s` 估算约 `410 s`，实际吞吐约 `1.4x`。 |

并发验证后的两颗 round9 候选特征：

| 候选 | 耗时 | S21@5G | S21@6G | S21@8G | S21@9G | 通带最差 | Ripple | worst S11/S22 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `i7_fr4_r9_asym0237` | 290.2 s | -25.53 | -3.56 | -7.06 | -46.06 | -7.06 | 5.66 | -2.80 / -2.83 |
| `i7_fr4_r9_asym0272` | 285.1 s | -27.65 | -3.15 | -5.77 | -52.12 | -5.77 | 4.26 | -3.82 / -3.65 |

结论：并发可用，但当前 `workers=2` 并不会线性提速，可能受 CPU、内存、RFPro/xxPro 进程和 FEM license 调度共同限制。短期建议用 `workers=2` 跑低点数快速闭环；`workers=3+` 需要单独小样本验证，不能直接用于整轮 top8。

round10/round11b 快速闭环使用 `Linear 46, 1-10 GHz`。该设置间隔为 `200 MHz`，相比 `Linear 51` 的 `180 MHz` 更适合当时目标，因为它正好包含 `5/6/7/8/9 GHz` 关键反馈点，可降低插值对 5 GHz 带阻和 6/8 GHz 通带边缘判断的影响。round11b 后，后续常规闭环改回 `Linear 40, 4-10 GHz`，评分继续插值读取关键频点。

round12 已验证 `Linear 40, 4-10 GHz` 可用于闭环。该轮以 `i7_fr4_r11b_asym3016` 为中心，用 `S21@5 <= -26 dB` 保护约束选 top8。实测最好 5 GHz 带阻为 `i7_fr4_r12_asym3898` 和 `i7_fr4_r12_asym3263`，分别约 `-26.92/-26.90 dB`；但回损仍偏弱，`3898` 的 `S11/S22` 约 `-4.19/-4.03 dB`，说明模型对回损仍系统性乐观，后续候选排序需要对 `worst_s11/worst_s22` 做约 `+1.7/+2.2 dB` 的保守校正，或者直接要求预测回损比目标更深。

理论锚点 `i7_fr4_theory_marki_20260802` 已按 Marki 7 阶 Chebyshev 原始尺寸生成并在同一 `FR4_210UM` 模板工程中仿真，频率口径为 `Linear 40, 4-10 GHz`。理论尺寸为 `W0=W=0.3585 mm`、`L=5.792 mm`、`tap=1.932 mm`、`Egap=0.478 mm`、`S1..S6=0.1182/0.1753/0.1860/0.1860/0.1753/0.1182 mm`。RFPro 单点耗时约 `70 s`，ADS EM 结果为 `S21@5=-22.07 dB`、`S21@6=-1.48 dB`、`S21@7=-4.73 dB`、`S21@8=-4.83 dB`、`S21@9=-47.26 dB`，通带最差 `-4.94 dB`，ripple `3.47 dB`，`worst S11/S22=-2.96/-3.02 dB`。该点说明理论长度和间距可提供更低 6 GHz 插损和良好高边阻带，但 5 GHz 阻带和回损弱于 round12 最佳优化点，不宜直接作为最终版图；更适合作为后续局部搜索的一个长谐振器锚点，用来探索 `L/tap/feed` 对回损和低边阻带的折中。

## 9. 待办

- [x] 确认 legacy 报告最佳基点：`i7_fr4_r1_l555_taper`，等价于当前训练集中的 `r3/r4/r5/r6_base`。
- [x] 保留现有 ridge surrogate 作为低成本候选生成基线。
- [x] 新增交指 residual MLP 曲线代理脚手架：`src/simads/nn/interdigital_surrogate.py`。
- [x] 将 `InterdigitalSParamSurrogate` 拆成 `resonator_encoder/gap_encoder/feed_encoder/derived_encoder` 多分支结构。
- [x] 新增 `tools/build_interdigital_nn_dataset.py`，输出 `x_raw/x_sym/x_delta/x_derived/y_s_db/valid_s_mask/freq_ghz` NPZ；当前已构建 55 个样本。
- [x] 新增 `tools/train_interdigital_surrogate.py`，支持 `S11:S21:S22 = 0.25:1.0:0.25` 和 `0.3:1.0:0.3` 权重配置；当前 300 epoch checkpoint 已生成。
- [x] 新增 `tools/make_i7_fr4_r8_refined_nn_candidates.py`，以 legacy 最佳参数为中心生成对称 trust-region 候选；当前已生成 512 个 round8 pool 候选。
- [x] 新增 `tools/rank_interdigital_surrogate_candidates.py`，用预测 S 曲线、硬约束、匹配收益和参数距离排序候选；当前已输出 round8 top8 plan。
- [x] round8 使用 `1-10 GHz` ADS/RFPro 仿真，并生成 `filter_features.csv` 与 SVG S 曲线。
- [x] 数据集构建加入源频点数和 6-8 GHz 步进质量控制；当前重建后为 62 个样本。
- [x] round9 以 ADS 实测最佳平衡点 `i7_fr4_r8_nn0447` 为中心，释放 `S1S6_delta/S2S5_delta/S3S4_delta` 做小范围非对称微调。
- [x] round9 试跑 `Linear 401` 两颗候选，平均 `7.14 min/candidate`，top8 估算约 `57 min`，时间成本偏高。
- [x] round9 常规闭环下调为 `Linear 201` 点；401 点只用于候选复核/出图，最终 1-2 个候选再使用 `Linear 1001`。
- [x] 新建 `SIMADS_EM_PAR` 模板 workspace，模板 cell 使用通用名 `SIMADS_EM_TEMPLATE_2PORT_FEM`，当前专用层叠命名为 `FR4_210UM`。
- [x] 修复新 workspace 的 `lib.defs` 无 BOM 写入、library 注册、`FR4_210UM.subst` 和 `materials.matdb` 复制。
- [x] emSetup 克隆逻辑改为优先使用 profile substrate，避免旧候选 params 中的 `substrate4` 覆盖标准层叠命名。
- [x] 2 worker `--skip-fem` 并发准备验证通过。
- [x] 在 `FR4_210UM` 层叠修复后重跑 2 worker `Linear 91` 真实 FEM；wall time `290.2 s`，吞吐约 `1.4x`。
- [x] round9 top8 ADS/RFPro 仿真后，生成 `filter_features.csv`、SVG 曲线，并刷新 NN 数据集到 71 个有效样本。
- [x] 以 round9 实测平衡点 `i7_fr4_r9_asym0667` 为中心生成 round10 窄信赖域候选池 1024 个，并用 round9-parallel surrogate 选出 top8。
- [x] round10 快速闭环频点改为 `Linear 46, 1-10 GHz`，200 MHz 间隔，包含 `5/6/7/8/9 GHz`。
- [x] round10 top8 使用 `workers=2` 在 `SIMADS_EM_PAR` / `FR4_210UM` 模板工程中并发 ADS/RFPro 仿真，生成 `filter_features.csv` 和 SVG；wall time 约 `495 s`。
- [x] round11b 以 `i7_fr4_r10_asym0555` 为中心生成 4096 个 5 GHz 带阻偏置候选，选 top8 并用 `Linear 46, 1-10 GHz` 并发仿真；wall time 约 `485 s`，平均 `115 s/candidate`。
- [x] round11b 生成 `filter_features.csv` 和 SVG；最佳 5 GHz 带阻为 `i7_fr4_r11b_asym1855`，`S21@5=-26.68 dB`，更均衡候选为 `i7_fr4_r11b_asym3016`，`S21@5=-25.91 dB`、`S21@8=-2.82 dB`、ripple `3.30 dB`。
- [x] 回填 round11b 数据：全量训练集 `interdigital_refined_nn_dataset_round11b_parallel_full.npz` 为 87 个样本，高质量 40+ 点训练集为 27 个样本。
- [x] 训练 round11b surrogate：`interdigital_refined_surrogate_round11b_parallel_full_h64b2_s1130.pt`，仍使用 `S11:S21:S22 = 0.30:1.0:0.30`。
- [x] 下一轮常规闭环改为 `4-10 GHz, Linear 40`，保留 5/6/8/9 GHz 插值评分；若需要关键整数 GHz 精确落点，再切换为 `Linear 41`。
- [x] round12 以 `i7_fr4_r11b_asym3016` 为中心生成 4096 个候选，使用 `S21@5 <= -26 dB` 保护约束选 top8，并完成 `workers=2` 并发仿真。
- [x] round12 生成 `filter_features.csv` 和 SVG；wall time 约 `485 s`，平均 `105.7 s/candidate`。
- [x] round12 回填训练集：全量 95 个样本，高质量 40+ 点 35 个样本。
- [x] 训练 round12 全量增强回损权重模型：`interdigital_refined_surrogate_round12_parallel_full_h64b2_s1150.pt`，`S11:S21:S22 = 0.50:1.0:0.50`。
- [x] 按 Marki 原始理论尺寸生成 `i7_fr4_theory_marki_20260802` 理论锚点，完成 `4-10 GHz, Linear 40` ADS/RFPro 仿真，输出 `filter_features.csv`、SVG 曲线和理论 S2P 对比图。
- [ ] 下一轮排序对回损使用保守校正，优先寻找预测 `worst(S11,S22) <= -7 dB` 且 `S21@5 <= -26 dB` 的候选；不要只按未校正神经网络总分取 top8。







