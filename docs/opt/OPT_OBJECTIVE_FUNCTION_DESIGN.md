# ADS 自动仿真目标函数与 Target Profile 设计

Status: Active
Domain: OPT
Canonical: `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`
Related: `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`, `config/targets/fr4_25db_rl6.json`, `tools/analyze_ads_dataset.py`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真框架的 target profile、硬约束、软目标、评分版本和发布判据。目标是把评分逻辑从滤波器脚本中的隐含规则升级为可配置、可追溯、可扩展到多器件的 objective contract。

## 1. 当前结论

当前 FR4 7 阶交指滤波器使用：

```text
target_profile_id = fr4_25db_rl6
score_version = fr4_i7_score_v1
device_type = filter.interdigital
```

目标配置文件：

```text
config/targets/fr4_25db_rl6.json
```

当前评分实现：

```text
tools/analyze_ads_dataset.py
```

注意：当前脚本内仍保留 `TARGET_PROFILES` 硬编码字典，P2 阶段应迁移到 `src/simads.scoring`，并优先读取 `config/targets/<target_profile_id>.json`。

## 2. Target Profile Schema

Target profile 必须至少包含：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `schema_version` | string | - | target profile schema 版本。 |
| `target_profile_id` | string | - | 目标 profile ID。 |
| `name` | string | - | 可读名称。 |
| `score_version` | string | - | 评分函数版本。 |
| `frequency_ghz` | object | GHz | 关键采样点和频段定义。 |
| `hard_constraints` | object | dB | 必须满足的硬约束。 |
| `return_loss_targets` | object | dB | 回波损耗目标。 |
| `soft_objectives` | object | mixed | 可选软目标、权重和排序策略。 |
| `release_gate` | object | mixed | 可发布候选判据。 |

当前 `fr4_25db_rl6` 已包含 `frequency_ghz`、`hard_constraints` 和 `return_loss_targets`；`soft_objectives` 与 `release_gate` 目前由本文档定义，后续可回填到 JSON。

## 3. 频率采样

当前 FR4 7 阶交指滤波器采样口径：

| 名称 | 频点 / 频段 | 用途 |
|---|---:|---|
| `stop_low_probe` | 5.0 GHz | 低边 5G 阻带抑制。 |
| `passband_start` | 6.0 GHz | 通带低边入口。 |
| `passband_center` | 7.0 GHz | 通带中心参考点。 |
| `passband_stop` | 8.0 GHz | 通带高边出口。 |
| `stop_high_probe` | 9.0 GHz | 高边阻带参考点。 |
| `passband` | 6.0-8.0 GHz | 计算通带最差 S21、纹波、最差 S11/S22。 |

当前 `analyze_ads_dataset.py` 对 5/6/7/8/9 GHz 使用线性插值；对 6-8 GHz 通带使用采样点集合计算最差值。

## 4. 硬约束

`fr4_25db_rl6` 硬约束：

| 指标 | 判据 | 说明 |
|---|---:|---|
| `s21_5g_db` | `<= -25.0 dB` | 5 GHz 低边阻带至少 25 dB。 |
| `s21_6g_db` | `>= -5.0 dB` | 6 GHz 通带入口插损不差于 5 dB。 |
| `s21_8g_db` | `>= -5.0 dB` | 8 GHz 通带出口插损不差于 5 dB。 |
| `passband_min_s21_db` | `>= -5.0 dB` | 6-8 GHz 最差 S21 不差于 5 dB。 |
| `passband_ripple_db` | `<= 4.0 dB` | 6-8 GHz 通带纹波不超过 4 dB。 |

硬约束是发布前置条件。任何候选未满足硬约束，即使某个局部指标改善，也不得作为 release candidate。

## 5. 回损目标

`fr4_25db_rl6` 回损目标：

| 指标 | 判据 | 说明 |
|---|---:|---|
| `worst_s11_6_8_db` | `<= -6.0 dB` | 6-8 GHz 最差输入回损不高于 -6 dB。 |
| `worst_s22_6_8_db` | `<= -6.0 dB` | 6-8 GHz 最差输出回损不高于 -6 dB。 |

当前 frozen baseline 的 S21 硬约束满足，但回损略未达标：`worst_s11_6_8_db=-5.55 dB`、`worst_s22_6_8_db=-5.98 dB`。因此后续优化的主方向不是继续单纯加深 5 GHz 抑制，而是在保留硬约束的前提下改善 S11/S22。

## 6. Margin 定义

评分输出应包含以下 margin 字段，数值越大越好，`>= 0` 表示满足对应约束：

| 字段 | 公式 |
|---|---|
| `margin_s21_5g_db` | `s21_5g_db_max - s21_5g_db` |
| `margin_s21_6g_db` | `s21_6g_db - s21_6g_db_min` |
| `margin_s21_8g_db` | `s21_8g_db - s21_8g_db_min` |
| `margin_passband_min_s21_db` | `passband_min_s21_db - passband_min_s21_db_min` |
| `margin_passband_ripple_db` | `passband_ripple_db_max - passband_ripple_db` |
| `margin_worst_s11_6_8_db` | `worst_s11_6_8_db_max - worst_s11_6_8_db` |
| `margin_worst_s22_6_8_db` | `worst_s22_6_8_db_max - worst_s22_6_8_db` |

注意：S 参数均为 dB。对阻带 S21 和回损指标，数值更负通常更好，因此 margin 使用目标上限减实际值。

## 7. Status 判定

当前 `analyze_ads_dataset.py` 使用：

| Status | 含义 |
|---|---|
| `PASS_CANDIDATE` | S21 硬约束和回损目标全部满足。 |
| `TUNE` | 至少一个硬约束或回损目标未满足。 |

建议后续扩展为：

| Status | 含义 |
|---|---|
| `RELEASE_CANDIDATE` | 满足硬约束、回损目标、baseline 改善和制造 gate。 |
| `PASS_CANDIDATE` | 满足 target profile 指标，但尚未完成 baseline/制造/报告 gate。 |
| `TUNE` | 可继续优化。 |
| `REJECTED` | 违反硬约束或制造约束，默认不进入下一轮局部优化。 |
| `FAILED` | 仿真或评分失败。 |

## 8. 软目标与排序

当前 round 结果显示，仅按代理模型或局部单指标优化会出现“5 GHz 抑制改善但回损退化”的候选。后续排序应采用两级逻辑：

1. 先执行 hard filter：所有 S21 硬约束必须满足。
2. 再执行 soft ranking：优先改善回损，再考虑 5 GHz 阻带、纹波和通带余量。

推荐 soft objective：

| 目标 | 方向 | 建议权重 | 说明 |
|---|---|---:|---|
| `worst_s11_6_8_db` | 越负越好 | 0.35 | 当前主要短板。 |
| `worst_s22_6_8_db` | 越负越好 | 0.35 | 当前主要短板。 |
| `margin_s21_5g_db` | 越大越好 | 0.10 | 需要保留 5 GHz 阻带余量。 |
| `margin_s21_8g_db` | 越大越好 | 0.10 | 防止高边通带被收窄。 |
| `margin_passband_ripple_db` | 越大越好 | 0.05 | 控制通带平坦度。 |
| `margin_passband_min_s21_db` | 越大越好 | 0.05 | 控制通带最差插损。 |

排序不能让软目标抵消硬约束失败；硬约束失败的候选只可作为训练负样本。

## 9. Baseline 改善判据

候选宣称优于 baseline 至少需要满足：

| 判据 | 要求 |
|---|---|
| S21 硬约束 | 全部满足。 |
| 回损目标 | `worst_s11_6_8_db <= -6 dB` 且 `worst_s22_6_8_db <= -6 dB`，或明确标记为 tune candidate。 |
| Baseline drift | 若 profile/substrate/emSetup 变更，先复跑 baseline 且在 drift tolerance 内。 |
| 关键指标退化 | 不得牺牲 5 GHz 阻带和 8 GHz 通带余量来换取局部改善。 |
| 制造 gate | 满足线宽、间距、孔径、焊盘、层叠和板厂能力。 |

当前 frozen baseline 仍是 release reference；round7 的 `i7_fr4_r7_bo04` 只能作为探索样本，不能作为 release candidate。

## 10. 多器件扩展规则

通用框架不得把 `s21_5g_db`、`worst_s11_6_8_db` 这类滤波器专用字段写死在核心模块。推荐拆分：

| 层 | 责任 |
|---|---|
| `simads.scoring` | 通用 score runner、target profile 加载、margin 计算、状态判定。 |
| `simads.devices.<device>` | 定义器件专用 metrics、hard constraints、soft objectives 和 report sections。 |
| `config/targets/*.json` | 每个项目/器件的目标 profile 实例。 |
| `tools/analyze_ads_dataset.py` | 兼容 CLI，逐步变成薄入口。 |

不同器件示例：

| 器件 | 典型硬约束 |
|---|---|
| 带通滤波器 | S21 通带、阻带抑制、S11/S22、纹波。 |
| 耦合器 | 耦合度、隔离度、直通损耗、相位平衡。 |
| 功分器 | 插损、隔离、幅相一致性、端口匹配。 |
| 天线 | S11、增益、效率、方向图、带宽。 |

## 11. P2 代码迁移建议

后续应将 `tools/analyze_ads_dataset.py` 中的硬编码内容迁移为：

```text
src/simads/scoring/
  target_profile.py
  sparams.py
  margins.py
  status.py
  objective.py
```

迁移顺序：

1. 新增 target profile loader，优先读取 `config/targets/<target_profile_id>.json`。
2. 抽出 S 参数插值和通带采样逻辑。
3. 抽出 margin 公式和 status 判定。
4. 保留 `tools/analyze_ads_dataset.py` CLI 兼容入口。
5. 为 `fr4_25db_rl6` 增加纯 Python unit test。

## 12. 当前执行规则

- 新 round 计划必须声明使用的 `target_profile_id` 和 `score_version`。
- 新 score CSV 必须写入 run metadata、target profile、score version 和 margin 字段。
- 新报告必须引用 target profile、baseline、score CSV 和 run manifest。
- 目标函数修改必须升级 `score_version`，并在 round index 中说明旧分数是否可比。

