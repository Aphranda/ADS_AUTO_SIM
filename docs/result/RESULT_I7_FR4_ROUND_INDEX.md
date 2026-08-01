# FR4 7 阶交指滤波器 Round 结果索引

Status: Active
Domain: RESULT
Canonical: `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`
Related: `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`, `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档索引 FR4 7 阶交指带通滤波器 `round2` 到 `round7` 的 plan、result、summary、代表候选和结论。用途是让后续优化、报告和 baseline 比较只引用一个统一入口，避免把材料、阶数、拓扑或历史试跑结果混在一起。

## 1. 当前结论

| 项目 | 结论 |
|---|---|
| 当前 frozen baseline | `i7_fr4_baseline_freeze_20260801` |
| 代表候选 | `i7_fr4_r3_base` |
| 代表 cell | `i7_fr4_r3_base_mm_coords` |
| Target profile | `fr4_25db_rl6` |
| Score version | `fr4_i7_score_v1` |
| 发布状态 | 未形成优于 baseline 的 release candidate |

当前冻结 baseline 满足 S21 硬约束，但 `worst_s11_6_8_db=-5.55 dB`、`worst_s22_6_8_db=-5.98 dB`，仍未完全达到 -6 dB 回损目标。后续候选必须在保持 5 GHz 阻带和 6/8 GHz 通带硬约束的前提下改善回损，才可宣称优于 baseline。

## 2. 结果口径

硬约束判断使用以下口径：

```text
S21@5GHz <= -25 dB
S21@6GHz >= -5 dB
S21@8GHz >= -5 dB
passband_min_s21 >= -5 dB
passband_ripple <= 4 dB
```

回损目标使用：

```text
worst_s11_6_8_db <= -6 dB
worst_s22_6_8_db <= -6 dB
```

旧 score 文件可能没有 run metadata 或 margin 字段；本索引用原始指标统一判断，不依赖旧字段版本。

## 3. Round 总览

| Round | Plan | 已评分 | 状态 | 代表硬约束候选 | 结论 |
|---|---:|---:|---|---|---|
| round2 | 14 | 9 | Legacy scored | `i7_fr4_r2_base` | 初始可行点重复，baseline 仍最好；其他扰动多牺牲 5 GHz 阻带或回损。 |
| round3 | 12 | 12 | Legacy scored | `i7_fr4_r3_base` | baseline 重复并冻结来源之一；局部 feed/taper/overlap 未形成更优 release 点。 |
| round4 | 10 | 10 | Legacy scored | `i7_fr4_r4_base` | gap/taper 局部搜索未改善综合可发布性。 |
| round5 | 12 | 12 | Legacy scored | `i7_fr4_r5_base` | W0/feed length 搜索未优于 baseline，部分候选虽硬通过但回损退化。 |
| round6 | 17 | 5 | Partial legacy scored | `i7_fr4_r6_base` | 局部收敛搜索只完成部分候选，未形成优于 baseline 的点。 |
| round7 | 8 | 4 | Partial company scored | `i7_fr4_r7_bo04` | surrogate 候选探索数据；`bo04` 保持 S21 硬约束但回损明显差于 baseline，不作为 release。 |

## 4. 关键候选指标

| Candidate | Round | S21@5G | S21@6G | S21@8G | Passband Min | Ripple | Worst S11 | Worst S22 | 判断 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `i7_fr4_r3_base` | round3 | -27.15 | -2.13 | -4.28 | -4.28 | 2.83 | -5.55 | -5.98 | Frozen baseline。 |
| `i7_fr4_r3_t195_tw022` | round3 | -25.93 | -2.72 | -4.30 | -4.30 | 2.88 | -5.06 | -5.50 | S21 硬通过，但回损差于 baseline。 |
| `i7_fr4_r4_tw020_s6m` | round4 | -25.91 | -2.78 | -4.70 | -4.70 | 3.18 | -4.64 | -4.62 | S21 硬通过，但回损明显退化。 |
| `i7_fr4_r5_w0345_len400` | round5 | -25.66 | -1.95 | -4.78 | -4.78 | 3.30 | -4.50 | -4.60 | S21 硬通过，但通带高边和回损余量不足。 |
| `i7_fr4_r6_base_tw0190` | round6 | -25.27 | -2.85 | -4.89 | -4.89 | 3.33 | -4.40 | -4.52 | 接近高边通带约束，回损退化。 |
| `i7_fr4_r7_bo04` | round7 | -28.03 | -3.01 | -4.64 | -4.64 | 3.00 | -4.33 | -4.56 | 5 GHz 阻带改善，但回损差于 baseline；探索数据。 |
| `i7_fr4_r7_bo05` | round7 | -24.65 | -2.84 | -4.03 | -4.17 | 2.43 | -3.73 | -3.94 | 5 GHz 阻带未达 25 dB，不可作为候选。 |

单位：dB。

## 5. 资产索引

| Round | Plan | Result Dir | Summary |
|---|---|---|---|
| round2 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round2.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round2/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round2/sweep_summary.csv` |
| round3 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round3.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round3/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round3/sweep_summary.csv` |
| round4 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round4.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round4/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round4/sweep_summary.csv` |
| round5 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round5.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round5/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round5/sweep_summary.csv` |
| round6 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round6.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round6/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round6/sweep_summary.csv` |
| round7 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round7.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round7/` | `sweep_summary.csv`、`sweep_summary_bo05.csv`、`sweep_summary_bo01_bo03.csv` |

## 6. Baseline 关系

| Baseline Candidate | 来源 | 说明 |
|---|---|---|
| `i7_fr4_r3_base` | round3 | 冻结代表候选。 |
| `i7_fr4_r4_base` | round4 | baseline 重复点，指标与代表候选一致。 |
| `i7_fr4_r5_base` | round5 | baseline 重复点，指标与代表候选一致。 |
| `i7_fr4_r6_base` | round6 | baseline 重复点，指标与代表候选一致。 |

baseline 冻结记录：

```text
projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md
projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json
```

公司环境复跑记录：

```text
projects/bfp_6_8g_i7_fr4/results/baselines/company_rerun_20260801/
```

公司环境复跑指标与 frozen baseline 一致，可作为后续公司电脑环境比较的漂移检查参考。

## 7. 后续建议

- round8 不建议继续扩大 surrogate 搜索半径，应回到 baseline 附近做回损导向的小信赖域搜索。
- 下一轮 hard filter 必须先保留 5 GHz 阻带和 8 GHz 通带余量，再优化 `worst_s11_6_8_db` / `worst_s22_6_8_db`。
- 每个新 round 必须在本文件追加 plan、result、summary、代表候选、失败点和结论。
- 若新候选仅改善 5 GHz 抑制但回损明显退化，不应作为 release candidate。

