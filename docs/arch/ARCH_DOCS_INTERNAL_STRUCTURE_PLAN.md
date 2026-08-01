# Docs 内部架构与迁移规划

Status: Active
Domain: ARCH
Canonical: `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
Related: `docs/README.md`, `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档规划 `docs/` 的内部目录架构。目标是把当前平铺文档逐步整理为可导航、可迁移、可长期维护的分层文档库，同时保护已有引用和历史记录。

## 1. 结论

当前 `docs/` 根目录已经包含 28 个正式文件，继续平铺会带来三个问题：

| 问题 | 影响 |
|---|---|
| 查找依赖文件名前缀 | 需要记住 `ARCH_`、`FLOW_`、中文标题和项目分支文件名。 |
| canonical 和进度记录混放 | 顶层架构、任务流水、结果索引和理论分析在同一层，阅读路径不清晰。 |
| 后续迁移成本上升 | 文档越多，后续一次性移动越容易打断 README、Related 和报告引用。 |

推荐方案：

```text
先逻辑分组
  -> 新增目录架构规划和迁移表
  -> 先迁低风险辅助文档
  -> 再迁 canonical 文档
  -> 最后清理根目录冗余文件
```

当前已完成 Phase 1、Phase 2、Phase 3 和 Phase 4 的物理迁移，根目录仅保留 `README.md`。退役的旧路径说明和兼容 CSV 已归档到 `docs/archive/`；新增正式文档必须直接进入目标目录，并在 README 与迁移表中登记。

## 2. 目标目录结构

长期目标：

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

目录职责：

| 目录 | 职责 | 典型文档 |
|---|---|---|
| `docs/` | 总入口、子目录索引和退役材料归档。 | `README.md`。 |
| `docs/arch/` | 顶层框架、目录治理、评审、迁移、重构 TODO 和任务记录。 | framework、review、todo、progress、asset migration。 |
| `docs/data/` | schema、manifest、字段契约、数据版本。 | schema registry、run manifest schema。 |
| `docs/env/` | ADS、Python、uv、license、home/company profile 和 API 能力。 | company uv、ADS API capability。 |
| `docs/flow/` | 自动化流程、状态机、调度、写入安全、人工介入。 | run state、workspace policy、job scheduling。 |
| `docs/layout/` | 版图重建、几何规则、DRC、layer map、端口/via 审查。 | layout reconstruction checklist。 |
| `docs/devices/` | 器件拓扑和分支设计规则。 | interdigital、folded SIR、hilo SIR、stub。 |
| `docs/opt/` | 目标函数、优化算法、round 脚本迁移、代理模型。 | objective、surrogate、round migration。 |
| `docs/result/` | round 结果索引、baseline freeze、漂移复测。 | round index、baseline policy。 |
| `docs/mfg/` | 制造能力、容差、材料漂移和发布前鲁棒性 gate。 | tolerance robustness。 |
| `docs/report/` | HTML/PDF 模板、报告发布 gate、打印导出规则。 | report playbook。 |
| `docs/test/` | 测试策略、smoke、golden、baseline full run。 | test strategy。 |
| `docs/archive/` | 已废弃、旧版本或只保留追溯价值的文档。 | deprecated docs、旧迁移说明、兼容快照。 |

项目专用流程和结果说明优先放在：

```text
projects/<project_id>/docs/
```

全局 `docs/` 只保留平台级规则、跨项目复用方法和正式治理文档。

## 3. 文档树和分支串联规则

文档架构不仅用于存放文件，还必须能串联完整项目。`docs/README.md` 是唯一总入口，应提供一棵稳定的阅读树：

```text
平台总纲
  -> 环境和工程边界
  -> 自动化闭环
  -> 数据契约和可追溯
  -> 版图和器件分支
  -> 优化、制造和测试
  -> 结果和报告
```

每个器件或项目分支必须满足以下最小链路：

| 链路节点 | 必须回答的问题 | 典型位置 |
|---|---|---|
| Branch entry | 这个分支是什么拓扑、目标和约束。 | `docs/devices/` 或 `projects/<project_id>/docs/` |
| Layout source | 版图来自论文、公式、截图、手工设计还是参数化生成。 | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`、分支文档 |
| Config binding | 使用哪个 project、profile、target、substrate。 | `config/projects/`、`config/ads_profiles.json`、`config/targets/` |
| Automation flow | 怎么生成版图、导入 ADS、放端口、复制 emSetup、仿真、导出、评分。 | 项目 `docs/ADS自动仿真流程说明.md`、`FLOW_*.md` |
| Data trace | plan、layout、result、run manifest、score 在哪里。 | `projects/<project_id>/plans/layouts/results/runs/` |
| Optimization trace | 每轮为什么这么改，候选来自人工、扫参还是优化器。 | `OPT_*.md`、`RESULT_*.md`、项目 results |
| Decision/report | 哪个候选推荐、为什么、制造风险是什么。 | `RESULT_*.md`、`REPORT_*.md`、项目 reports |

新增分支时必须在 README 的“项目阅读树”中登记入口；如果分支还处于探索状态，至少登记为 Draft，并说明数据和结果是否齐全。

## 4. 根目录保留规则

迁移完成后，`docs/` 根目录只保留：

| 文件 | 原因 |
|---|---|
| `README.md` | 文档总入口和导航。 |

根目录不再新增普通主题文档。新增文档应直接进入目标领域目录；退役旧路径说明、兼容 CSV 和历史快照统一进入 `docs/archive/`。

## 5. 迁移阶段

### Phase 0 - 规划冻结

目标：冻结目录架构和迁移规则，不移动文件。

- [x] 新增本规划文档。
- [x] 在 README 增加目标目录结构和迁移入口。
- [x] 在 TODO 中登记 docs 物理迁移任务。
- [x] 建立迁移映射表模板：`ARCH_DOCS_MIGRATION_20260801.csv`。

### Phase 1 - 低风险文档迁移

目标：迁移不会被脚本直接读取的辅助文档。

当前状态：第一批已迁移 `ENV_`、`MFG_`、`REPORT_`、`TEST_`、`LAYOUT_` 文档到目标目录，旧路径说明已归档。

优先迁移：

```text
ENV_*.md
REPORT_*.md
MFG_*.md
TEST_*.md
LAYOUT_*.md
```

规则：

- 每移动一个文件，更新 README、Related、Canonical。
- 旧路径说明先归档，再从 README 和历史引用中逐步移除。
- 本阶段不移动主框架、TODO、任务进度和 schema。

### Phase 2 - 数据和流程文档迁移

目标：迁移可被脚本、流程和分支说明引用的核心规范。

当前状态：已迁移 `DATA_`、`FLOW_`、`OPT_`、`RESULT_` 与器件分支文档到 `docs/data/`、`docs/flow/`、`docs/opt/`、`docs/result/`、`docs/devices/`，旧路径说明已归档；README、Related 和主文档引用已做第一轮更新。

迁移对象：

```text
DATA_*.md
FLOW_*.md
OPT_*.md
RESULT_*.md
FR4高低阻抗带通滤波器优化TODO.md
FR4折叠SIR带通滤波器分支.md
交指带通滤波器回波损耗影响因素.md
```

规则：

- 先运行 `rg` 查引用。
- 更新项目流程文档、README 和主框架。
- 对 schema、manifest、state machine 等核心文档的历史说明至少保留一个完整优化周期后再归档。

### Phase 3 - 架构文档迁移

目标：迁移最高频入口和重构记录。

迁移对象：

```text
ADS版图自动仿真项目框架设计.md
ARCH_*.md
PYTHON_SCRIPT_MANAGEMENT.md
```

规则：

- 主框架迁移前必须冻结路径映射。
- `README.md` 仍保留在根目录。
- `ARCH_REFACTOR_TASK_PROGRESS.md` 可考虑拆分为年度或阶段日志，但旧文件保留总索引。

### Phase 4 - 清理旧路径

目标：让 `docs/` 根目录只保留 `README.md`。

条件：

- 连续一个完整优化周期没有旧路径引用。
- README、项目文档、报告模板和脚本中不再引用旧路径。
- `rg` 检查无旧路径直接引用。

## 6. 当前文件目标归属

| 当前 canonical 文件 | 目标目录 | 迁移优先级 |
|---|---|---|
| `README.md` | `docs/README.md` | 保留根目录 |
| `arch/ADS版图自动仿真项目框架设计.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_ADS_ASSET_MIGRATION_20260801.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_DIRECTORY_GOVERNANCE.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_REFACTOR_TASK_PROGRESS.md` | `docs/arch/` | Phase 3 completed |
| `arch/ARCH_REFACTOR_TODO.md` | `docs/arch/` | Phase 3 completed |
| `arch/PYTHON_SCRIPT_MANAGEMENT.md` | `docs/arch/` | Phase 3 completed |
| `data/DATA_RUN_MANIFEST_SCHEMA.md` | `docs/data/` | Phase 2 |
| `data/DATA_SCHEMA_REGISTRY.md` | `docs/data/` | Phase 2 |
| `env/ENV_ADS_API_CAPABILITY_MATRIX.md` | `docs/env/` | Phase 1 |
| `env/ENV_UV_COMPANY_20260801.md` | `docs/env/` | Phase 1 |
| `flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md` | `docs/flow/` | Phase 2 |
| `flow/FLOW_JOB_SCHEDULING_POLICY.md` | `docs/flow/` | Phase 2 |
| `flow/FLOW_MANUAL_INTERVENTION_LOG.md` | `docs/flow/` | Phase 2 |
| `flow/FLOW_RUN_STATE_MACHINE.md` | `docs/flow/` | Phase 2 |
| `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` | `docs/layout/` | Phase 1 |
| `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md` | `docs/opt/` | Phase 2 |
| `opt/ROUND_SCRIPT_MIGRATION_PLAN.md` | `docs/opt/` | Phase 2 |
| `opt/FR4交指滤波器搜索算法改进方案.md` | `docs/opt/` | Phase 2 |
| `result/RESULT_BASELINE_FREEZE_POLICY.md` | `docs/result/` | Phase 2 |
| `result/RESULT_I7_FR4_ROUND_INDEX.md` | `docs/result/` | Phase 2 |
| `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` | `docs/mfg/` | Phase 1 |
| `report/REPORT_TEMPLATE_PLAYBOOK.md` | `docs/report/` | Phase 1 |
| `test/TEST_STRATEGY.md` | `docs/test/` | Phase 1 |
| `devices/FR4高低阻抗带通滤波器优化TODO.md` | `docs/devices/` 或项目 docs | Phase 2 |
| `devices/FR4折叠SIR带通滤波器分支.md` | `docs/devices/` 或项目 docs | Phase 2 |
| `devices/交指带通滤波器回波损耗影响因素.md` | `docs/devices/` 或项目 docs | Phase 2 |

器件分支文档如果只服务 `bfp_6_8g_i7_fr4`，最终应迁入 `projects/bfp_6_8g_i7_fr4/docs/`；如果沉淀为通用拓扑规则，则迁入 `docs/devices/`。

## 7. 迁移映射表字段

迁移时新增：

```text
docs/arch/ARCH_DOCS_MIGRATION_<YYYYMMDD>.csv
```

字段：

| 字段 | 说明 |
|---|---|
| `old_path` | 迁移前路径。 |
| `new_path` | 迁移后路径。 |
| `doc_domain` | 文档领域。 |
| `status` | moved/stubbed/deprecated/kept/archived。 |
| `canonical_updated` | 是否更新 Canonical 字段。 |
| `readme_updated` | 是否更新 README 索引。 |
| `related_updated` | 是否更新 Related 反向引用。 |
| `notes` | 特殊说明。 |

## 8. 旧路径 Stub 规则

旧路径说明使用统一格式：

```markdown
# 文档已迁移

Status: Deprecated
Domain: <DOMAIN>
Canonical: `docs/<domain>/<file>.md`
Related: `docs/README.md`, `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
Last updated: YYYY-MM-DD
Owner: ADS Automation

本文档已迁移到 `docs/<domain>/<file>.md`。请以后维护新路径。
```

说明不复制正文，避免新旧两份内容分叉。

## 9. 验收 Gate

每批 docs 迁移后必须检查：

```powershell
rg -n "old_file_name|old_path" E:\OneDrive\4.Code\SIM
```

验收条件：

- README 中能找到新路径。
- README 的“项目阅读树”能串联到该文档所属分支。
- 新文件 `Canonical` 指向新路径。
- 旧路径说明和兼容快照均已归档。
- Related 链接不指向不存在文件。
- 项目流程文档和报告模板没有断链。
- 任务记录写入 `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`。

## 10. 下一步

建议下一步进入 Phase 3 准备：

1. 先冻结 Phase 3 的架构文档迁移顺序，优先评估 `ARCH_REFACTOR_TASK_PROGRESS.md` 是否需要拆成阶段日志。
2. 迁移 `ARCH_*.md` 和 `PYTHON_SCRIPT_MANAGEMENT.md` 前，先检查 README、任务记录、主框架和项目文档中的旧根目录引用。
3. 每批迁移后更新 README、Canonical、Related 和 `ARCH_DOCS_MIGRATION_20260801.csv`，并把旧路径说明归档。
4. Phase 4 已完成根目录清理，后续只维护 `archive/` 中的退役材料。
