# ADS 版图自动仿真项目框架独立评审与缺口分析

Status: Draft
Domain: ARCH
Canonical: `docs/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`
Related: `docs/ADS版图自动仿真项目框架设计.md`, `docs/PYTHON_SCRIPT_MANAGEMENT.md`, `docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档从独立评审角度审查 `ADS版图自动仿真项目框架设计.md`。目的不是继续扩写主框架，而是查漏补缺，指出当前框架要扩展成通用 ADS 版图自动仿真平台前必须补齐的契约、边界、验收门槛和工程治理能力。

## 1. 评审结论

当前框架方向正确：已经明确了版图优先、ADS API 能力验证、Python 脚本模块化、文档治理、公司/家里双环境和优化闭环。但它仍偏“设计说明”，还没有完全变成可执行、可验收、可长期演进的工程框架。

最主要缺陷是：缺少形式化契约和状态机。当前文档讲清了“应该做什么”，但对“输入输出长什么样、如何验证、失败后如何恢复、哪些文件可写、结果如何冻结、脚本如何兼容迁移”定义不足。对于单一滤波器用例可以靠人工经验维持；扩展到多器件、多轮优化、多环境和大量 FEM 作业后，会出现不可追溯、不可复现、误覆盖 ADS 工程、结果混淆和脚本分叉的问题。

独立评审结论：

| 等级 | 判断 |
|---|---|
| 架构方向 | 可继续沿用，不需要推倒重来。 |
| 平台成熟度 | 当前处于 POC 到工程化过渡阶段。 |
| 最大短板 | schema、manifest、状态机、写入安全、测试和验收 gate 不足。 |
| 近期策略 | 先补文档契约和验收门槛，再逐步模块化脚本。 |
| 是否立即改目录 | 不建议。应先补齐迁移前置条件。 |

## 2. 评审范围和方法

评审对象：

- 顶层框架：`docs/ADS版图自动仿真项目框架设计.md`
- 文档索引：`docs/README.md`
- ADS API 能力：`docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`
- Python 脚本管理：`docs/PYTHON_SCRIPT_MANAGEMENT.md`
- 当前可执行流程：`projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
- 当前 FR4 7 阶交指滤波器优化链路和历史结果

评审维度：

| 维度 | 关注点 |
|---|---|
| 需求边界 | 平台支持什么、不支持什么、验收标准是什么。 |
| 数据契约 | profile、plan、candidate、layout、run、result、score 是否有稳定 schema。 |
| ADS 操作 | workspace、library、cell、substrate、emSetup、RFPro、dataset 是否可控。 |
| 版图生成 | 从论文、公式、图片到几何对象是否有规则、约束和审查机制。 |
| 仿真编排 | 作业状态、重试、恢复、超时、license、并发和日志是否明确。 |
| 优化闭环 | 目标函数、约束、代理模型、基线保护和候选选择是否可复现。 |
| 代码治理 | Python 模块、CLI、测试、兼容迁移和复用边界是否清楚。 |
| 文档治理 | canonical、索引、进度、报告、冻结和引用关系是否完整。 |
| 风险控制 | 写入安全、误操作、人工介入、环境漂移和制造风险是否受控。 |

## 3. 总体评价

优点：

- 已经把平台核心闭环拆成参数化设计、版图生成、ADS 导入、EM 设置、仿真、导出、评分、优化和报告。
- 已经承认公司/家里环境差异是长期存在的配置问题，而不是临时路径替换问题。
- 已经把 ADS API 能力验证单独成章，方向正确。
- 已经把 Python 脚本管理单独成章，避免 `tools/*.py` 无限扩散。
- 已经把“论文、公式、图片到版图”的过程放到版图章节第一小节，符合真实流程。
- 已经意识到当前六轮搜索低效，需要从盲扫转为更有信息增益的优化算法。

主要缺陷：

- 缺少可机器校验的配置、参数、结果和评分 schema。
- 缺少 run manifest / artifact manifest，导致结果追溯仍依赖文件名和人工记忆。
- 缺少统一 run state machine，不利于处理 ADS 超时、仿真失败、半完成输出和断点恢复。
- 缺少写入安全模型，尤其是 ADS workspace/library/cell 被脚本修改时的保护策略。
- 缺少系统测试矩阵，尚未区分 host Python、ADS Python、无 ADS mock、真实 ADS smoke、长耗时 FEM。
- 缺少基线冻结、漂移检测和 release 流程，最佳模板容易在后续试验中被混淆。
- 对多器件扩展的 plugin/device contract 还不够严格，当前仍明显以滤波器为中心。

## 4. P0 缺口

P0 是平台化前必须补齐的缺口。没有这些内容，后续目录重构或脚本模块化会放大风险。

| 编号 | 缺口 | 当前问题 | 影响 | 建议修正 | 应更新文档 |
|---|---|---|---|---|---|
| P0-01 | 需求与非目标不够形式化 | 主框架有目标和边界，但没有明确 MVP、非目标、验收门槛。 | 容易把“滤波器优化脚本”误扩展成过大的平台，阶段验收不清。 | 新增 `ARCH_REQUIREMENTS_AND_ACCEPTANCE.md`，定义 MVP、长期目标、非目标、验收 gate。 | 主框架第 1 章，docs README。 |
| P0-02 | 配置 schema 缺失 | home/company profile 已存在，但字段、类型、默认值、必填项、验证规则未固定。 | 路径、library、substrate、python 解释器、license 环境容易漂移。 | 定义 `profiles.schema.json` 或 Markdown schema，启动前强制 validate。 | `ENV_ADS_HOME_COMPANY_PROFILES_DESIGN.md`，流程文档。 |
| P0-03 | run manifest 缺失 | 每次仿真没有统一记录 profile、git 状态、脚本版本、ADS 版本、候选参数、layout hash、emSetup 来源。 | 结果不可复现，无法判断两个 CSV/Touchstone 是否来自同一条件。 | 每个 run 输出 `run_manifest.json`，作为所有结果文件的根索引。 | 主框架第 7/10 章，新建 `data/DATA_RUN_MANIFEST_SCHEMA.md`。 |
| P0-04 | artifact manifest 缺失 | DXF、JSON、SVG、ADS cell、dataset、s2p、score.csv、报告之间靠命名关联。 | 文件重命名或批量扫参后容易串结果。 | 每个候选输出 `artifact_manifest.json`，记录 artifact 类型、路径、hash、生成时间和依赖。 | `DATA_ARTIFACT_MANIFEST_SCHEMA.md`。 |
| P0-05 | 写入安全模型不足 | 脚本会操作 ADS workspace/library/cell，但没有明确只读模板、候选 cell 命名、覆盖策略。 | 可能误改模板 cell、覆盖好结果或污染工作区。 | 建立 ADS workspace write policy：模板只读、候选 cell 必须带 run_id、覆盖需显式 `--force`、写前备份或 clone。 | 主框架第 5/8 章，流程文档。 |
| P0-06 | ADS API 能力没有验收级 smoke test | 已有能力矩阵，但未形成“每次环境切换必须跑”的最小脚本集合和通过标准。 | 家里/公司环境切换时问题发现太晚，常表现为长时间超时。 | 建立 `ENV_ADS_API_SMOKE_TEST_PLAN.md`，分 import、workspace open、library inspect、layout create、substrate inspect、dataset read 六级。 | API 能力矩阵，流程文档。 |
| P0-07 | 仿真状态机缺失 | 当前流程是线性脚本链，失败点和恢复点不够标准化。 | FEM 超时、dataset 未导出、S 参数缺失时难以自动恢复。 | 定义 run states：planned、layout_generated、ads_imported、emsetup_ready、sim_running、dataset_exported、scored、reported、failed。 | `flow/FLOW_RUN_STATE_MACHINE.md`。 |
| P0-08 | 幂等与 resume 策略缺失 | 脚本重复运行时，哪些步骤跳过、覆盖、重跑没有统一规则。 | 批量优化成本高，重复仿真浪费时间，半成品难处理。 | 每步检查 manifest 和 hash；相同输入默认复用，参数或环境变更必须生成新 run。 | 主框架第 7 章，流程手册。 |
| P0-09 | 数据 schema/versioning 不足 | `params.json`、`source_map.json`、`score.csv`、`sweep_summary.csv`、训练集 CSV 没有正式字段版本。 | 优化脚本很快会被历史字段拖住，新增指标后无法兼容旧数据。 | 建立 `data/DATA_SCHEMA_REGISTRY.md`，每类文件定义 schema_version、字段、单位、允许空值。 | README，优化文档。 |
| P0-10 | 测试策略不完整 | 现在主要靠真实运行 ADS 发现问题。 | 调整脚本时风险大，失败反馈慢。 | 建立测试金字塔：纯 Python 单元测试、几何 golden、schema validate、ADS API smoke、短 FEM、长 FEM。 | `test/TEST_STRATEGY.md`，Python 管理文档。 |

## 5. P1 缺口

P1 会影响长期效率、结果质量和多器件扩展，但可以在 P0 后逐步补齐。

| 编号 | 缺口 | 当前问题 | 影响 | 建议修正 | 应更新文档 |
|---|---|---|---|---|---|
| P1-01 | 目标函数治理不足 | 当前滤波器评分已存在，但还没有通用 target profile schema。 | 换成耦合器、功分器、天线后评分逻辑容易硬编码。 | 定义 `target_profile.json`：频段、指标、硬约束、软权重、采样点、惩罚函数。 | `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`。 |
| P1-02 | 基线冻结和漂移检测不足 | 已知初始模板目前最好，但缺少冻结状态和周期复测规则。 | 后续搜索可能误判“变好/变差”，无法区分算法改进和环境漂移。 | 为 baseline 输出 frozen manifest，环境变更后先复跑 baseline 并比较容差。 | `result/RESULT_BASELINE_FREEZE_POLICY.md`。 |
| P1-03 | 优化实验设计不足 | 已提出代理模型，但没有明确候选生成、探索/开发比例、信赖域收缩规则。 | 可能继续出现多轮搜索不如初版。 | 定义 optimizer policy：DoE 初始集、局部信赖域、EI/PI、约束可行概率、失败样本处理。 | `OPT_SURROGATE_EI_DESIGN.md`。 |
| P1-04 | 制造容差和鲁棒优化未成为 gate | FR4、铜厚、蚀刻误差、介电常数偏差会影响 6-8 GHz 性能。 | 单点最优可能不可制造或实物偏移严重。 | 在候选入围后强制跑 tolerance sweep：线宽、间距、介电常数、厚度、铜厚。 | `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`。 |
| P1-05 | 版图重建缺少审查表 | 已有规则方向，但还缺“从图到版图”的人工审查 checklist。 | 论文图片转参数化版图时容易漏掉 via、地、端口、开路端、耦合间距。 | 增加 layout reconstruction checklist：拓扑、层、参考地、电流路径、端口、边界、单位、约束。 | 主框架 9.1，`layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`。 |
| P1-06 | 人工 ADS GUI 介入不可追踪 | 某些步骤可能需要手动修补，但没有记录格式。 | 自动化结果和人工修补混在一起，复现困难。 | 每次 GUI 操作写 `manual_intervention.md/json`：操作者、时间、对象、动作、原因、截图。 | `flow/FLOW_MANUAL_INTERVENTION_LOG.md`。 |
| P1-07 | 日志和错误分类不足 | 当前强调加 log，但还没有统一事件字段和错误码。 | 排查超时时只能看长日志，不利于自动统计。 | 定义 structured log：event、run_id、candidate_id、stage、duration、status、error_code。 | `FLOW_ADS_ERROR_HANDLING_PLAYBOOK.md`。 |
| P1-08 | 并发、队列和 license 策略不足 | RFPro/FEM 可能受 license、CPU、内存、ADS workspace 锁限制。 | 批量搜索时容易互相抢资源或卡死。 | 建立 job queue policy：最大并发、license probe、超时、退避、锁文件、优先级。 | `flow/FLOW_JOB_SCHEDULING_POLICY.md`。 |
| P1-09 | 多器件 plugin contract 不足 | 当前对象模型有扩展方向，但没有严格接口。 | 新器件会把滤波器专用字段带入通用框架。 | 定义 device plugin contract：parameters、layout_generator、constraints、ports、target_profiles、report_sections。 | 主框架第 4 章，`DEVICE_PLUGIN_CONTRACT.md`。 |
| P1-10 | 报告冻结和发布流程不足 | HTML/PDF 报告已有，但没有说明何时可作为正式结论。 | 报告可能引用未冻结数据或旧图。 | 报告必须引用 run manifest 和 dataset hash；发布前过 schema、链接、图片、公式检查。 | `REPORT_RELEASE_POLICY.md`。 |

## 6. P2 缺口

P2 属于成熟度增强，不阻塞当前框架落地。

| 编号 | 缺口 | 当前问题 | 建议修正 |
|---|---|---|---|
| P2-01 | GUI/Notebook 探索层未定义 | 当前以 CLI 和文档为主。 | 后续可增加只读 dashboard，用于看候选、曲线、Pareto 和 artifact。 |
| P2-02 | 参数空间可视化不足 | 训练集有数据，但未形成固定可视化。 | 增加 scatter matrix、特征重要性、局部敏感度和失败区域图。 |
| P2-03 | 文档 lint 不足 | README 规则已有，但没有自动检查。 | 增加 docs lint：元数据、canonical、related、索引登记、过期链接。 |
| P2-04 | 示例项目不足 | 当前只有滤波器主用例。 | 后续增加最小耦合线、50 ohm 传输线、简单匹配网络作为 smoke 示例。 |
| P2-05 | 版本发布节奏未定义 | 没有平台版本号。 | 可在完成 P0 后引入 `SIM_ADS_AUTOMATION_VERSION`。 |

## 7. 维度评审

### 7.1 需求和范围

主框架已经有目标和短期边界，但缺少可验收定义。建议拆成三层：

| 层级 | 定义 |
|---|---|
| MVP | 能在 home/company 两套环境中稳定跑通一个候选的 layout -> ADS -> FEM -> s2p -> score。 |
| V1 | 能批量运行候选，支持 resume、manifest、baseline 复测和报告输出。 |
| V2 | 支持多器件 plugin、代理优化、队列调度和鲁棒优化。 |

非目标也要明确：短期不做 ADS 工程大迁移、不做 GUI 平台、不追求替代 ADS 内部建模器、不把所有论文结构自动识别完全自动化。

### 7.2 数据契约

建议把所有关键文件纳入 schema registry：

| 文件 | 必须字段 |
|---|---|
| `profile.yaml/json` | profile_id、ads_root、workspace_path、library、template_cell、substrate、python_host、python_ads、os、notes。 |
| `plan.json` | plan_id、device_type、target_profile_id、parameter_space、candidate_source、created_at。 |
| `candidate.json/csv` | candidate_id、plan_id、schema_version、参数字段、单位、父候选、生成算法。 |
| `layout.json` | layout_id、candidate_id、units、layers、ports、shapes、vias、source_map_hash。 |
| `run_manifest.json` | run_id、candidate_id、profile_id、ads_version、scripts、git_ref、input_hash、artifact_manifest。 |
| `score.csv/json` | score_id、run_id、target_profile_id、metrics、constraints、objective_value、pass_fail。 |
| `training_dataset.csv` | dataset_id、source_runs、feature_schema、metric_schema、excluded_reason、created_at。 |

关键要求：每个 schema 必须有 `schema_version`，每个物理量必须有单位，所有评分必须能追溯到 target profile。

### 7.3 ADS 环境和 API

当前 API 能力矩阵已经建立，但还需要从“文档清单”升级为“能力认证”。建议每个 profile 都有如下命令级 gate：

| Gate | 验证内容 | 失败处理 |
|---|---|---|
| ADS-PY-01 | ADS Python 可启动，能 import `keysight.ads` 相关包。 | 停止流程，提示路径和 PYTHONPATH。 |
| ADS-WS-01 | 能打开 workspace，读取 library/cell/substrate。 | 停止流程，检查 profile。 |
| ADS-LAY-01 | 能创建临时 cell，写入矩形/端口，然后删除临时对象。 | 禁止进入批量导入。 |
| ADS-EM-01 | 能读取或克隆模板 emSetup。 | 禁止启动 FEM。 |
| ADS-DS-01 | 能读取一个已知 dataset 或 Touchstone。 | 禁止评分。 |

这些 gate 应该在真正仿真前完成，因为它们耗时短，可以快速定位环境变量、路径、library 和 API 问题。

### 7.4 版图生成

版图是平台最前端，必须先稳定。建议把版图生成拆成四层：

| 层 | 作用 |
|---|---|
| Intent | 从论文/公式/图片提取拓扑、阶数、端口、层、谐振器、耦合关系和目标频段。 |
| Parameter | 把长度、宽度、间距、stub、via、tap、feed、ground clearance 转成带单位的参数。 |
| Geometry | 生成 rect、polygon、path、via、port、keepout、boundary 等几何对象。 |
| ADS Binding | 把几何对象映射到 ADS layer、purpose、cell、pin/port、substrate 和 EM setup。 |

版图重建不是单纯描图，应强制满足：拓扑等价、电气路径闭合、端口参考明确、层叠匹配、最小线宽/间距满足制造限制、via 与地连接明确、边界和空气盒合理、单位和坐标原点稳定。

### 7.5 仿真编排

当前线性流程需要变成状态机。每个 stage 都应满足：输入已校验、输出可检测、失败可分类、重跑可决定。

建议每个 run 目录包含：

```text
run_manifest.json
artifact_manifest.json
logs/
layout/
ads/
dataset/
score/
report/
state.json
```

`state.json` 记录当前 stage、开始时间、结束时间、耗时、重试次数、错误码和下一步建议。重复运行时先读 state 和 manifest，不盲目覆盖已有输出。

### 7.6 优化算法

当前“六轮搜索不如初版”的结论说明搜索空间利用效率不足。框架层面必须明确：

- 初版 baseline 是受保护参考点，不允许被普通候选覆盖。
- 每轮优化必须说明探索/开发比例。
- 候选必须记录来源：人工、网格、局部扰动、代理模型、EI、可行性修复。
- 负样本也必须进入训练集，但要标记失败原因。
- 排名不能只看单一综合分，应同时看硬约束、目标余量、Pareto、鲁棒性和回损风险。

对当前 FR4 7 阶交指滤波器，下一轮不应继续大范围盲扫，而应围绕 baseline 做小信赖域局部搜索，并把 S11/S22 作为局部改进目标，同时对 S21 通带和 5 GHz 阻带设置硬约束保护。

### 7.7 Python 脚本和模块

`PYTHON_SCRIPT_MANAGEMENT.md` 的方向正确，但还需要明确兼容迁移策略：

| 类型 | 规则 |
|---|---|
| 旧 CLI | 短期保留入口，内部调用新模块。 |
| 新模块 | 只放可复用能力，不读取全局路径。 |
| profile | 只通过配置传入，不在模块内写死。 |
| ADS Python 脚本 | 尽量薄封装，复杂逻辑留在 host Python。 |
| 测试 | 纯 Python 模块必须能在无 ADS 环境测试。 |

推荐增加 `scripts/` 与 `simads/` 的迁移表，但在未完成 P0 schema 前不要急着移动文件。

### 7.8 测试和验收

建议建立最小测试矩阵：

| 层级 | 内容 | 触发时机 |
|---|---|---|
| Unit | 参数解析、几何计算、评分函数、schema validate。 | 每次脚本修改。 |
| Golden | 同一参数生成的 DXF/layout JSON hash 或几何摘要稳定。 | 版图生成修改。 |
| ADS Smoke | ADS import、workspace、layout、substrate、dataset 读取。 | 环境切换或 ADS 相关脚本修改。 |
| Short FEM | 一个最小结构短仿真。 | emSetup/RFPro 脚本修改。 |
| Full Run | 当前 baseline 完整复跑。 | 发布候选、迁移目录、升级 ADS 后。 |

### 7.9 文档治理

README 已有入口和新增规则，但还应增加“文档状态”和“冻结结果”的概念：

| 状态 | 含义 |
|---|---|
| Draft | 设计中，不能作为自动化实现依据。 |
| Active | 当前依据，可被脚本和流程引用。 |
| Frozen | 历史基线或正式报告，只补勘误。 |
| Deprecated | 已被替代，但保留迁移说明。 |

所有正式结论报告应引用具体 run manifest、score schema 和 dataset hash。

## 8. 建议新增或调整的文档

优先新增：

| 优先级 | 文档 | 目的 |
|---|---|---|
| P0 | `ARCH_REQUIREMENTS_AND_ACCEPTANCE.md` | 平台需求、非目标、MVP/V1/V2 验收。 |
| P0 | `data/DATA_SCHEMA_REGISTRY.md` | 所有 JSON/CSV/Touchstone/报告输入输出契约。 |
| P0 | `data/DATA_RUN_MANIFEST_SCHEMA.md` | run_id、profile、candidate、artifact、环境、脚本版本。 |
| P0 | `flow/FLOW_RUN_STATE_MACHINE.md` | 仿真阶段、状态、失败、resume、幂等策略。 |
| P0 | `test/TEST_STRATEGY.md` | 单元测试、golden、ADS smoke、短 FEM、完整复跑。 |
| P1 | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` | 论文/公式/图片到版图的审查清单。 |
| P1 | `flow/FLOW_JOB_SCHEDULING_POLICY.md` | license、并发、队列、锁和超时策略。 |
| P1 | `result/RESULT_BASELINE_FREEZE_POLICY.md` | 初始模板和最佳候选的冻结、复测和漂移检测。 |
| P1 | `DEVICE_PLUGIN_CONTRACT.md` | 多器件扩展接口。 |
| P1 | `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` | 制造容差、材料漂移和鲁棒优化。 |

不建议立即新增太多执行脚本；应先把 P0 文档契约固化，避免脚本按不稳定接口开发。

## 9. 建议回填到主框架的内容

主框架不需要大改，但应补入以下反向引用和原则：

| 位置 | 建议补充 |
|---|---|
| 第 1 章 | 增加独立评审文档链接，并说明平台化前必须通过 P0 gate。 |
| 第 3 章 | 增加 schema registry、run manifest、state machine 作为目标架构核心。 |
| 第 5 章 | 增加 ADS API smoke test gate，profile 切换必须先验证。 |
| 第 7 章 | 将线性数据流升级为带 manifest 和 state 的可恢复流程。 |
| 第 8 章 | 增加 ADS workspace 写入安全、人工 GUI 介入记录和 destructive write policy。 |
| 第 9 章 | 补入版图重建 checklist 和制造约束 gate。 |
| 第 10 章 | 增加 Draft/Active/Frozen/Deprecated 文档状态和正式报告冻结规则。 |

## 10. 下一步执行清单

建议按以下顺序补齐，不急着移动目录：

1. 新增 `data/DATA_SCHEMA_REGISTRY.md`，先定义 profile、candidate、layout、run、score、training dataset 的最小字段。
2. 新增 `flow/FLOW_RUN_STATE_MACHINE.md`，把现有 ADS 自动仿真流程映射到状态机和 resume 规则。
3. 新增 `test/TEST_STRATEGY.md`，把 home 环境 ADS smoke test 和 baseline full run 作为环境切换 gate。
4. 回填主框架第 3、7、8、10 章中的 manifest、state、写入安全、文档状态原则。
5. 冻结当前 FR4 7 阶交指滤波器 baseline，建立 `result/RESULT_BASELINE_FREEZE_POLICY.md`。
6. 再开始 Python 模块化迁移，把旧 CLI 改成调用 `simads.*` 模块。

短期验收标准：

| 验收项 | 通过标准 |
|---|---|
| 文档入口 | README 能快速找到框架、评审、API、Python 管理和流程文档。 |
| 环境切换 | home/company profile 字段完整，并有 smoke test 通过记录。 |
| 单候选复跑 | 一个候选能产出 run manifest、artifact manifest、state、score。 |
| 失败恢复 | 中断后能从 state 判断从哪一步恢复，不重复跑已完成 FEM。 |
| 基线保护 | 初始模板和当前最佳候选有 frozen 记录，后续候选只能引用不能覆盖。 |
| 结果追溯 | 任意报告图、score 和 s2p 都能追到 candidate、layout、profile 和 ADS 版本。 |

## 11. 独立评审判定

当前框架可以作为顶层方向文档继续使用，但在真正扩展为 ADS 版图自动仿真项目框架前，至少应完成 P0-01 到 P0-10。最优先的不是重排目录，而是把数据契约、运行状态、写入安全和测试门槛补齐。完成这些后，再做目录迁移和模块化，风险会显著降低。

