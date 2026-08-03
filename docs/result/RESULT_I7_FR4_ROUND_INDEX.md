# FR4 7 阶交指滤波器 Round 结果索引

Status: Active
Domain: RESULT
Canonical: `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`
Related: `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`, `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-03
Owner: ADS Automation

本文档索引 FR4 7 阶交指带通滤波器 `round2` 到 `round7` 的 plan、result、summary、代表候选和结论，并记录 `round13` 当前 ADS 并发模板下的 baseline 单候选复跑结果。用途是让后续优化、报告和 baseline 比较只引用一个统一入口，避免把材料、阶数、拓扑或历史试跑结果混在一起。

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
| round13 | 3 | 1 | Current home parallel retest | `i7_fr4_r13_retest_base_l555_taper` | 单独复跑 legacy baseline 参数；S21 硬约束仍通过，但当前模板回损约 -4.2 dB，状态为 TUNE。 |

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
| `i7_fr4_r13_retest_base_l555_taper` | round13 | -26.98 | -2.51 | -4.60 | -4.60 | 3.07 | -4.26 | -4.20 | 当前 home parallel / 4-10 GHz Linear40 复跑；S21 硬通过但回损明显弱于 frozen baseline 记录。 |

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
| round13 | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round13_retest_4to10_40.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round13_retest_4to10_40/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round13_retest_4to10_40/sweep_summary.csv` |

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

## 7. Current Template Retest

2026-08-02 在家里电脑 `home_simads_em_parallel` profile 下，使用新建 ADS 并发模板 `SIMADS_EM_TEMPLATE_2PORT_FEM`，对 legacy baseline 参数单独复跑一次：

```text
Sweep: interdigital_7o_fr4_round13_retest_4to10_40
Candidate: i7_fr4_r13_retest_base_l555_taper
Equivalent legacy params: i7_fr4_r1_l555_taper / i7_fr4_r3_base
Frequency: 4-10 GHz Linear40
Elapsed: 106.6 s
Status: TUNE
S21@5/6/7/8/9 GHz: -26.98 / -2.51 / -3.06 / -4.60 / -55.59 dB
Passband min/ripple: -4.60 dB / 3.07 dB
Worst S11/S22: -4.26 / -4.20 dB
```

复跑结论：同一组几何参数在当前并发模板下仍保持 5 GHz 阻带与 6/8 GHz 通带硬约束，但回损比 frozen baseline 记录退化约 1.3-1.8 dB。后续比较 NN 候选前，应优先在同一 `round13` 口径下复跑 `i7_fr4_r10_asym0555` 和 `i7_fr4_r11b_asym3016`，确认这是模板/端口/层叠漂移还是候选本身差异。

## 8. HFSS 裁决记录

2026-08-02 在 HFSS 3D Layout 中复核同一 `i7_fr4_r13_retest_base_l555_taper` 版图：

```text
Project: D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss_aedt_edge_port_gnd_airbox.aedt
Result: projects/bfp_6_8g_i7_fr4/results/hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd/
Port: AEDT native edge port, Gap/Vertical, is_circuit=False
GND: x=-3.54..7.0502 mm, y=-1.5..7.5323 mm, left/right edges aligned to P1/P2 port cross sections
Frequency: 4-10 GHz Linear40
Elapsed: HFSS solve about 1m43s, full script 136.1s
Status: TUNE
S21@5/6/7/8/9 GHz: -20.38 / -4.81 / -5.08 / -9.64 / -27.44 dB
Passband min/ripple: -9.64 dB / 5.78 dB
Worst S11/S22: -6.78 / -6.90 dB
SVG: projects/bfp_6_8g_i7_fr4/results/hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd/svg/i7_fr4_r13_retest_base_l555_taper_hfss_s_curves.svg
```

HFSS 结论：修正 GND 范围后，回损指标比 ADS round13 当前模板更好，但 S21 通带高端明显变差，8 GHz 只有约 `-9.64 dB`。5 GHz 抑制约 `-20.38 dB`，低于 ADS round13 的 `-26.98 dB`。这说明后续优化不能只看 ADS/RFPro 的单一模板结果，至少需要在端口/GND 口径固定后继续做 HFSS 抽检。

pyEDB `edge-gap` 端口排查记录：显式把 reference point 放在 GND 边界且与端口同轴后，AEDT 重新打开求解仍报 `solution data is not available`，不作为后续自动仿真主路线。当前可执行主路线为 `aedt-edge + --gnd-boundary-mode port-edges`。

2026-08-02 继续用配置化真实层叠 `JLC04161H_7628_1P6MM` 和 `--route reliable` 重跑同一候选，验证重构后的 HFSS 模块化链路：

```text
Route: hfss3dlayout_aedt_edge_gap_gnd_port_edges
Project: D:\Work\ADS\SIMADS_EM_PAR\HFSS_RELIABLE_SMOKE\i7_fr4_r13_retest_base_l555_taper_jlc_hfss_reliable_4to10_40.aedt
Result: projects/bfp_6_8g_i7_fr4/results/hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40/
Run manifest: projects/bfp_6_8g_i7_fr4/runs/hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40/run_manifest.json
Stackup: ETCH_TOP signal, ETCH_INNER1 reference ground, 0.2104 mm signal-to-reference height
Frequency: 4-10 GHz Linear40, spacing 153.846 MHz
Elapsed: full script 129.349 s, AEDT solve about 1m46s
Status: TUNE
S21@5/6/7/8/9 GHz: -21.67 / -3.24 / -4.04 / -5.52 / -33.34 dB
Passband min/ripple: -5.52 dB / 2.27 dB
Worst S11/S22: -6.92 / -6.88 dB
SVG: projects/bfp_6_8g_i7_fr4/results/hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40/svg/i7_fr4_r13_retest_base_l555_taper_hfss_s_curves.svg
```

与 ADS round13 当前模板结果对比：

```text
ADS source: projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round13_retest_4to10_40/i7_fr4_r13_retest_base_l555_taper_mm_coords_rfpro.csv
HFSS source: projects/bfp_6_8g_i7_fr4/results/hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40/i7_fr4_r13_retest_base_l555_taper_hfss_trace.csv
Compare SVG: projects/bfp_6_8g_i7_fr4/results/compare_ads_hfss_i7_fr4_r13_reliable_jlc/i7_fr4_r13_base_ads_vs_hfss.svg
Compare summary: projects/bfp_6_8g_i7_fr4/results/compare_ads_hfss_i7_fr4_r13_reliable_jlc/i7_fr4_r13_base_ads_vs_hfss_summary.csv
S21 mean abs delta: 6.21 dB overall, 1.21 dB in 6-8 GHz
S21 delta at 5/6/7/8/9 GHz: +5.06 / -0.74 / -1.35 / -0.92 / +19.79 dB
S11/S22 passband mean abs delta: 4.38 / 3.82 dB
```

JLC 层叠 HFSS 结论：重构后的 HFSS build/solve/export/manifest 链路已经能真实跑通，并且相比旧简化层叠 HFSS 结果，6-8 GHz 的 S21 更接近 ADS；但 5 GHz 抑制仍弱于 ADS 约 5 dB，9 GHz 处差异很大。后续若用 HFSS 做裁决，应固定该 `JLC04161H_7628_1P6MM + reliable route` 为当前自动化主口径，并继续增加端口属性读回和 ADS 层叠对齐检查。

2026-08-03 同一候选已通过标准 backend sweep 入口真实求解，不再走 verdict-only 手工命令：

```text
Command entry: tools/run_ads_filter_sweep.py --backend hfss
Pipeline: bfp_6_8g_i7_fr4_home_parallel_round13_retest_4to10_40
HFSS profile: home
Project: D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss.aedt
Result: projects/bfp_6_8g_i7_fr4/results/hfss_round13_standard_backend_solve/
Run: bfp_6_8g_i7_fr4_round13_i7_fr4_r13_retest_base_l555_taper_home_20260803_224339
Backend summary: projects/bfp_6_8g_i7_fr4/results/hfss_round13_standard_backend_solve/backend_summary.csv
Status/stage: completed/scored
Elapsed: 176.178 s
S21@5/6/7/8/9 GHz: -21.67 / -3.24 / -4.04 / -5.52 / -33.34 dB
Passband min/ripple: -5.52 dB / 2.27 dB
Worst S11/S22: -6.92 / -6.88 dB
```

标准 backend 与 ADS smoke 对比：

```text
Compare: projects/bfp_6_8g_i7_fr4/results/compare_ads_hfss_round13_standard_backend/
Compare SVG: projects/bfp_6_8g_i7_fr4/results/compare_ads_hfss_round13_standard_backend/i7_fr4_r13_base_ads_smoke_vs_hfss_standard.svg
Compare summary: projects/bfp_6_8g_i7_fr4/results/compare_ads_hfss_round13_standard_backend/i7_fr4_r13_base_ads_smoke_vs_hfss_standard_summary.csv
S21 mean abs delta: 6.21 dB overall, 1.21 dB in 6-8 GHz
S21 delta at 5/6/7/8/9 GHz: +5.06 / -0.74 / -1.35 / -0.92 / +19.79 dB
S11/S22 passband mean abs delta: 4.38 / 3.82 dB
```

2026-08-03 标准 HFSS backend 已完成 round13 三个候选的真实 solve，并生成统一 ranking：

```text
Backend summary: projects/bfp_6_8g_i7_fr4/results/hfss_round13_standard_backend_solve/backend_summary.csv
HFSS ranking: projects/bfp_6_8g_i7_fr4/results/hfss_round13_standard_backend_solve/hfss_score_ranking.csv
All runs: completed/scored
```

| HFSS Rank | Candidate | Status | S21@5G | S21@6G | S21@8G | Passband Min | Ripple | Worst S11 | Worst S22 | 结论 |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `i7_fr4_r13_retest_r11b_asym3016` | TUNE | -23.48 | -3.36 | -4.92 | -4.92 | 1.62 | -5.74 | -5.89 | 通带 S21 最好，但 5GHz 阻带和回损未达目标。 |
| 2 | `i7_fr4_r13_retest_r10_asym0555` | TUNE | -22.87 | -3.29 | -5.35 | -5.35 | 2.08 | -6.09 | -6.12 | 回损刚过 -6dB，但 5GHz 阻带和 8GHz 通带未达目标。 |
| 3 | `i7_fr4_r13_retest_base_l555_taper` | TUNE | -21.67 | -3.24 | -5.52 | -5.52 | 2.27 | -6.92 | -6.88 | 回损最好，但 5GHz 阻带和 8GHz 通带最弱。 |

标准 backend 结论：HFSS 已经并入正常 pipeline/sweep/run manifest/backend summary 架构。HFSS 口径下 3 个 round13 候选均不是 release candidate，主要问题是 5GHz 抑制不足；r11b 是下一步最值得保留的通带形状参考，r10 是回损与通带折中点。当前 round13 ADS/RFPro 只完成 base，同口径缺 r10/r11b，因此不能直接用旧 round10/round11b ADS 结果替代正式 compare；下一步需要按当前 round13 pipeline 补跑 r10/r11b 的 ADS/RFPro。

## 9. ADS Flow Smoke

2026-08-02 在家里电脑 `home_simads_em_parallel` profile 下，使用独立 smoke cell 重新试跑 ADS 候选流程：

```text
Run: ads_smoke_i7_fr4_r13_base_4to10_40
Candidate: i7_fr4_r13_retest_base_l555_taper
Target cell: i7_fr4_r13_retest_base_l555_taper_ads_smoke_mm_coords
Result: projects/bfp_6_8g_i7_fr4/results/ads_smoke_i7_fr4_r13_base_4to10_40/
Run manifest: projects/bfp_6_8g_i7_fr4/runs/ads_smoke_i7_fr4_r13_base_4to10_40/run_manifest.json
Frequency: 4-10 GHz Linear40
Elapsed: full flow 113.434 s, score elapsed 113.259 s
Status: TUNE
S21@5/6/7/8/9 GHz: -26.98 / -2.51 / -3.06 / -4.60 / -55.59 dB
Passband min/ripple: -4.60 dB / 3.07 dB
Worst S11/S22: -4.26 / -4.20 dB
SVG: projects/bfp_6_8g_i7_fr4/results/ads_smoke_i7_fr4_r13_base_4to10_40/svg/i7_fr4_r13_retest_base_l555_taper_ads_smoke_s_curves.svg
```

本次 ADS 链路完成 DXF 导入、端口添加、emSetup 模板克隆、RFPro FEM、S 参数导出、评分和 SVG 生成。首次尝试暴露出一个工程约束：当前 ADS DXF import 路线要求 DXF 文件 stem 与 `--cell` 一致；为了不覆盖 round13 原始 cell，本次把 DXF 复制为 `.tmp/ads_smoke_inputs/i7_fr4_r13_retest_base_l555_taper_ads_smoke_mm_coords.dxf` 后再导入到 smoke cell。

与 HFSS JLC reliable smoke 对比：

```text
Compare: projects/bfp_6_8g_i7_fr4/results/compare_ads_smoke_hfss_i7_fr4_r13_jlc/
Compare SVG: projects/bfp_6_8g_i7_fr4/results/compare_ads_smoke_hfss_i7_fr4_r13_jlc/i7_fr4_r13_base_ads_smoke_vs_hfss.svg
Verdict summary: projects/bfp_6_8g_i7_fr4/results/compare_ads_smoke_hfss_i7_fr4_r13_jlc/i7_fr4_r13_base_ads_smoke_hfss_verdict_summary.json
Verdict: needs_tuning
S21 mean abs delta: 6.21 dB overall, 1.21 dB in 6-8 GHz
S21 delta at 5/6/7/8/9 GHz: +5.06 / -0.74 / -1.35 / -0.92 / +19.79 dB
S11/S22 passband mean abs delta: 4.38 / 3.82 dB
```

ADS smoke 结论：ADS 自动化流程已能在新 workspace/profile 中完整跑通，速度与 HFSS reliable 路线同量级，约 2 分钟以内。当前结果仍是 `TUNE`，通带 S21 可用但回损偏弱；同时 manifest 显示 ADS 实际 substrate 仍为 `SIMADS_EM_PAR_lib:FR4_210UM`，而 stackup config 记录为 `JLC04161H_7628_1P6MM`。因此 ADS/HFSS 的物理层叠还不能视为完全一致，下一步需要把 ADS substrate 生成或模板 substrate patch 到配置化 JLC 层叠。

### 9.1 ADS Layout GND Prepare

2026-08-02 对 ADS 版图生成链路做一次几何完善验证，仍以 `i7_fr4_r13_retest_base_l555_taper` 参数为基点，但使用 JLC 配置层名和显式参考地铜皮：

```text
Layout dir: projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_jlc04161h_7628_1p6mm_ads_layout_gnd/
Layout id: i7_fr4_r13_retest_base_l555_taper_ads_gnd_jlc04161h_7628_1p6mm
Top metal layer: ETCH_TOP
Via layer: DRILL_TOP_BOTTOM
Reference ground layer: ETCH_INNER1
GND plane: hfss_ground_plane, x=-3.54..7.0502 mm, y=-1.5..7.5323 mm
GND mode: port-edges
ADS prepare run: ads_layout_gnd_prepare_i7_fr4_r13
ADS cell: SIMADS_EM_PAR_lib:i7_fr4_r13_retest_base_l555_taper_ads_gnd_jlc04161h_7628_1p6mm_mm_coords
```

本次只验证 ADS DXF 导入和 emSetup 克隆，不包含 FEM 求解。DXF fallback import 成功导入 `30` 个实体：`ETCH_TOP=18`、`DRILL_TOP_BOTTOM=7`、`ETCH_INNER1=1`、`EM_BOUNDARY=4`；其中 `ETCH_INNER1` 的唯一 solid 为显式参考地铜皮。该口径比旧 `cond/pcvia1` 版图更接近真实 JLC 层叠，但仍需要后续把 ADS template substrate 本体也切换/生成到 `JLC04161H_7628_1P6MM`，否则 RFPro 求解仍可能使用旧 substrate。

2026-08-02 进一步按真实四层板口径修正 ADS 版图 GND 网络：`L2/L3/L4` 全部赋予 `GND`。层叠配置新增 `geometry.ground_layers = [ETCH_INNER1, ETCH_INNER2, ETCH_BOTTOM]`；版图生成器在 `--include-ground-plane` 时输出三张有限地铜；ADS fallback importer 强制把这些 SOLID 转为 `PlaneInfo.net_name = GND` 的 ADS Plane。

```text
Layout dir: projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_jlc04161h_7628_1p6mm_ads_layout_gnd_l234/
Layout id: i7_fr4_r13_retest_base_l555_taper_ads_gnd_l234_jlc04161h_7628_1p6mm
ADS cell: SIMADS_EM_PAR_lib:i7_fr4_r13_retest_base_l555_taper_ads_gnd_l234_jlc04161h_7628_1p6mm_mm_coords
DXF solids: ETCH_INNER1=1, ETCH_INNER2=1, ETCH_BOTTOM=1, ETCH_TOP=11
ADS import: generated_dxf_subset, solid=14, via=7, plane=3
ADS readback: <LayerId 1001>/GND, <LayerId 1002>/GND, <LayerId 1003>/GND
```

注意：ADS `add_net_connection_label` 不能直接贴到普通图形或 via 上，脚本日志会保留该 fallback 失败信息；本轮有效路径是 ADS `Plane` 自身的 `net_name=GND`。下一步若要让 via 也在 ADS netlist 层面显式归属 GND，需要继续研究 PCBVia/InstTerm 的绑定方式，或者在地过孔处生成可绑定的 GND pin/term。

2026-08-02 自动流程补齐：`tools/run_ads_filter_candidate.py`、`tools/run_ads_filter_sweep.py`、`tools/run_ads_filter_sweep_parallel.py` 均接入 `--force-generated-dxf-subset`；`bfp_6_8g_i7_fr4_home_parallel_round13_retest_4to10_40` 和 `bfp_6_8g_i7_fr4_home_parallel_theory_marki_4to10_40` pipeline 已显式设置 `ads.force_generated_dxf_subset=true`。后续 round13/theory ADS 批量导入应默认生成 L2/L3/L4 三张 `GND` Plane。

## 10. 后续建议

- round8 不建议继续扩大 surrogate 搜索半径，应回到 baseline 附近做回损导向的小信赖域搜索。
- 下一轮 hard filter 必须先保留 5 GHz 阻带和 8 GHz 通带余量，再优化 `worst_s11_6_8_db` / `worst_s22_6_8_db`。
- 每个新 round 必须在本文件追加 plan、result、summary、代表候选、失败点和结论。
- 若新候选仅改善 5 GHz 抑制但回损明显退化，不应作为 release candidate。
