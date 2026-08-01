# ADS 资产迁移记录 2026-08-01

Status: Active
Domain: ARCH
Canonical: `docs/ARCH_ADS_ASSET_MIGRATION_20260801.md`
Related: `docs/ARCH_ADS_ASSET_MIGRATION_20260801.csv`, `docs/ADS版图自动仿真项目框架设计.md`, `docs/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

## 迁移结论

旧 `SIM/ADS` 目录的边界不符合新的 ADS 版图自动仿真框架。它同时承载了 plan、layout、result、reference report 和流程文档，导致项目资产、全局文档和可复用脚本混在一起。

本次迁移把 ADS 项目资产移动到：

```text
projects/bfp_6_8g_i7_fr4/
```

旧 `ADS/` 目录只保留 `README.md` 和空的历史占位目录，不再作为新产物写入位置。

## 新目录职责

| 新目录 | 职责 |
|---|---|
| `config/` | 全局 profile、target profile、project config。 |
| `projects/bfp_6_8g_i7_fr4/plans/` | 候选计划 CSV、round plan、baseline plan。 |
| `projects/bfp_6_8g_i7_fr4/layouts/` | DXF/SVG/params/DRC 等版图生成产物。 |
| `projects/bfp_6_8g_i7_fr4/results/` | RFPro/FEM 导出、score、summary、training dataset、prediction report。 |
| `projects/bfp_6_8g_i7_fr4/runs/` | 后续 run_manifest、artifact_manifest、state、logs 的标准输出根。 |
| `projects/bfp_6_8g_i7_fr4/reports/` | 项目报告 HTML/PDF 和发布资产。 |
| `projects/bfp_6_8g_i7_fr4/references/` | 论文、文章分析、参考图片和提取资料。 |
| `projects/bfp_6_8g_i7_fr4/docs/` | 该项目专用流程说明和项目内参考说明。 |

## 主要旧路径映射

| 旧路径 | 新路径 |
|---|---|
| `ADS/filter_opt_i7_fr4_round*.csv` | `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round*.csv` |
| `ADS/interdigital_7o_fr4_210um_round*/` | `projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_fr4_210um_round*/` |
| `ADS/results/interdigital_7o_fr4_210um_round*/` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/` |
| `ADS/results/interdigital_7o_fr4_training_dataset.csv` | `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_training_dataset.csv` |
| `ADS/ADS自动仿真流程说明.md` | `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md` |
| `ADS/6G宽带带通滤波器文章分析报告.html` | `projects/bfp_6_8g_i7_fr4/references/6g_bpf_report/6G宽带带通滤波器文章分析报告.html` |
| `6-8G_7O滤波器设计优化报告.html` | `projects/bfp_6_8g_i7_fr4/reports/legacy/6-8G_7O滤波器设计优化报告.html` |

完整条目见 `docs/ARCH_ADS_ASSET_MIGRATION_20260801.csv`。

## 后续要求

- 新脚本默认输入输出必须使用 `projects/bfp_6_8g_i7_fr4/...`。
- 历史文档中的 `SIM/ADS` 路径视为迁移前路径，查找时先按本迁移表映射。
- 后续真实 ADS/FEM 运行不得把新结果写回旧 `ADS/` 目录。
- 旧 CLI 可以继续存在，但必须逐步变成读取 project config 的薄入口。
