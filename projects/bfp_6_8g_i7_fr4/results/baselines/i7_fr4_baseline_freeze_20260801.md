# FR4 7 阶交指滤波器 Baseline Freeze

Status: Frozen
Domain: RESULT
Canonical: `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`
Related: `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json`, `docs/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档冻结当前 FR4 7 阶交指带通滤波器 baseline。该 baseline 用于 round7 及后续候选的性能比较、环境漂移判断和报告引用。

## 1. 冻结对象

| 项目 | 内容 |
|---|---|
| Baseline ID | `i7_fr4_baseline_freeze_20260801` |
| 状态 | Frozen |
| 代表候选 | `i7_fr4_r3_base` |
| 重复候选 | `i7_fr4_r3_base` / `i7_fr4_r4_base` / `i7_fr4_r5_base` / `i7_fr4_r6_base` |
| 代表 Cell | `i7_fr4_r3_base_mm_coords` |
| Target profile | `fr4_25db_rl6` |
| Score version | `fr4_i7_score_v1` |
| Run ID | 历史结果，无 run manifest；以 candidate、layout hash、score hash 和重复指标冻结 |

## 2. 关键参数

| 参数 | 数值 |
|---|---:|
| `L_mm` | 5.55 |
| `tap_mm` | 1.95 |
| `Egap_mm` | 0.4823 |
| `S1/S6_mm` | 0.1176 |
| `S2/S5_mm` | 0.1750 |
| `S3/S4_mm` | 0.1857 |
| `W0_mm` | 0.3648 |
| `feed_len_mm` | 3.00 |
| `feed_taper_len_mm` | 0.60 |
| `feed_tip_w_mm` | 0.18 |
| `feed_overlap_mm` | 0.06 |
| `via_diameter_mm` | 0.254 |
| `via_pad_mm` | 0.3556 |

## 3. 冻结指标

| 指标 | 数值 | 判断 |
|---|---:|---|
| `S21@5GHz` | -27.15 dB | 满足 25 dB 低边阻带 |
| `S21@6GHz` | -2.13 dB | 满足通带入口 |
| `S21@7GHz` | -2.43 dB | 可接受 |
| `S21@8GHz` | -4.28 dB | 满足通带出口 |
| `S21@9GHz` | -58.64 dB | 高边抑制充足 |
| `passband_min_s21` | -4.28 dB | 满足硬约束 |
| `passband_ripple` | 2.83 dB | 满足硬约束 |
| `worst_s11_6_8` | -5.55 dB | 距 -6 dB 目标差 0.45 dB |
| `worst_s22_6_8` | -5.98 dB | 距 -6 dB 目标差 0.02 dB |

结论：该 baseline 满足 S21 硬约束，但未完全满足 `fr4_25db_rl6` 的回波损耗目标。后续候选若宣称优于 baseline，应至少保持 5 GHz 阻带和 6/8 GHz 通带硬约束，并优先改善 `worst_s11_6_8_db` 与 `worst_s22_6_8_db`。

## 4. 追溯文件

| 类型 | 路径 | SHA256 |
|---|---|---|
| Params | `projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_fr4_210um_round3/i7_fr4_r3_base_params.json` | `C3914D80DACB3D82F60EE52C9BEEE1A449BBAF0E9AABD9BDC14156547717307A` |
| DXF | `projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_fr4_210um_round3/i7_fr4_r3_base_mm_coords.dxf` | `350E154DC215D1DB201DDA489578D530EB6084BE3B2BC36DAD4C47ED21410A2E` |
| SVG | `projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_fr4_210um_round3/i7_fr4_r3_base.svg` | `BDCCCE0B468163EFCD29F433E5AD11CE3842A6D1A618CA2F978250D87EF84BF9` |
| Score | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round3/i7_fr4_r3_base_mm_coords_score.csv` | `36A5FFF5B76B41F96E15CED84A025E6712E091D010D198CA37BB33B3FABEE79F` |

## 5. 漂移容差

环境、ADS 版本、substrate 或 emSetup 发生变化后，应先复跑代表 baseline。若任一指标超过以下容差，则判定 baseline drift，需要先排查环境差异，再比较新候选。

| 指标 | 容差 |
|---|---:|
| `S21@5GHz` | ±1.0 dB |
| `S21@6GHz` | ±0.5 dB |
| `S21@8GHz` | ±0.5 dB |
| `passband_min_s21` | ±0.5 dB |
| `passband_ripple` | ±0.5 dB |
| `worst_s11_6_8` | ±0.5 dB |
| `worst_s22_6_8` | ±0.5 dB |

## 6. 使用规则

- 本文件冻结后只允许补勘误，不改结论。
- 新 profile、ADS 版本、substrate 或 emSetup 变更后，先复跑 baseline。
- 后续报告和优化结论引用 baseline 时，应引用 `baseline_id`。
- 若新候选仅在综合分上优于 baseline，但硬约束或回损目标退化，不得作为 release candidate。
