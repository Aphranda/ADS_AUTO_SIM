# ADS 自动仿真项目重构 TODO

Status: Active
Domain: ARCH
Canonical: `docs/arch/ARCH_REFACTOR_TODO.md`
Related: `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`, `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
Last updated: 2026-08-04
Owner: ADS Automation

本文档跟踪 ADS 版图自动仿真项目从现有 `tools/*.py` 脚本集合向框架化平台演进的重构待办。TODO 文档只记录验收标准、推荐执行顺序、P0/P1/P2 待办和当前风险；每次实际任务闭环记录写入 `ARCH_REFACTOR_TASK_PROGRESS.md`。当前已开始首批 `tools/ads/` 和 `tools/layout/` 物理分拆，旧路径保留兼容 wrapper。

## 验收标准摘要

| 优先级 | 验收标准 |
|---|---|
| P0 | 不移动外部 ADS workspace 的前提下，项目资产按新架构进入 `projects/<project_id>/...`；单候选/批量入口保持兼容；home profile 和 ADS API smoke test 可独立运行；单候选成功/失败 run 都能输出 state、run manifest、artifact manifest、日志和可追溯 score/summary 字段；template cell 不会被普通候选流程覆盖。 |
| P1 | round 级结果、baseline、target profile、score schema、人工 GUI 介入和报告发布 gate 全部可追溯；round2-roundN 有结果索引，baseline 漂移可复测。 |
| P2 | `src/simads` 模块化完成：geometry、exporters、ADS workspace/layout/emsetup/rfpro/dataset、scoring、optimizer、device plugin 逐步替代旧脚本内部逻辑，旧 CLI 只保留薄入口。 |

## 推荐执行顺序

| 顺序 | 待办 | 原因 |
|---|---|---|
| 1 | P0-01 ADS 资产边界迁移 | 先把旧 `ADS/` 混合目录拆入 `projects/<project_id>/...`，否则后续 schema 和 manifest 仍会绑定旧边界。 |
| 2 | P0-02 schema registry | 先固定数据契约，避免后续 manifest/score/summary 字段继续漂移。 |
| 3 | P0-03 run/artifact manifest schema | 代码已有初版输出，需要正式冻结字段和必填规则。 |
| 4 | P0-04 score 回填 run 元数据 | 让 score.csv 成为可追溯数据源，summary 才能可靠合并。 |
| 5 | P0-05 sweep 预生成 run_id | 失败候选也能进入 summary 和任务回溯。 |
| 6 | P0-06 workspace 写入安全 gate | 在继续真实 ADS/FEM 前保护 template cell 和历史结果。 |
| 7 | P0-07 baseline freeze | 当前初始模板仍是最好候选，必须先冻结再继续比较。 |
| 8 | P1 结果索引和报告发布 gate | 让 round 结论、报告、图片和数据来源一致。 |
| 9 | P2 模块化迁移 | 行为和契约稳定后，再抽 geometry/scoring/ADS 子模块。 |

---

## P0 - 平台化前置 Gate

### P0-00 第一批兼容重构落地

**目标：** 建立 `src/simads` 包骨架、profile/runtime 基础模块，并保持旧 `tools` 入口兼容。

- [x] 新增 `src/simads/config`，集中管理 home/company profile。
- [x] 新增 `src/simads/runtime`，提供 run id、state、manifest、hash 和错误分类 helper。
- [x] `tools/ads_profiles.py` 改为兼容转发层。
- [x] `tools/run_ads_filter_candidate.py` 新增 `--project-id --round-id --run-id --run-dir`，并输出 `state.json`、`run_manifest.json`、`artifact_manifest.json`。
- [x] `tools/run_ads_filter_sweep.py` 向单候选入口传递 project/round，并预留 summary 状态字段。
- [x] 新增 `tools/check_ads_profile.py`。
- [x] `tools/check_ads_python_env.py` 支持 `--profile home`。
- [x] 新增 `pyproject.toml`。

闭环记录：见 `ARCH_REFACTOR_TASK_PROGRESS.md` 中 `ARCH-REFACTOR-TASK-20260801-001`。


### P0-01 ADS 资产边界迁移

**目标：** 按新架构把旧 `ADS/` 混合资产拆入项目目录，旧 `ADS/` 不再作为新产物根。

- [x] 新增 `projects/bfp_6_8g_i7_fr4/plans` 并迁入 plan CSV。
- [x] 新增 `projects/bfp_6_8g_i7_fr4/layouts` 并迁入 DXF/SVG/params/DRC 版图产物。
- [x] 新增 `projects/bfp_6_8g_i7_fr4/results` 并迁入 RFPro/FEM/score/summary/training dataset。
- [x] 新增 `projects/bfp_6_8g_i7_fr4/references` 并迁入文章分析和图片资产。
- [x] 新增 `projects/bfp_6_8g_i7_fr4/reports` 并迁入 6-8G 旧报告。
- [x] 新增 `config/ads_profiles.json`、`config/projects/bfp_6_8g_i7_fr4.json`、`config/targets/fr4_25db_rl6.json`。
- [x] 生成 `ARCH_ADS_ASSET_MIGRATION_20260801.md/csv`。
- [x] 更新关键脚本默认路径，不再默认读取 `SIM/ADS`。

闭环记录：见 `ARCH_REFACTOR_TASK_PROGRESS.md` 中 `ARCH-REFACTOR-TASK-20260801-002`。
### P0-02 建立 Data Schema Registry

**现状：** 已新增 `data/DATA_SCHEMA_REGISTRY.md`，profile、project、target profile、candidate、layout、score、summary 和 training dataset 的最小字段已经登记。后续需要把代码输出与该 schema 对齐。

**影响：** 后续 score、summary、manifest、训练集字段容易各自演化，旧数据兼容困难。

- [x] 新增 `data/DATA_SCHEMA_REGISTRY.md`。
- [x] 定义 profile schema：profile_id、ads_root、workspace、library、template_cell、substrate、ads_python、host_python。
- [x] 定义 candidate schema：candidate_id、round_id、参数字段、单位、生成算法、父候选。
- [x] 定义 layout schema：layout_id、candidate_id、units、layers、ports、shapes、vias、geometry_hash。
- [x] 定义 score schema：run_id、profile_id、score_version、target_profile、metrics、constraint margins、pass/fail。
- [x] 定义 training dataset schema：source_runs、feature fields、metric fields、excluded_reason。

### P0-03 冻结 Run Manifest / Artifact Manifest Schema

**现状：** 已新增 `data/DATA_RUN_MANIFEST_SCHEMA.md`，`run_manifest.json`、`artifact_manifest.json` 和 `state.json` 的 P0 最小字段已经冻结。后续代码可追加兼容字段，但不得改变已定义字段语义。

**影响：** 报告和训练集一旦引用 manifest，需要稳定字段和版本规则。

- [x] 新增 `data/DATA_RUN_MANIFEST_SCHEMA.md`。
- [x] 固定 `run_manifest.json` 必填字段和可选字段。
- [x] 固定 `artifact_manifest.json` artifact 类型、路径、hash、producer 规则。
- [x] 规定 `schema_version` 升级策略。
- [x] 规定 run_id 生成规则和 round_id/candidate_id/project_id 命名规则。

### P0-04 Score CSV 回填 Run 元数据

**现状：** `analyze_ads_dataset.py` 已接收 run metadata，`run_ads_filter_candidate.py` 已把 run/project/round/candidate/profile/target/score_version 传入 score CSV。

**影响：** `sweep_summary.csv` 只能靠文件名推断，无法满足框架追溯要求。

- [x] 修改 `analyze_ads_dataset.py`，支持 `--run-id`、`--profile-id`、`--score-version`、`--target-profile-id`。
- [x] `run_ads_filter_candidate.py` 调用评分脚本时传入 run 元数据。
- [x] score CSV 输出字段包含 `run_id/profile_id/score_version/target_profile_id/status/error_class/failed_step/elapsed_s`。
- [x] 固定 RFPro CSV 和 FEM dataset 两种评分来源的字段一致性。

### P0-05 Sweep 预生成 Run ID 并合并 State/Manifest

**现状：** 批量入口已预生成 run_id 并传递 run_dir；summary 写入时已读取 `state.json` 和 `run_manifest.json`，成功和失败候选均可追溯 run。

**影响：** 失败候选难以进入训练集和问题回溯。

- [x] `run_ads_filter_sweep.py` 为每个候选预生成 run_id 并传给 candidate runner。
- [x] summary 写入时读取对应 `state.json` 和 `run_manifest.json`。
- [x] 成功和失败候选都进入 summary。
- [x] summary 字段固定为 schema registry 中定义的字段。

### P0-06 ADS Workspace 写入安全 Gate

**现状：** 已新增 `src/simads.safety` 和 `flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`，单候选 runner、底层 emSetup clone 和 substrate patch 均已接入写入安全 gate。普通候选流程无法误写 template cell，substrate 文件修改必须显式 `--force`。

**影响：** 真实 ADS/FEM 批量运行时存在误覆盖模板或污染 baseline 的风险。

- [x] candidate runner 启动前检查 `target_cell != template_cell`。
- [x] 对 `--overwrite-setup` 增加 target cell 范围检查。
- [x] 删除 cell、覆盖 template、修改 substrate 等操作必须显式 `--force`。
- [x] 写 ADS 前打印并写入 manifest：profile、workspace、library、template_cell、target_cell、substrate、force。

### P0-07 Baseline Freeze

**现状：** 当前最好候选已冻结为 `i7_fr4_baseline_freeze_20260801`，覆盖 `i7_fr4_r3_base/r4_base/r5_base/r6_base`，并记录指标、hash 和漂移容差。历史结果没有 run manifest，因此以 legacy migrated 方式冻结。

**影响：** 后续新候选无法稳定判断是否真正优于 baseline，环境漂移也难以识别。

- [x] 新增 baseline frozen 记录，覆盖 `i7_fr4_r3_base/r4_base/r5_base/r6_base`。
- [x] 记录 candidate_id、run_id、profile、ADS version、substrate、layout hash、score version、关键指标。
- [x] 定义漂移容差：S21@5G、S21@6G、S21@8G、passband_min_s21、worst S11/S22。
- [x] 新 profile/ADS/substrate/emSetup 变更后，先复跑 baseline。

### P0-08 测试策略文档

- [x] 新增 `test/TEST_STRATEGY.md`。
- [x] 定义纯 Python unit test、几何 golden、profile check、ADS API smoke、short FEM、baseline full run。
- [x] 把当前验证命令写入测试策略。
- [x] 区分 host Python 和 ADS Python 测试入口。

### P0-09 Run State Machine

**现状：** 已新增 `flow/FLOW_RUN_STATE_MACHINE.md` 和 `src/simads/runtime/state_machine.py`，`state.json` 与 `run_manifest.json` 的 `stage/status/error_class` 已有统一允许值和轻量校验。

- [x] 定义 run stage：`planned`、`layout_ready`、`ads_imported`、`emsetup_ready`、`rfpro_ready`、`sim_running`、`dataset_exported`、`scored`、`reported`、`completed`、`failed`。
- [x] 定义 run status：`planned`、`running`、`completed`、`failed`、`skipped`。
- [x] 定义 error_class 和 resume 映射。
- [x] `write_state()` 和 `write_run_manifest()` 接入 stage/status/error_class 校验。
- [x] 文档同步到 `data/DATA_RUN_MANIFEST_SCHEMA.md`。

---

## P1 - 结果治理、报告和优化闭环

### P1-01 Round 结果索引

- [x] 新增 `result/RESULT_I7_FR4_ROUND_INDEX.md`。
- [x] 记录 round2-roundN 的 plan、候选、summary、最佳点、失败点和结论。
- [x] 记录当前 baseline 与 round7/round8 的关系。

### P1-02 Objective / Target Profile 文档

- [x] 新增 `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`。
- [x] 定义 target profile schema、硬约束、软目标、权重、采样点和 score version。
- [x] 明确不同器件不得硬编码滤波器专用指标。

### P1-03 Layout Reconstruction Checklist

- [x] 新增 `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`。
- [x] 固化论文、公式、图片到参数化版图的审查清单。
- [x] 覆盖拓扑、层叠、端口、via、ground、边界、单位、DRC 和制造限制。

### P1-04 Job Scheduling Policy

- [x] 新增 `flow/FLOW_JOB_SCHEDULING_POLICY.md`。
- [x] 定义 license、并发、workspace 锁、超时、最大连续失败数和候选优先级。

### P1-05 Baseline Freeze Policy

- [x] 新增 `result/RESULT_BASELINE_FREEZE_POLICY.md`。
- [x] 定义 Frozen 状态、复测流程、漂移判据和勘误规则。

### P1-06 Manufacturing Tolerance Plan

- [x] 新增 `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`。
- [x] 对 FR4 Er、板厚、铜厚、线宽、间距、长度做 tolerance sweep 规则。

### P1-07 Manual GUI Intervention Log

- [x] 新增 `flow/FLOW_MANUAL_INTERVENTION_LOG.md` 或模板。
- [x] 记录人工 ADS GUI 介入的时间、对象、动作、原因、截图/导出文件和复现影响。

### P1-08 Report Release Gate

- [x] 新增或扩展 `report/REPORT_TEMPLATE_PLAYBOOK.md`。
- [x] HTML/PDF 报告必须引用 manifest、score、曲线、版图资产和 target profile。

### P1-09 Directory Governance

- [x] 新增 `ARCH_DIRECTORY_GOVERNANCE.md`。
- [x] 明确 `docs/` 先逻辑分层、后物理迁移。
- [x] 明确 `tools/` 暂不大规模移动，先抽复用逻辑到 `src/simads`。
- [x] 定义文档领域前缀、状态字段、迁移 gate 和 CLI 兼容策略。
- [x] 完成 `src/simads.safety` 写入安全模块后，再评估 `tools/ads/` 物理迁移。

### P1-10 Framework Compliance Alignment

**现状：** 2026-08-01 复核 `ADS版图自动仿真项目框架设计.md` 后，当前实现与框架约 75%-80% 符合。主要偏差集中在文档路径漂移、run 目录当前实现与目标结构并存、部分生成器默认路径仍指向旧目录、device plugin contract 未完全形式化、layout/source_map/DRC 机器校验不足。

**影响：** 如果不先把这些偏差显式纳入待办，后续继续优化滤波器时容易把公司/家里环境、旧 `ADS/` 路径、不同 run 输出根和未冻结接口混在一起。

- [x] 修正主框架和 README 中当前公司工作目录说明，当前根目录为 `E:\OneDrive\4.Code\SIM`。
- [x] README 的进度记录路由改为现有 canonical 文档，不再指向缺失文件。
- [x] 主框架明确 `config/ads_profiles.json` 是 home/company 环境的唯一机器可读来源，文档中的路径只作为示例。
- [x] 主框架和 run manifest 文档明确：当前实现仍使用 `projects/<project_id>/results/<round>/runs/<run_id>/`，P1 再迁移到 `projects/<project_id>/runs/<run_id>/`。
- [ ] 更新非交指 layout generator 的默认输出目录，逐步切到 `projects/<project_id>/layouts/...`。
- [ ] 新增或细化 `DEVICE_PLUGIN_CONTRACT.md`，覆盖 `score_adapters`、`report_sections`、context-aware `optimizer_bounds(project_context)`。
- [x] 将 layout schema 的 `source_map`、`port_on_metal`、`via_inside_pad`、`layer_exists`、layer map version 纳入机器校验 gate。
- [ ] P1 run 目录迁移：让新 run 默认写入 `projects/<project_id>/runs/<run_id>/`，并保留 round results 下的索引或兼容映射。

### P1-11 Docs Internal Architecture

**现状：** `docs/` 已完成 Phase 0-4 分层迁移：低风险辅助文档、数据/流程/优化/结果规范和器件分支文档已进入目标目录；Phase 3 已迁移 `ARCH_*.md`、主框架和 Python 脚本管理文档到 `docs/arch/`；当前根目录仅保留 `README.md`，旧路径说明和兼容 CSV 已归档到 `docs/archive/`。

**影响：** 新增文档越来越依赖文件名前缀查找；主框架、任务流水、结果索引、理论分析混在一起，后续物理迁移成本会持续升高。

- [x] 新增 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`，定义 `arch/data/env/flow/layout/devices/opt/result/mfg/report/test/archive` 目标结构。
- [x] 为当前 docs 文件逐一登记目标目录和迁移阶段。
- [x] 定义旧路径 stub 模板、迁移映射表字段和每批迁移验收 gate。
- [x] 在 README 建立项目阅读树，串联平台总纲、环境、自动化闭环、数据契约、器件分支、优化制造测试、结果报告。
- [x] 在 docs 架构规划中规定新增分支必须登记 Branch entry、Layout source、Config binding、Automation flow、Data trace、Optimization trace、Decision/report。
- [x] 更新 `ARCH_DIRECTORY_GOVERNANCE.md`，引用 docs 内部架构规划。
- [x] 更新 README，加入 docs 目标目录结构和本规划入口。
- [x] Phase 0：建立 `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv` 模板，不移动文件。
- [x] Phase 1 第一批：迁移 `ENV_`、`MFG_`、`REPORT_`、`TEST_`、`LAYOUT_` 文档到 `env/mfg/report/test/layout/`，旧路径保留 stub。
- [x] Phase 2：迁移 `data/flow/opt/result/devices/` 文档，并逐步更新历史引用。
- [x] Phase 3：迁移 `arch/` 文档和长任务记录。
- [x] Phase 4：确认无旧路径引用后清理根目录文件并归档旧路径说明。

### P1-12 Standard Pipeline Contract

**现状：** 已新增标准 pipeline contract，用于统一版图生成器、ADS DXF 导入/端口放置、emSetup/RFPro FEM、数据导出和评分器的模板、层、单位、端口和目标 profile。当前先覆盖 `bfp_6_8g_i7_fr4_interdigital_v1`，并已接入 sweep/candidate runner 的默认值解析和 run/score 元数据。

**影响：** 如果没有统一 pipeline contract，后续优化迭代容易继续把 template cell、layer map、单位、端口坐标来源、score profile 和 home/company 路径混在 CLI 参数里，导致结果难以复现。

- [x] 新增 `config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json`，固定 `mm`、`cond/pcvia1/EM_BOUNDARY`、`P1/P2`、`em%Setup/emSetup`、`4-10 GHz` 和 `fr4_25db_rl6`。
- [x] `config/projects/bfp_6_8g_i7_fr4.json` 和 active sweep 登记 `pipeline_id`。
- [x] 新增 `src/simads/config/pipelines.py`，提供 pipeline loader、dataclass、id 解析和只读校验。
- [x] 新增 `tools/check_pipeline_contract.py`，执行 project/profile/pipeline 一致性、脚本路径、单位、层、端口、模板、频段和评分检查。
- [x] `tools/run_ads_filter_candidate.py` 接入 `--pipeline-id`，并从 contract 解析脚本路径、模板、层、view、target profile 和 score version。
- [x] `tools/run_ads_filter_sweep.py` 接入 `--pipeline-id`，并传递到 candidate runner、summary 和失败记录。
- [x] `tools/analyze_ads_dataset.py` 输出 `pipeline_id` 元数据。
- [x] 新增 `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`。
- [x] 将 `pipeline_id/pipeline_snapshot` 正式写入 `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`。
- [x] 将标准 pipeline 检查加入正式 round 执行前 gate。
- [x] 支持同一 project 下默认 pipeline 与分支 sweep pipeline 并存。
- [x] 将 layout schema 的 `source_map`、`port_on_metal`、`via_inside_pad`、`layer_exists`、layer map version 纳入机器校验。
- [x] 为二维码像素化 FR4 210um 分支建立独立 pipeline config。
- [ ] 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立独立 pipeline config。
- [ ] 为每个非交指 pipeline 记录 topology-specific layout gate：过孔/接地语义、耦合缝隙、最小间距、端口过渡和可制造性约束。

### P1-13 QR-like Pixelated BPF Branch

**现状：** 已新增二维码式二值像素化带通滤波器独立项目 `pixel_qr_bpf_fr4_210um`，用于探索 FR4 210um、8x8/10x10 像素矩阵在 6-8 GHz 带通目标下的可行性。该分支已从 `bfp_6_8g_i7_fr4` 拆分，后续配置、版图、结果和报告均在独立项目目录维护。R0 版图规则已调整为相邻黑色像素共边无间隙，不再使用补桥矩形。

- [x] 新增 `docs/devices/二维码像素化带通滤波器设计报告.md`。
- [x] 新增 `tools/layout/generate_pixel_qr_bpf_layout.py` 和根目录兼容 wrapper。
- [x] 新增 `config/projects/pixel_qr_bpf_fr4_210um.json`。
- [x] 新增 `config/pipelines/pixel_qr_bpf_fr4_210um_v1.json`。
- [x] 新增 `projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r0.csv`。
- [x] 生成 8x8 和 10x10 R0 样例 DXF/SVG/layout JSON/params JSON/DRC。
- [x] 将相邻黑色像素连通规则改为 edge-touching no-gap 网格，移除 `conn_h/conn_v` 补桥图形。
- [x] 已接入通用 layout contract 机器校验，覆盖 `port_on_metal`、`source_map/generator`、声明层、已使用层、过孔焊盘/落铜和 `layer_map_version`。
- [x] 新增像素化分支专用 layout/DRC 机器校验，覆盖孤岛统计、最小间距、feed/pixel 连通性和 matrix `source_map` 完整性。
- [ ] 根据第一次 FEM 和板厂约束设置像素化分支的 `max_island_components` 推荐阈值。
- [ ] 用无间隙 R0 候选执行 ADS 导入后单候选 FEM 验证，判断是否形成带通而非低通/陷波。
- [ ] 根据第一次 FEM 响应决定是否进入 DBS/GA 二值翻转优化。

### P1-14 HFSS Standard Simulation Backend

**现状：** HFSS 3D Layout 自动化已经具备独立闭环能力，`src/simads/hfss/workflow.py` 可从 SIM `layout.json` 构建 AEDT/HFSS 工程、配置层叠和端口、执行求解、导出 S2P/trace/score/SVG，并写入 run/artifact manifest。当前已纳入标准 pipeline backend、单候选 runner 和串行 sweep 编排；并行 runner 暂保持 ADS/RFPro 专用，避免 AEDT license 和工程文件并发风险。

**影响：** 如果 HFSS 继续停留在裁决路径，ADS 和 HFSS 的配置、频段、stackup、端口、run manifest、summary 和 compare 关系会分散维护；后续批量候选无法用统一口径选择 ADS、HFSS 或 ADS+HFSS 双后端仿真。

- [x] 在 pipeline contract 中新增 `simulation_backends` 或等价字段，支持 `ads_rfpro`、`hfss3dlayout` 和 `both` 路由。
- [x] 在 pipeline config 中新增 `hfss` 配置段，固定 HFSS workflow script、profile、workspace、route、stackup_config、design、频段、点数、端口类型和 GND boundary mode。
- [x] 新增或抽象标准单候选入口，例如 `tools/run_sim_filter_candidate.py`，通过 `--backend ads|hfss|both` 调用现有 ADS runner 和 HFSS workflow；第一阶段不得破坏稳定的 `run_ads_filter_candidate.py`。
- [x] 将标准单候选入口接入 `tools/run_ads_filter_sweep.py`，支持显式 `--backend hfss|both|auto` 批量运行；默认仍为 `--backend ads`。
- [x] 将 run state machine 从 ADS 专用 stage 泛化为仿真后端通用 stage，保留 ADS 兼容映射，并覆盖 HFSS build/ports/setup/solve/export/score 阶段。
- [x] 扩展 run/artifact manifest schema，明确 `hfss3dlayout` 的 `aedt_project`、`edb_project`、`s2p`、`trace_csv`、`score_csv`、`svg`、`summary_csv` artifact 类型和 profile 语义。
- [x] 将 `FLOW_HFSS_PYAEDT_VERDICT.md` 的后续口径从 verdict-only 调整为 HFSS backend 文档；ADS/HFSS 对比保留为独立 compare workflow，而不是 HFSS 的唯一角色。
- [x] 为 HFSS backend 增加只读 pipeline/profile gate，检查 pyAEDT 环境、AEDT 路径、workspace、stackup_config、layout JSON、端口和输出目录，不启动真实求解。
- [x] 在 sweep summary 或后续 backend summary 中记录每个 candidate 的 backend、simulator、run_id、score path 和可比较 trace path。

### P1-15 HFSS Connector Layout Optimization Extension

**现状：** 已新增 `flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`，将连接器/连接器等效 launch 的 HFSS 自动化仿真拆成独立扩展项。当前目标为标准 50 ohm 微带线 + 两端连接器 launch 的联合仿真，不加入滤波器或其他结构，主要迭代连接器焊盘、锥形过渡、地间隙、地过孔、via fence、端口参考面和去嵌设置，从而改善连接处自身的 S 参数。

**影响：** 如果连接器 launch 与滤波器主体混在同一优化分支中，后续会难以区分滤波器拓扑问题、端口参考面问题和连接器过渡引入的劣化；独立微带线+连接器联合仿真可以降低系统复杂度，并把优化结果作为可移植的连接器版图模块。

- [ ] 固定连接器类型或等效 footprint 版本，明确 Route A/B/C 使用边界。
- [ ] 登记用户提供的连接器 HFSS 模型路径、版本、hash、端口定义、坐标基准和参考面。
- [ ] 固定层叠、50R 线宽、联合仿真模型长度、板边位置、端口参考面和求解频段。
- [x] 将公司电脑连接器 HFSS profile 独立为 `company_connector`，固定 `D:\Work\ADS\HFSS_VERDICT` 为连接器专用工作区；公司滤波器/常规 HFSS backend 保持原工作区 `D:\Work\ADS\SIMADS_STANDARD\HFSS`。
- [x] 建立 connector launch 参数 schema，覆盖 signal pad、taper、ground clearance、via fence、reference plane、deembed 和 P1/P2 symmetry。
- [x] 新增 microstrip+connector generator：输入 stackup/50R template 和 connector 参数，输出微带线+连接器 layout JSON。
- [x] 增加连接器区域 DRC gate：pad、clearance、via、edge setback、mechanical envelope、左右对称和板厂工艺限制。
- [x] 扩展 HFSS workflow/manifest，记录 `fixture_type=microstrip_connector_50r`、`connector_model_version`、`connector_route`、`microstrip_connector_layout_json`、`connector_params_json`、`connector_hfss_model_path`、`connector_hfss_model_hash`、`connector_port_mapping`、`line_w_mm`、`line_l_mm`、`reference_plane_offset_mm` 和 `port_deembed_mm`。
- [x] 新增连接器参数审计/同步脚本 `tools/hfss/audit_connector_parameters.py`，固定 source design 变量、工程 `$sma_` 变量、3D Layout instance passed parameters 和关键对象 bbox 的检查口径。
- [x] 2026-08-04 已在公司电脑对 `D:\Work\ADS\HFSS_VERDICT\hfss_sma_connector_cpw.aedt` 执行 source-to-project 参数同步并保存；同步报告位于 `projects/hfss_sma_connector/reports/connector_parameter_sync_project_vars_20260804.json` 和 `projects/hfss_sma_connector/reports/connector_parameter_sync_project_vars_resync_20260804.json`。
- [ ] 修复 `SMA_KE_Unite_Small_Solder` 源模型的中心导体几何：当前 `Pin` bbox 仍为 `1.25mm`，与 `Hole_D` 一致而非 `Pin_D=0.95mm`；修复后必须重新运行 `audit_connector_parameters.py`，并以 `Pin diameter from bbox` 通过作为继续 Validate/solve 的 gate。
- [x] 端口命名规则勘误：HFSS 3D Layout connector pin interface port 不能强制改名；改名后会报错。端口名称必须以 AEDT 自动生成结果为准。
- [ ] 后续探索安全改名路径：仅允许使用 AEDT/PyAEDT 官方 API，需证明改名后 Validate 和 solve 均不报错，并记录 excitation/report/dataset 引用是否同步更新；当前主流程先按不改名执行。
- [ ] 将端口处理从 `Port1/Port2` 字面命名改为 logical port mapping：manifest/score/report 记录 `logical_port=P1/P2` 与 AEDT generated port name 的对应关系。
- [ ] 用只读检查脚本记录 design/port/net 状态，确认实际 generated port name、component ID、pin name 和 reference conductor 均有效，作为继续求解前 gate。
- [ ] 对 3-5 个 smoke 候选先做 layout gate，再选择 1 个候选执行 HFSS solve，输出 S2P/trace/score/compare/manifest。
- [ ] 将评分扩展为 50R baseline delta 口径，重点比较通带 S21 劣化、S11/S22、端口对称性和 4-10 GHz 宽频回波尖峰。
- [ ] Route C 使用用户提供的连接器 HFSS 模型复核前 2-3 个 launch 候选。
- [ ] 最终合并验证作为最后事项：连接器 launch 冻结并完成微带线+连接器联合仿真/Route C 复核后，再移植到滤波器 PCB 做少量整板验证。

---

## P2 - 模块化迁移

### P2-01 Geometry / Exporters

- [x] 新增 `simads.geometry`：Rect、Polygon、Path、Via、Port、Boundary、LayerMap。
- [x] 新增 `simads.exporters`：DXF/SVG/GDS/JSON writer。
- [x] 将 `tools/generate_stub_bpf_layout.py` 接入通用 `Layout` 几何对象，并新增 `_layout.json` 输出。
- [x] 将 `tools/generate_interdigital_filter_layout.py` 接入通用 `Layout` 几何对象，并覆盖 `Rect/Polygon/Via/Port/Boundary`。
- [x] 将 `tools/generate_folded_sir_bpf_layout.py` 接入通用 `Layout` 几何对象，并保留 folded SIR 方形 via pad 语义。
- [x] 将 `tools/generate_hilo_sir_bpf_layout.py` 和 `tools/generate_paper_mixed_sir_bpf_layout.py` 接入通用 `Layout` 几何对象。
- [x] 从现有 `generate_*_layout.py` 抽出通用几何能力：所有现有 layout generator 均新增结构化 `_layout.json` 输出。
- [x] 首批 layout generator 物理迁移到 `tools/layout/`，根目录保留兼容 wrapper。

### P2-02 ADS API 子模块

- [x] 新增 `simads.ads.workspace`。
- [x] 新增 `simads.ads.layout`。
- [x] 新增 `simads.ads.emsetup`。
- [x] 新增 `simads.ads.rfpro`。
- [x] 新增 `simads.ads.dataset`。
- [x] 保持旧 `tools/ads_*.py` CLI 兼容。
- [x] `tools/export_ads_fem_dataset.py` 转接到 `simads.ads.dataset` 的路径、dB/phase 和表格写出 helper。
- [x] `tools/ads_clone_emsetup_template.py` 转接到 `simads.ads.workspace/layout` 的 cell 目录解析和 P1/P2 读取 helper。
- [x] `tools/ads_import_dxf_add_ports.py` 转接到 `simads.ads.layout` 的 DXF 子集解析和 P1/P2 读取 helper。
- [x] `tools/ads_run_rfpro_fem.py` 转接到 `simads.ads.workspace/rfpro` 的 cell 目录、substrate 归一化和 RFPro setup XML helper。
- [x] 将主流程旧 ADS CLI 的纯路径/计划/解析 helper 转接到 `simads.ads`；`ads_probe_ael_words.py` 保留为 ADS-only 诊断脚本。
- [x] 首批 ADS helper 脚本物理迁移到 `tools/ads/`，根目录保留兼容 wrapper。
- [ ] 在 ADS Python 环境中增加 profile/API smoke，不启动 FEM。

### P2-03 Scoring / Optimizer

- [x] 新增 `simads.scoring`，抽出 S 参数指标和 target profile evaluator。
- [x] 新增 `simads.optimizer`，抽出信赖域、EI/PI、可行概率和候选筛选。
- [x] 新增 `simads.optimizer.variants` 和 `tools/propose_filter_candidates.py`，支持 deterministic variants 配置校验与 plan 行展开。
- [x] 新增 `config/optimizer/i7_fr4_deterministic_variant_probe.json`，作为 legacy round 经验扫描迁移探针。
- [ ] round 专用脚本收敛为 optimizer 配置。

### P2-04 Device Plugin Contract 代码化

- [x] 新增 `simads.devices`。
- [x] 将 `filter.interdigital` 注册为第一个 plugin。
- [x] 后续 folded_sir、hilo_sir、stub 使用同一接口。

### P2-05 uv Editable 安装

- [x] 新增无副作用 editable/package 环境检查脚本。
- [x] 在 ADS 自动化 uv 环境中执行 editable 安装。
- [x] 记录 `pip freeze` 或 `uv pip list`。
- [x] 确认旧脚本和模块导入都能工作。

### P2-06 Workflow / Project Config 配置化

- [x] 新增 `simads.config.projects`，统一读取 `config/projects/<project_id>.json`。
- [x] 将 project root、plans、layouts、results、runs、reports、references 目录解析收敛为模块 API。
- [x] project config 支持 `active_sweep` 和 `sweeps`，登记 round/sweep 的 plan、layout、result、summary、device 和 target 默认值。
- [x] `tools/run_ads_filter_candidate.py` 的项目目录默认值改为通过 `ProjectConfig` 获取，缺失配置时保留旧 fallback。
- [x] `tools/run_ads_filter_sweep.py` 新增 `--sweep-id` 和 `--device-id`，并默认从 active sweep 或 project config 读取 device。
- [x] sweep runner 的 plan/out/results/summary/target/template/setup 默认值进一步从 active sweep 和 profile 推导，减少 round 专用硬编码。
- [x] 明确 project config 的 `ads` 块与 machine profile 的优先级策略：CLI > active sweep > current machine profile > project ads fallback。
- [x] active sweep 支持 `generator` 和 `optimizer` 配置，并让 surrogate 候选脚本读取 dataset、seed、输出目录和搜索参数默认值。
- [x] 新增 `config/round_script_migration.json` 和 `tools/check_round_script_migration.py`，迁移或归档 round 专用脚本前先做索引校验。
- [ ] 将剩余 `make_i7_fr4_round*.py` 等 round 专用脚本迁入 optimizer 配置或归档为 legacy。

---

## 当前风险和注意事项

| 风险 | 当前状态 | 处理建议 |
|---|---|---|
| `setup_dxf.opt` 缺失 | home profile 校验为 WARN。 | 当前导入脚本有 generated-DXF fallback；后续把 layer map 作为可选能力登记。 |
| ADS cell 大写目录编码 | home 模板 `BFP` 实际目录为 `%B%F%P`。 | profile 校验已支持大写编码识别。 |
| SIM 目录不是 git 仓库 | 无法用 git diff/status 做变更保护。 | 重要重构前建议初始化 git 或手工备份关键文件。 |
| run 目录仍处于兼容结构 | 当前 runner 写入 `results/<round>/runs/<run_id>`，目标结构是 `runs/<run_id>`。 | P1 迁移时保留 round summary/index，避免破坏历史结果引用。 |
| device plugin contract 未完全形式化 | registry 和基础 plugin 已有，但 score/report/context-aware optimizer 接口仍未冻结。 | 新增或细化 `DEVICE_PLUGIN_CONTRACT.md`，再扩 folded_sir、hilo_sir、stub。 |
| layout/source_map/DRC gate 扩展到多拓扑 | 交指 pipeline 已接入 `_layout.json` 机器校验；非交指分支尚需独立 pipeline 规则。 | 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立专用 pipeline config 和 layout gate。 |
| template 覆盖风险 | 代码 gate 已落地。 | 后续新增 ADS 删除/清理脚本必须复用 `src/simads.safety`。 |

## P0 完成定义

```text
[ ] 单候选成功 run 具备 run_manifest、artifact_manifest、state、score、log。
[ ] 单候选失败 run 具备 failed state、error_class、failed_step、log。
[ ] sweep_summary.csv 中每一行都有 status、run_id、profile_id、score_version。
[ ] 任意 score 行能追溯到 candidate、layout、profile、ADS version、target profile。
[ ] profile/API smoke test 能在 home 环境独立运行。
[ ] template cell 不会被普通候选流程覆盖。
[x] baseline 已 frozen，并有漂移复测规则。
```






















