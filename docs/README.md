# ADS 自动仿真项目文档索引

Status: Active
Domain: DOCS
Canonical: `docs/README.md`
Related: `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`, `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档是 `E:\OneDrive\4.Code\SIM\docs` 的总入口。当前项目已经从旧 `ADS/` 混合目录迁移到新项目边界：

```text
projects/bfp_6_8g_i7_fr4/
```

旧 `ADS/` 只保留迁移说明，不再作为新 plan、layout、result、report 的写入根目录。

## Canonical 主文档

| 领域 | 当前 canonical 主文档 | 说明 |
|---|---|---|
| ARCH | `arch/ADS版图自动仿真项目框架设计.md` | 顶层框架、对象模型、ADS API 能力边界、Python 脚本管理、数据流、优化路线和文档管理体系。 |
| ARCH | `arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md` | 独立评审和缺口分析，登记 P0/P1/P2 风险、补齐建议和平台化 gate。 |
| ARCH | `arch/ARCH_REFACTOR_TODO.md` | 项目重构 TODO，记录 P0/P1/P2 待办、验收标准、推荐执行顺序和风险。 |
| ARCH | `arch/ARCH_REFACTOR_TASK_PROGRESS.md` | 项目重构任务记录，记录每次重构的完成内容、验证和剩余工作。 |
| ARCH | `arch/ARCH_ADS_ASSET_MIGRATION_20260801.md` | 旧 `ADS/` 资产迁移到 `projects/bfp_6_8g_i7_fr4/` 的说明和映射。 |
| ARCH | `arch/ARCH_DIRECTORY_GOVERNANCE.md` | `docs/`、`tools/` 和 `src/simads/` 的分层治理、迁移 gate 和兼容策略。 |
| ARCH | `arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` | `docs/` 内部目录架构、目标归属、分批迁移、旧路径归档和验收 gate。 |
| ARCH | `arch/ARCH_DOCS_MIGRATION_20260801.csv` | `docs/` 当前文件到目标子目录的迁移映射表。 |
| DATA | `data/DATA_SCHEMA_REGISTRY.md` | profile、project、target、candidate、layout、score、summary 和 training dataset 的字段契约。 |
| DATA | `data/DATA_RUN_MANIFEST_SCHEMA.md` | `run_manifest.json`、`artifact_manifest.json`、`state.json` 的 P0 最小字段和追溯规则。 |
| ENV | `env/ENV_UV_COMPANY_20260801.md` | 公司电脑 ADS 自动化 uv 环境记录。 |
| ENV | `env/ENV_ADS_API_CAPABILITY_MATRIX.md` | ADS API 文档源、Python 包、示例和能力验证矩阵。 |
| TEST | `test/TEST_STRATEGY.md` | ADS 自动仿真测试策略，定义 Python、schema、profile、ADS API、dry-run、baseline 和 batch run 的测试 gate。 |
| FLOW | `flow/FLOW_RUN_STATE_MACHINE.md` | ADS 自动仿真 run stage/status、失败分类、resume 和幂等规则。 |
| FLOW | `flow/FLOW_STANDARD_PIPELINE_CONTRACT.md` | 标准 pipeline 契约，固定版图生成、ADS 导入、层映射、单位、端口、频段和评分规则。 |
| FLOW | `flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md` | ADS workspace、template cell、emSetup 和 substrate 文件的写入安全策略。 |
| FLOW | `flow/FLOW_JOB_SCHEDULING_POLICY.md` | ADS 自动仿真任务调度策略，定义 license、并发、workspace 锁、超时、失败熔断、候选优先级和 resume。 |
| FLOW | `flow/FLOW_MANUAL_INTERVENTION_LOG.md` | ADS GUI 人工介入记录模板，覆盖手动导入、端口、via、emSetup、simulate、导出和残留清理。 |
| FLOW | `../projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md` | 当前可执行 ADS 自动仿真闭环流程，包含 home/company profile、命令和脚本清单。 |
| LAYOUT | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` | 从论文、公式、截图或原理图重构参数化版图时的拓扑、层叠、单位、端口、via、DRC 和 ADS 导入审查清单。 |
| RESULT | `result/RESULT_I7_FR4_ROUND_INDEX.md` | FR4 7 阶交指滤波器 round2-round7 的 plan、结果、baseline 和候选结论索引。 |
| RESULT | `result/RESULT_BASELINE_FREEZE_POLICY.md` | baseline freeze、复测、漂移判定、勘误和报告引用规则。 |
| OPT | `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md` | target profile、硬约束、软目标、评分版本、baseline 改善和多器件扩展规则。 |
| OPT | `opt/ROUND_SCRIPT_MIGRATION_PLAN.md` | 历史 round 候选脚本迁移、索引校验和 active sweep 收敛策略。 |
| OPT | `opt/FR4交指滤波器搜索算法改进方案.md` | FR4 7 阶交指滤波器搜索算法、目标函数、代理模型和下一轮策略。 |
| MFG | `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` | 制造容差和材料漂移鲁棒性检查计划，覆盖 FR4 Er、板厚、铜厚、线宽、间距、长度、via 和 release gate。 |
| REPORT | `report/REPORT_TEMPLATE_PLAYBOOK.md` | HTML/PDF 报告模板、发布 gate、导出检查、数据一致性和冻结规则。 |
| FILTER | `devices/交指带通滤波器回波损耗影响因素.md` | 交指带通滤波器回损理论、版图参数影响和当前优化要点。 |
| FILTER | `devices/FR4折叠SIR带通滤波器分支.md` | FR4 折叠 SIR 带通滤波器分支方案和参考分析。 |
| FILTER | `devices/FR4高低阻抗带通滤波器优化TODO.md` | FR4 高低阻抗滤波器优化待办和实验方向。 |
| FILTER | `devices/二维码像素化带通滤波器设计报告.md` | 二维码式二值像素化带通滤波器文献归纳、FR4 210um 初版参数和自动化生成路径。 |

## 项目资产入口

| 类型 | 新路径 |
|---|---|
| 项目配置 | `../config/projects/bfp_6_8g_i7_fr4.json` |
| ADS profile 配置 | `../config/ads_profiles.json` |
| 目标 profile | `../config/targets/fr4_25db_rl6.json` |
| 候选计划 CSV | `../projects/bfp_6_8g_i7_fr4/plans/` |
| 版图产物 | `../projects/bfp_6_8g_i7_fr4/layouts/` |
| 仿真结果 | `../projects/bfp_6_8g_i7_fr4/results/` |
| 标准 run 目录 | `../projects/bfp_6_8g_i7_fr4/runs/` |
| 项目报告 | `../projects/bfp_6_8g_i7_fr4/reports/` |
| 参考文章和图片 | `../projects/bfp_6_8g_i7_fr4/references/` |

## Docs 目标分层

当前 `docs/` 已完成 Phase 1-4 的物理分层迁移；根目录仅保留 `README.md` 和子文件夹，退役的旧路径说明已收进 `archive/`。迁移规划以 `arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` 为准。长期目标结构：

```text
docs/
  README.md
  arch/
  data/
  env/
  flow/
  layout/
  devices/
  opt/
  result/
  mfg/
  report/
  test/
  archive/
```

迁移原则：

- Phase 0 只冻结规划和映射表规则。
- Phase 1 先迁低风险辅助文档。
- Phase 2 再迁被流程和脚本引用的数据、流程、优化和结果文档。
- Phase 3 已迁移主框架、重构 TODO、任务记录等高频入口。
- 每批迁移必须更新 README、Canonical、Related，并把旧路径说明或旧名索引归档。

## 项目阅读树

新读者或后续维护者应能只从本 README 出发，按树状路径理解整个项目和每个分支：

```text
SIM ADS 自动仿真平台
├─ 1. 平台总纲
│  ├─ docs/arch/ADS版图自动仿真项目框架设计.md
│  ├─ docs/arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md
│  ├─ docs/arch/ARCH_REFACTOR_TODO.md
│  └─ docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md
├─ 2. 环境和工程边界
│  ├─ config/ads_profiles.json
│  ├─ config/projects/bfp_6_8g_i7_fr4.json
│  ├─ docs/env/ENV_UV_COMPANY_20260801.md
│  └─ docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md
├─ 3. 自动化闭环
│  ├─ projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md
│  ├─ docs/flow/FLOW_RUN_STATE_MACHINE.md
│  ├─ docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md
│  ├─ docs/flow/FLOW_JOB_SCHEDULING_POLICY.md
│  └─ docs/flow/FLOW_MANUAL_INTERVENTION_LOG.md
├─ 4. 数据契约和可追溯
│  ├─ docs/data/DATA_SCHEMA_REGISTRY.md
│  ├─ docs/data/DATA_RUN_MANIFEST_SCHEMA.md
│  ├─ projects/bfp_6_8g_i7_fr4/plans/
│  ├─ projects/bfp_6_8g_i7_fr4/layouts/
│  ├─ projects/bfp_6_8g_i7_fr4/results/
│  └─ projects/bfp_6_8g_i7_fr4/runs/
├─ 5. 版图和器件分支
│  ├─ docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md
│  ├─ docs/devices/交指带通滤波器回波损耗影响因素.md
│  ├─ docs/devices/FR4折叠SIR带通滤波器分支.md
│  ├─ docs/devices/FR4高低阻抗带通滤波器优化TODO.md
│  ├─ docs/devices/二维码像素化带通滤波器设计报告.md
│  └─ projects/bfp_6_8g_i7_fr4/docs/fr4_stub_bpf_l3_reference.md
├─ 6. 优化、制造和测试
│  ├─ docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md
│  ├─ docs/opt/FR4交指滤波器搜索算法改进方案.md
│  ├─ docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md
│  ├─ docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md
│  └─ docs/test/TEST_STRATEGY.md
└─ 7. 结果和报告
   ├─ docs/result/RESULT_I7_FR4_ROUND_INDEX.md
   ├─ docs/result/RESULT_BASELINE_FREEZE_POLICY.md
   ├─ docs/report/REPORT_TEMPLATE_PLAYBOOK.md
   └─ projects/bfp_6_8g_i7_fr4/reports/
```

分支阅读规则：

| 目标 | 阅读入口 | 继续追踪 |
|---|---|---|
| 理解平台为什么这样分层 | `arch/ADS版图自动仿真项目框架设计.md` | `arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`、`arch/ARCH_REFACTOR_TODO.md` |
| 理解当前公司电脑如何运行 | `env/ENV_UV_COMPANY_20260801.md` | `config/ads_profiles.json`、`env/ENV_ADS_API_CAPABILITY_MATRIX.md` |
| 理解一轮 ADS 自动仿真怎么跑 | `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md` | `flow/FLOW_RUN_STATE_MACHINE.md`、`data/DATA_RUN_MANIFEST_SCHEMA.md` |
| 理解交指滤波器分支 | `devices/交指带通滤波器回波损耗影响因素.md` | `result/RESULT_I7_FR4_ROUND_INDEX.md`、`opt/FR4交指滤波器搜索算法改进方案.md` |
| 理解折叠 SIR 分支 | `devices/FR4折叠SIR带通滤波器分支.md` | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`、项目 `layouts/` 和 `results/` |
| 理解高低阻抗分支 | `devices/FR4高低阻抗带通滤波器优化TODO.md` | `fr4_stub_bpf_l3_reference.md`、`opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md` |
| 理解二维码像素化分支 | `devices/二维码像素化带通滤波器设计报告.md` | `config/projects/pixel_qr_bpf_fr4_210um.json`、`config/pipelines/pixel_qr_bpf_fr4_210um_v1.json`、`projects/pixel_qr_bpf_fr4_210um/layouts/pixel_qr_bpf_fr4_210um_r0/` |
| 判断候选是否可制造 | `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`、目标板厂工艺规则 |
| 准备正式报告 | `report/REPORT_TEMPLATE_PLAYBOOK.md` | `result/RESULT_BASELINE_FREEZE_POLICY.md`、项目 `reports/` |

## 关键数据

| 文件 | 定位 |
|---|---|
| `../projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_training_dataset.csv` | round2-round6 合并训练集，包含参数、指标、约束余量和综合评分。 |
| `../projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round7.csv` | round7 代理模型候选参数表。 |
| `../projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_round7_predictions.csv` | round7 候选预测指标、EI 和改进概率。 |
| `../projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md` | 当前 FR4 7 阶交指 baseline 冻结记录，包含指标、hash 和漂移容差。 |
| `../projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json` | baseline 冻结记录的机器可读版本。 |
| `../config/round_script_migration.json` | 历史 round 候选脚本迁移索引，配合 `tools/check_round_script_migration.py` 做迁移前检查。 |
| `../config/optimizer/i7_fr4_deterministic_variant_probe.json` | FR4 7 阶历史 round 经验扫描迁移探针，配合 `tools/propose_filter_candidates.py --validate-only` 校验。 |
| `../docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv` | 旧路径到新路径的完整迁移索引。 |

## 当前报告

| 文件 | 定位 |
|---|---|
| `../projects/bfp_6_8g_i7_fr4/reports/legacy/6-8G_7O滤波器设计优化报告.html` | 6-8 GHz 7 阶滤波器设计优化 HTML 报告。 |
| `../projects/bfp_6_8g_i7_fr4/reports/legacy/6-8G_7O滤波器设计优化报告.pdf` | 6-8 GHz 7 阶滤波器设计优化 PDF 报告。 |
| `../projects/bfp_6_8g_i7_fr4/references/6g_bpf_report/6G宽带带通滤波器文章分析报告.html` | 6G 宽带带通滤波器文章分析报告。 |
| `../SIM-83_plus_滤波器优化验证报告.html` | SIM-83+ 滤波器优化验证报告，暂未纳入 ADS 项目目录。 |

## 进度记录路由

| 领域 | 进度入口 | 规则 |
|---|---|---|
| 项目重构待办 | `arch/ARCH_REFACTOR_TODO.md` | 记录 P0/P1/P2 TODO、验收标准、推荐执行顺序和风险。 |
| 项目重构进度 | `arch/ARCH_REFACTOR_TASK_PROGRESS.md` | 记录正式重构任务闭环、验证结果、剩余工作和下一步。 |
| ADS 环境 | `env/ENV_UV_COMPANY_20260801.md`、`env/ENV_ADS_API_CAPABILITY_MATRIX.md` | 记录公司/家里 Python、ADS API、workspace、library、substrate、template 差异。 |
| 自动化流程 | `../projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`、`flow/FLOW_MANUAL_INTERVENTION_LOG.md` | 记录导入、emSetup、RFPro、导出、日志、超时和人工介入。 |
| Python 脚本管理 | `arch/PYTHON_SCRIPT_MANAGEMENT.md` | 记录脚本状态、可复用模块抽取和运行时边界。 |
| 交指滤波器优化 | `result/RESULT_I7_FR4_ROUND_INDEX.md`、`opt/FR4交指滤波器搜索算法改进方案.md` | 记录 roundN 候选、仿真结果、评分、下一轮决策。 |
| 文档治理 | `arch/ARCH_DIRECTORY_GOVERNANCE.md`、`arch/ARCH_REFACTOR_TODO.md` | 记录文档改名、索引补齐、目录治理和迁移计划。 |
| 报告输出 | `report/REPORT_TEMPLATE_PLAYBOOK.md` | 记录 HTML/PDF 模板、图片、公式、版图分析报告调整和发布 gate。 |

## 快速查找规则

- 查项目总体架构：先读 `arch/ADS版图自动仿真项目框架设计.md`。
- 查框架缺陷和平台化 gate：读 `arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`。
- 查项目重构待办：读 `arch/ARCH_REFACTOR_TODO.md`。
- 查项目重构任务记录：读 `arch/ARCH_REFACTOR_TASK_PROGRESS.md`。
- 查 docs/tools 是否需要拆目录及治理规则：读 `arch/ARCH_DIRECTORY_GOVERNANCE.md`。
- 查 docs 目标目录、文件归属和迁移阶段：读 `arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`。
- 查数据字段契约：读 `data/DATA_SCHEMA_REGISTRY.md`。
- 查 run/artifact/state 追溯规则：读 `data/DATA_RUN_MANIFEST_SCHEMA.md`。
- 查 run stage/status 和 resume 规则：读 `flow/FLOW_RUN_STATE_MACHINE.md`。
- 查 ADS workspace 写入安全策略：读 `flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`。
- 查 ADS 批量任务调度、并发、超时和失败熔断：读 `flow/FLOW_JOB_SCHEDULING_POLICY.md`。
- 查 ADS GUI 人工介入记录格式：读 `flow/FLOW_MANUAL_INTERVENTION_LOG.md`。
- 查测试 gate 和验证命令：读 `test/TEST_STRATEGY.md`。
- 查论文/截图/公式到参数化版图的重构审查：读 `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`。
- 查旧 `ADS/` 文件去哪了：读 `arch/ARCH_ADS_ASSET_MIGRATION_20260801.md` 和 `arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv`。
- 查 ADS 怎么跑：先读 `../projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`。
- 查家里/公司环境：先看 `../config/ads_profiles.json`，再看 `env/ENV_UV_COMPANY_20260801.md` 和 Python profile 实现 `../src/simads/config/profiles.py`。
- 查每轮结果：先看 `../projects/bfp_6_8g_i7_fr4/results/<round>/sweep_summary.csv`。
- 查候选参数：先看 `../projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round*.csv`。
- 查代理模型候选预测：先看 `../projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_round*_predictions.csv`。
- 查目标函数和 target profile 规则：读 `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`。
- 查 round 专用候选脚本迁移策略：读 `opt/ROUND_SCRIPT_MIGRATION_PLAN.md`，并运行 `../tools/check_round_script_migration.py`。
- 查当前冻结 baseline：先看 `../projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`。
- 查 baseline 冻结、复测、漂移和勘误规则：读 `result/RESULT_BASELINE_FREEZE_POLICY.md`。
- 查 FR4 7 阶交指 round 结论：先看 `result/RESULT_I7_FR4_ROUND_INDEX.md`。
- 查制造容差、材料漂移和 robust release gate：读 `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`。
- 查 HTML/PDF 报告发布 gate 和导出规则：读 `report/REPORT_TEMPLATE_PLAYBOOK.md`。

## 新增文档规则

新增正式文档前按以下顺序判断：

1. 能否补充到现有 canonical 文档中。
2. 是否需要独立生命周期，例如独立 TODO、独立进度、独立环境约束或独立结果索引。
3. 是否已有同领域同类型文件，避免重复创建近义文档。
4. 文件名是否符合 `<DOMAIN>_<SUBJECT>_<TYPE>.md`。
5. 新文件是否包含元数据块。
6. 新文件是否已经加入本 README。
7. 相关主文档是否反向引用它。

## 迁移约束

- 新架构目录是当前有效边界，后续 ADS 项目资产默认进入 `projects/bfp_6_8g_i7_fr4/`。
- 文件移动必须生成迁移表，并更新 README、相关文档和脚本引用。
- 历史中文文件名在迁移前仍视为有效文档，不创建重复内容的新文档。
- 结果 CSV、DXF、JSON、HTML/PDF 报告必须保留可追溯关系。
- 已冻结的环境、层叠、基线结果文档只允许补勘误，不随意改写结论。
- 所有 Markdown 文档使用 UTF-8 编码。

