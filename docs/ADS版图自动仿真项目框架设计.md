# ADS 版图自动仿真项目框架设计

Status: Active
Domain: ARCH
Canonical: `docs/ADS版图自动仿真项目框架设计.md`
Related: `docs/README.md`, `docs/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`, `docs/ARCH_ADS_ASSET_MIGRATION_20260801.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`, `docs/opt/FR4交指滤波器搜索算法改进方案.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档是 ADS 版图自动仿真项目的顶层框架文档。它是当前 ADS 版图自动仿真平台的有效架构边界。后续目录、脚本、配置、结果和报告必须按本文档定义的项目结构、数据契约、流程、文档和工程治理规则推进。

独立评审和缺口清单见 `docs/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`。后续平台化、目录迁移和脚本模块化前，应优先完成该评审文档中的 P0 gate。

当前项目根目录：

```text
E:\OneDrive\4.Code\SIM
```

公司/家里两套 ADS 环境以 `config/ads_profiles.json` 为唯一机器可读来源。本文档中的绝对路径用于说明当前已知环境，不作为脚本默认值硬编码依据。

## 1. 总览

### 1.1 项目目标

项目目标是建立一套可持续扩展的 ADS 版图自动仿真平台，核心闭环为：

```text
参数化设计
  -> 版图生成
  -> ADS Layout 导入
  -> EM Setup 复用/修补
  -> RFPro/FEM 仿真
  -> S 参数导出
  -> 指标评分
  -> 候选优化
  -> 报告和决策沉淀
```

当前 6-8 GHz FR4 7 阶交指滤波器是第一条验证链路。后续平台应能扩展到：

- 交指、梳状、发夹、折叠 SIR、高低阻抗等滤波器；
- 匹配网络；
- 功分器、耦合器、巴伦；
- 天线、馈电结构和其它微波版图；
- 任意可以参数化生成 Layout 并由 ADS EM/FEM 验证的结构。

### 1.2 设计原则

- 当前可运行流程优先，不为追求目录美观破坏 ADS 自动化闭环。
- 环境配置、器件建模、版图生成、ADS 操作、仿真评分、优化算法和报告输出分层隔离。
- 所有结果必须可追溯到 profile、substrate、target profile、plan、candidate 和评分版本。
- 公司/家里两套 ADS 环境长期并存，不允许把路径写死在核心逻辑里。
- 优化算法必须复用历史仿真数据，避免每轮从零开始试错。
- 文档管理是框架的一部分，所有设计、结果、迁移和决策必须有 canonical 入口。

### 1.3 当前边界

当前边界以新架构为准，不再把旧 `ADS\` 目录作为项目资产根。旧 `ADS\` 同时混放 plan、layout、result、reference 和流程文档，已经不适合作为可扩展框架边界。

当前有效项目资产根目录：

```text
projects\bfp_6_8g_i7_fr4\
```

目录职责：

```text
plans/      候选计划 CSV。
layouts/    DXF/SVG/params/DRC/source map 等版图产物。
results/    RFPro/FEM 导出、score、summary、training dataset、prediction report。
runs/       后续 run_manifest、artifact_manifest、state、logs 的标准输出根。
reports/    HTML/PDF 报告和报告资产。
references/ 论文、文章分析、图片和外部参考。
docs/       项目专用流程说明和项目级补充文档。
```

旧路径迁移记录见 `docs/ARCH_ADS_ASSET_MIGRATION_20260801.md` 和 `docs/ARCH_ADS_ASSET_MIGRATION_20260801.csv`。

短期仍保留旧 `tools/*.py` CLI 兼容入口，但默认路径和新增产物必须逐步切到 `projects/<project_id>/...`。ADS workspace 仍是外部工程目录，不纳入本代码仓库移动范围。

### 1.4 平台化需求、非目标和验收阶段

当前框架必须按阶段验收，避免把一次滤波器优化任务直接扩展成不可控的大平台。

阶段定义：

| 阶段 | 范围 | 通过标准 |
|---|---|---|
| MVP | 单候选闭环 | 在 home/company 任一 profile 中，稳定完成 `layout -> ADS import -> emSetup -> RFPro/FEM -> export -> score`，并生成日志和结果。 |
| V1 | 批量优化闭环 | 支持 round 级批量候选、run manifest、artifact manifest、断点续跑、baseline repeat、训练集回填和报告输出。 |
| V2 | 通用 ADS 版图仿真平台 | 支持多器件 plugin、通用 target profile、队列调度、代理优化、容差扫描、冻结发布和结果索引。 |

短期非目标：

- 不自动重建或迁移正式 ADS workspace。
- 不替代 ADS GUI 的最终人工复核。
- 不承诺把任意论文图片完全自动识别为可仿真版图。
- 不在样本量不足时把神经网络作为主优化器。
- 不把公司/家里环境强行合并为一套路径配置。

平台化前置 gate：

```text
P0-GATE-01 profile schema 和启动校验存在。
P0-GATE-02 run_manifest.json 和 artifact_manifest.json 能随单候选输出。
P0-GATE-03 run state machine 能判断当前阶段、失败点和 resume 入口。
P0-GATE-04 ADS workspace 写入策略能保护 template cell 和历史结果。
P0-GATE-05 ADS API smoke test 能在 home/company profile 上独立运行。
P0-GATE-06 关键 CSV/JSON schema 有版本号、单位和必填字段。
P0-GATE-07 纯 Python 测试、几何 golden、ADS smoke 和 baseline full run 有明确触发条件。
```

## 2. 当前项目状态

### 2.1 当前目录

当前有效结构：

```text
E:\OneDrive\4.Code\SIM
├─ config\
│  ├─ ads_profiles.json
│  ├─ projects\bfp_6_8g_i7_fr4.json
│  └─ targets\fr4_25db_rl6.json
├─ projects\
│  └─ bfp_6_8g_i7_fr4\
│     ├─ plans\
│     ├─ layouts\
│     ├─ results\
│     ├─ runs\
│     ├─ reports\
│     ├─ references\
│     ├─ docs\
│     └─ notes\
├─ docs\
├─ src\simads\
├─ tools\
├─ ADS\README.md
└─ ...
```

目录职责：

| 目录 | 当前职责 |
|---|---|
| `config\` | profile、target profile、project config 的机器可读入口。 |
| `projects\bfp_6_8g_i7_fr4\plans\` | 候选 CSV、round plan、baseline plan。 |
| `projects\bfp_6_8g_i7_fr4\layouts\` | DXF/SVG/params/DRC 等版图生成产物。 |
| `projects\bfp_6_8g_i7_fr4\results\` | RFPro/FEM 导出、score、summary、training dataset、prediction report。 |
| `projects\bfp_6_8g_i7_fr4\runs\` | 标准 run 输出目录，后续承载 manifest、state 和 logs。 |
| `projects\bfp_6_8g_i7_fr4\reports\` | 项目报告 HTML/PDF 和报告资产。 |
| `projects\bfp_6_8g_i7_fr4\references\` | 文章、论文、图片和外部参考。 |
| `projects\bfp_6_8g_i7_fr4\docs\` | 项目专用流程说明。 |
| `docs\` | 全局架构、评审、理论、治理和迁移记录。 |
| `src\simads\` | 可复用 Python 包。 |
| `tools\` | 兼容 CLI 入口，后续逐步变薄。 |
| `ADS\` | Deprecated，仅保留迁移说明，不再作为新产物根。 |

### 2.2 当前 home ADS 环境

以下配置摘自 `config/ads_profiles.json`，运行时以该 JSON 和 CLI 覆盖项为准。

```text
ADS workspace : D:\Work\ADS\BFP\BFP
ADS root      : D:\Hardware\Keysight\ADS2026_Update1
ADS library   : BFP_lib
Template cell : BFP
Substrate     : BFP_lib:substrate4
Host Python   : D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
ADS Python    : D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

家里运行 ADS 闭环时必须显式使用：

```text
--profile home --template-cell BFP
```

### 2.3 当前 company ADS 环境

公司电脑当前使用独立 uv 环境：

```text
ADS workspace : D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
ADS root      : D:\Hardware\Keysight\ADS2026_Update1
ADS library   : 6-8G_Fillter_lib
Template cell : interdigital_9o_ro4350b_508um_v3_wide_mm_coords
Substrate     : 6-8G_Fillter_lib:substrate1
Host Python   : D:\Microsoft\Python\ads-automation\Scripts\python.exe
ADS Python    : D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

公司电脑运行 ADS 闭环时默认使用：

```text
--profile company
```

### 2.4 当前脚本能力

| 脚本 | 职责 | 环境 |
|---|---|---|
| `tools\ads_profiles.py` | home/company ADS profile 路径配置。 | host Python |
| `tools\generate_interdigital_filter_layout.py` | 交指滤波器 DXF/SVG/JSON/DRC 生成。 | host Python |
| `tools\generate_filter_sweep.py` | 从 plan CSV 批量生成候选版图。 | host Python |
| `tools\ads_import_dxf_add_ports.py` | ADS Python 导入 DXF 并放置端口。 | ADS Python |
| `tools\ads_clone_emsetup_template.py` | 克隆并修补 EM Setup。 | host Python |
| `tools\ads_run_rfpro_fem.py` | 创建/更新 RFPro view 并运行 FEM。 | ADS Python |
| `tools\export_ads_fem_dataset.py` | 导出 ADS FEM dataset。 | ADS Python |
| `tools\analyze_ads_dataset.py` | 提取 S 参数关键指标并评分。 | host/ADS Python |
| `tools\run_ads_filter_candidate.py` | 单候选闭环入口。 | host Python |
| `tools\run_ads_filter_sweep.py` | 批量闭环入口。 | host Python |
| `tools\build_i7_fr4_optimization_dataset.py` | 合并历史计划和仿真结果，生成训练集。 | host Python |
| `tools\propose_i7_fr4_surrogate_candidates.py` | 基于代理模型和信赖域生成下一轮候选。 | host Python |

## 3. 目标架构

### 3.1 分层结构

平台长期应拆成六层：

```text
配置层
  -> 器件与版图层
  -> ADS 自动化层
  -> 仿真数据层
  -> 评分与优化层
  -> 报告与文档层
```

各层职责：

| 层 | 职责 | 不应承担 |
|---|---|---|
| 配置层 | profile、workspace、library、substrate、target profile、项目配置。 | 不生成版图，不跑仿真。 |
| 器件与版图层 | 参数化生成 Layout、DXF、SVG、DRC、端口。 | 不调用 ADS，不评分。 |
| ADS 自动化层 | 导入 DXF、克隆 emSetup、运行 RFPro/FEM、导出 dataset。 | 不决定候选方向。 |
| 仿真数据层 | 管理 raw result、score、summary、training dataset。 | 不直接修改几何。 |
| 评分与优化层 | 计算指标、约束、综合评分，生成下一轮候选。 | 不操作 ADS workspace。 |
| 报告与文档层 | 输出 HTML/PDF、维护索引、记录决策和迁移。 | 不作为原始数据唯一来源。 |

### 3.2 当前目标目录

当前已经开始按以下结构迁移。后续新增项目应复用同一边界：

```text
SIM\
├─ config\
│  ├─ ads_profiles.yaml
│  ├─ targets.yaml
│  ├─ substrates.yaml
│  └─ projects\
│     └─ bfp_6_8g_i7_fr4.yaml
├─ src\ads_auto\
│  ├─ core\
│  ├─ layout\
│  ├─ devices\
│  ├─ ads\
│  ├─ simulation\
│  ├─ optimization\
│  └─ reports\
├─ projects\
│  └─ bfp_6_8g_i7_fr4\
│     ├─ plans\
│     ├─ layouts\
│     ├─ results\
│     ├─ reports\
│     └─ notes\
├─ docs\
├─ tools\
└─ legacy\
```

迁移原则：旧 `tools\run_ads_filter_sweep.py` 仍保留兼容入口，但默认路径和新增结果应指向 `projects/<project_id>/...`。

### 3.3 平台核心契约和门禁

目标架构不仅是目录分层，还必须有可机器校验的契约。后续所有重构都应围绕以下核心契约推进：

| 契约 | 作用 | 最小落地物 |
|---|---|---|
| Profile Schema | 固定 ADS root、workspace、library、substrate、Python、license 等环境字段。 | `profile.yaml/json` + validate 命令。 |
| Target Profile Schema | 固定频段、硬约束、软目标、权重、评分版本。 | `target_profile.json`。 |
| Candidate Schema | 固定参数字段、单位、边界、来源算法、父候选。 | plan CSV + schema version。 |
| Layout Schema | 固定几何对象、layer map、ports、source map、DRC 结果。 | `layout.json` / `params.json`。 |
| Run Manifest | 固定一次仿真的环境、输入、脚本版本、ADS 版本和输出索引。 | `run_manifest.json`。 |
| Artifact Manifest | 固定 DXF、SVG、ADS cell、dataset、s2p、score、report 的路径和 hash。 | `artifact_manifest.json`。 |
| State Machine | 固定流程阶段、失败分类、重试次数、resume 策略。 | `state.json`。 |
| Dataset Schema | 固定训练集字段、指标、排除原因和版本。 | `data/DATA_SCHEMA_REGISTRY.md`。 |

这些契约优先于目录迁移。只要契约稳定，旧 `tools/` 可以逐步改为薄 CLI；如果契约不稳定，提前搬目录只会把隐性耦合扩散到新结构中。

### 3.4 推荐运行目录和产物结构

中长期每个候选 run 建议采用以下结构，不要求一次性迁移历史文件：

```text
projects/<project_id>/runs/<run_id>/
├─ run_manifest.json
├─ artifact_manifest.json
├─ state.json
├─ input/
│  ├─ candidate.json
│  ├─ target_profile.json
│  └─ profile_snapshot.json
├─ layout/
│  ├─ layout.json
│  ├─ source_map.json
│  ├─ candidate.dxf
│  ├─ candidate.svg
│  └─ drc_report.json
├─ ads/
│  ├─ cell_ref.txt
│  ├─ emsetup_patch.json
│  └─ manual_intervention.md
├─ dataset/
│  ├─ raw_dataset_ref.txt
│  ├─ sparams.s2p
│  └─ exported_rfpro.csv
├─ score/
│  ├─ score.json
│  └─ score.csv
├─ logs/
└─ report/
```

当前 P0/P1 过渡期的 sweep runner 仍使用兼容位置：

```text
projects/<project_id>/results/<round>/runs/<run_id>/
```

历史结果已经迁移到 `projects\bfp_6_8g_i7_fr4\results\<round>`。新脚本当前必须至少输出 manifest、state 和 logs；P1 目录迁移任务完成后，新 run 再默认写入 `projects/<project_id>/runs/<run_id>/`，round results 下只保留 summary、索引或兼容映射。

## 4. 核心对象模型

### 4.1 Environment/Profile

Environment 描述一台机器上的 ADS 运行环境。

必需字段示例，以下为 home profile：

```yaml
profile: home
ads_root: D:\Hardware\Keysight\ADS2026_Update1
ads_python: D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
host_python: D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
workspace: D:\Work\ADS\BFP\BFP
library: BFP_lib
template_cell: BFP
setup_view: em%Setup
rfpro_emsetup_view: emSetup
substrate: BFP_lib:substrate4
```

规则：

- ADS Python 只负责 `keysight.ads`、OA/RFPro API 和 dataset 导出。
- host Python 负责 CSV/JSON/XML、候选生成、评分、优化和报告。
- profile 覆盖项必须写入 log 和 summary。
- `em%Setup` 是物理 view 目录名，`emSetup` 是 RFPro API 逻辑名，两者必须明确区分。

### 4.2 Project

Project 描述一个具体设计任务。

示例：

```yaml
project_id: bfp_6_8g_i7_fr4
name: 6-8 GHz FR4 7阶交指带通滤波器
device_type: filter.interdigital
profile: home
library: BFP_lib
template_cell: BFP
substrate: BFP_lib:substrate4
frequency:
  start_ghz: 4.0
  stop_ghz: 10.0
target_profile: fr4_25db_rl6
```

Project 不保存每个候选的全部几何参数。候选参数属于 plan CSV 或 training dataset。

### 4.3 Device/Design

Device 是可参数化生成版图的器件类型。

每个 Device 应提供：

```text
parameter_schema
validate_params(params)
build_layout(params)
ports(params, layout)
write_outputs(params, out_dir)
default_objectives
optimizer_bounds(project_context)
score_adapters(target_profile)
report_sections
```

当前 Device：

```text
filter.interdigital
filter.folded_sir
filter.hilo_sir
filter.stub
```

当前 `src/simads/devices` 已有 plugin registry、参数 schema、builder module、layout builder 和 optimizer bounds 的基础骨架。`score_adapters`、`report_sections`、带 project/substrate/manufacturing context 的 `optimizer_bounds(project_context)` 仍属于 P1 contract 待办，跟踪在 `ARCH_REFACTOR_TODO.md` 的 P1-10。

### 4.4 Layout

Layout 是几何对象集合，不绑定滤波器。

基础对象：

```text
Rect
Quad
Polygon
Circle/Via
Path
Port
Boundary
LayerMap
```

通用输出：

```text
write_dxf()
write_svg()
write_params_json()
write_drc_report()
write_tuning_table()
```

验收标准：新增一个器件时，不需要复制 ADS 导入、RFPro、评分主流程。

### 4.5 SimulationRun

SimulationRun 描述一次 ADS/RFPro/FEM 仿真任务。

输入：

```text
candidate_id
DXF path
params path
profile
workspace
library
cell
template cell
setup view
substrate
frequency plan
target profile
```

步骤：

```text
1. 查找候选 DXF 和 params.json。
2. 导入 DXF 到 ADS Layout。
3. 根据 params.json 放置 P1/P2 等端口。
4. 克隆模板 emSetup。
5. 修补 substrate、layer、port、boundary。
6. 创建或更新 RFPro view。
7. 设置频率计划。
8. 运行 FEM。
9. 导出 S 参数。
10. 评分并写入 score.csv。
11. 汇总到 sweep_summary.csv。
```

### 4.6 Result/Dataset

Result 是单次仿真的输出。字段至少包含：

```text
candidate
cell
source
target_profile
status
s21_5g_db
s21_6g_db
s21_7g_db
s21_8g_db
s21_9g_db
passband_min_s21_db
passband_ripple_db
worst_s11_6_8_db
worst_s22_6_8_db
```

Optimization Dataset 是 plan 参数和 Result 的合并表，是优化器唯一可信输入。

当前训练集：

```text
projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_training_dataset.csv
```

### 4.7 Objective

Objective 定义硬约束、软目标和综合评分。

当前 FR4 目标：

```text
S21@5G <= -25 dB
S21@6G >= -5 dB
S21@8G >= -5 dB
passband_min_s21 >= -5 dB
passband_ripple <= 4 dB
worst S11/S22 <= -6 dB
```

规则：

- 硬约束余量必须单独输出。
- 综合评分只用于排序，不能替代曲线检查。
- 评分函数必须版本化。
- target profile 改变后，历史分数必须重新计算或明确标注不可直接比较。

### 4.8 Optimizer

Optimizer 只依赖参数向量和评分数据，不直接操作 ADS。

输入：

```text
training_dataset.csv
parameter_schema
bounds
current_best
target_profile
optimizer_config
random_seed
```

输出：

```text
next round plan CSV
prediction report CSV
optimizer log
candidate selection rationale
```

每个候选必须记录生成依据：中心点、边界、模型、随机种子、筛选门限、EI/改进概率、预测指标和与已知点距离。

### 4.9 Schema Registry

Schema Registry 是所有输入输出文件的版本登记处。凡是被多个脚本读取、写入或进入报告的数据，都必须登记字段、单位、可空规则和版本。

优先登记对象：

| 对象 | 文件形态 | 必须字段 |
|---|---|---|
| Profile | YAML/JSON/Python dict | `profile_id`, `ads_root`, `workspace`, `library`, `template_cell`, `substrate`, `ads_python`, `host_python`。 |
| Project | YAML/JSON | `project_id`, `device_type`, `profile`, `frequency`, `target_profile`, `output_root`。 |
| Candidate | CSV/JSON | `candidate_id`, `round_id`, `schema_version`, 参数字段、单位、生成算法、父候选。 |
| Layout | JSON | `layout_id`, `candidate_id`, `units`, `layers`, `ports`, `shapes`, `vias`, `geometry_hash`。 |
| Run | JSON | `run_id`, `candidate_id`, `profile_id`, `ads_version`, `stage`, `input_hash`, `script_versions`。 |
| Artifact | JSON | `artifact_id`, `run_id`, `type`, `path`, `hash`, `created_at`, `producer`。 |
| Score | CSV/JSON | `score_id`, `run_id`, `target_profile_id`, `score_version`, metrics、constraint margins、pass/fail。 |
| Training Dataset | CSV | `dataset_id`, feature schema、metric schema、source runs、excluded_reason、created_at。 |

通用规则：

- 所有 schema 必须包含 `schema_version`。
- 所有物理量字段必须能从字段名或 schema 中读出单位。
- 新增字段默认向后兼容；删除或改义必须升级 major version。
- 脚本读取旧版本时必须显式转换或拒绝运行，不能静默猜测。
- 报告只能引用通过 schema 校验的数据。

### 4.10 Device Plugin Contract

为了支持滤波器以外的 ADS 版图任务，每种器件必须实现同一套最小接口。滤波器专用概念不能进入通用 ADS 自动化层。

```text
device_id
parameter_schema()
normalize_params(raw)
validate_params(params)
build_layout(params, stackup, layer_map)
ports(params, layout)
drc_rules(stackup, manufacturer)
default_target_profiles()
score_adapters(target_profile)
report_sections(run_result)
optimizer_bounds(project_context)
```

接口边界：

| 层 | 允许做 | 禁止做 |
|---|---|---|
| Device plugin | 定义拓扑、参数、端口、DRC、报告章节。 | 直接打开 ADS workspace。 |
| Layout core | 生成通用几何对象和导出 DXF/SVG/GDS。 | 写死某个滤波器尺寸。 |
| ADS adapter | 把 layout 绑定到 ADS cell/layer/port/emSetup。 | 决定候选优化方向。 |
| Optimizer | 处理参数向量和评分。 | 直接修改版图文件或 ADS 工程。 |

新增器件验收标准：同一个 `run_candidate` 主流程不需要复制，只需要注册新的 device plugin、target profile 和 parameter schema。

### 4.11 Baseline 和 Release Candidate

Baseline 是受保护参考点，Release Candidate 是准备进入人工复核或报告发布的候选。二者都必须有冻结记录。

冻结记录至少包含：

```text
baseline_id / release_id
candidate_id
run_id
profile_id
ADS version
substrate
layout hash
score version
target profile
关键指标
冻结日期
复测容差
引用报告
```

规则：

- baseline 只能被引用和复测，不允许被普通 sweep 覆盖。
- home/company 或 ADS 版本变化后，先复跑 baseline，再比较新候选。
- 当前 FR4 7 阶交指滤波器的初始模板应立即作为 baseline freeze 对象登记。
- release candidate 发布前必须通过 schema、日志、曲线、版图、图片和报告一致性检查。

## 5. ADS API 文档、能力边界与调用深度

本章专门定义 ADS API 在本项目中的使用方式。它不是凭经验罗列“可能能做什么”，而是把 ADS 2026 Update 1 安装目录中的本地文档、Python wheel、示例和当前脚本验证结果统一管理起来，形成可复测的 API 能力地图。

结论先行：本项目应把 ADS API 能力分成四层管理。

```text
本地官方文档源
  -> API 能力矩阵
  -> smoke test / 最小脚本
  -> 项目自动化封装
```

任何进入正式自动化闭环的 ADS 能力，都必须能回答四个问题：

```text
1. 本地文档在哪里。
2. 具体调用哪个 Python 包、AEL 函数、命令行工具或文件格式。
3. 在 home/company profile 上是否验证过。
4. 失败时 fallback 是什么。
```

### 5.1 本地 ADS API 文档源

ADS 安装目录示例：

```text
D:\Hardware\Keysight\ADS2026_Update1
```

已确认存在的关键文档入口：

| 文档源 | 本地路径 | 项目用途 |
|---|---|---|
| ADS Python 总文档 | `D:\Hardware\Keysight\ADS2026_Update1\doc\python` | Python API、venv、dataset、DE、AEL、EDA Toolbox 的主入口。 |
| Design Environment Python | `doc\python\de\html\index.html` | workspace、library、cell、view、layout、OpenAccess、Python in ADS、Pcell。 |
| AEL Python | `doc\python\ael\html\index.html` | 从 Python 调用 AEL，补足 DE API 覆盖不到的 ADS 内部函数。 |
| ADS Dataset | `doc\python\dataset\html\index.html` | 读取、合并、生成 ADS dataset，作为 RFPro CSV 的复核通道。 |
| EDA Toolbox | `doc\python\edatoolbox\html\index.html` | ADS 环境、Circuit、Dataset、SIPro/RFPro 示例和跨工具自动化。 |
| PathWave Data Tools | `doc\python\pwdatatools\html\index.html` | ADS 数据、S 参数、Touchstone、CSV、MDIF 等文件读写。 |
| ADS HTML Help | `doc\ads\Content\ads2026update1` | AEL 函数、layout、substrate、Momentum、RFPro/FEM、workspace 传统帮助。 |
| 示例工程 | `examples` | PDK、AEL、artwork、RFPro/SIPro、filter/circuit 示例。 |
| Python wheelhouse | `tools\python\wheelhouse` | 在外部 venv/uv 环境安装 Keysight ADS Python wheel。 |
| ADS Python packages | `tools\python\packages` | `keysight.ads.ael`、`keysight.ads.de` 等 ADS 内嵌桥接包。 |
| ADS Python site-packages | `tools\python\Lib\site-packages` | `keysight.ads.dataset`、`keysight.edatoolbox`、`keysight.pwdatatools` 等可导入包。 |

这些路径必须写入环境 profile 或能力矩阵，而不是散落在脚本中。home/company 两套配置可以共享 API 章节，但必须分别记录 `ads_root`、Python 版本、wheel 安装状态和 smoke test 结果。

### 5.2 Python 环境接入规则

ADS 2026 Update 1 自带 Python 位于：

```text
D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

本项目 company 专用 uv 虚拟环境：

```text
D:\Microsoft\Python\ads-automation\Scripts\python.exe
```

本项目 home 专用 uv 虚拟环境：

```text
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
```

本地 AEL Python 文档明确给出三种接入方式：

```text
1. 直接使用 $HPEESOF_DIR/tools/python/python.exe。
2. 基于 ADS 自带解释器创建 venv。
3. 对外部 venv，把 $HPEESOF_DIR/tools/python/packages 加入 sys.path，并安装 wheelhouse 中的 Keysight wheel。
```

对当前项目，推荐策略是：

| 场景 | Python | 说明 |
|---|---|---|
| ADS 内部脚本、AEL/DE/Layout 操作 | ADS Python 或与 ADS 同版本 venv | 需要 `keysight.ads.de`、`keysight.ads.ael`、ADS 运行时 DLL。 |
| 批量候选生成、评分、代理模型 | uv venv | 需要 numpy/pandas/scipy/sklearn 等常规科学计算依赖。 |
| dataset 解析复核 | 优先 uv venv + Keysight wheel | 可减少 ADS GUI 依赖，但必须确认 wheel 与 Python major/minor 匹配。 |
| GUI 联动和 RFPro/FEM 启动 | ADS Python | 避免外部 Python 缺少 ADS 运行时上下文。 |

wheelhouse 中当前确认存在的 ADS 相关 wheel 包括：

```text
keysight-ads-ael
keysight-ads-de[app]
keysight-ads-subst
keysight-ads-dataset
keysight-ads-datalink
keysight-ads-datalink-sm3d
keysight-ads-ann
keysight-ads-dds[app]
keysight-ads-emtools
keysight-edatoolbox
keysight-pwdatatools
numpy / pandas / scipy / matplotlib
```

外部 venv 的硬规则：

- Python major/minor 必须与 ADS wheel 匹配；当前 ADS 自带 Python 是 cp313 体系。
- 必须设置 `HPEESOF_DIR=D:\Hardware\Keysight\ADS2026_Update1`。
- 必须能导入 `keysight.ads.de`、`keysight.ads.ael`、`keysight.ads.dataset` 中项目需要的模块。
- 不能只验证 `import keysight`，必须执行最小 API 调用或对象创建。
- venv 安装过程和 `pip freeze` 应作为环境文档资产保存。

### 5.3 API 分层

ADS 自动化涉及五类接口：

| 层级 | 典型能力 | 稳定性 | 当前策略 |
|---|---|---|---|
| ADS DE Python API | workspace、library、cell、view、layout、OpenAccess 对象 | 中高 | 优先作为正式工程对象操作接口。 |
| ADS AEL Bridge | 从 Python 调用传统 AEL 函数，例如 workspace、layout、technology、substrate 辅助函数 | 中 | 作为 DE API 的补充，调用前登记函数名和返回类型。 |
| RFPro/FEM/xxPro/EDA Toolbox | 创建或运行 RFPro/SIPro/PiPro、EM 求解、跨工具任务 | 中 | 当前自动仿真主路径，必须保留 smoke test。 |
| Dataset/Data Tools | ADS dataset、CSV、Touchstone、S 参数、DataFrame | 高 | 作为评分和回归复核主路径。 |
| 文件级工程操作 | OA view、XML/文本配置、substrate/view 文件复制或 patch | 中低 | 只用于 API 不完整处，必须保留备份、diff 和日志。 |

当前稳定闭环仍然是：

```text
host Python wrapper
  -> ADS Python 脚本
  -> ADS workspace/library/cell/view
  -> RFPro/FEM
  -> dataset/export
  -> host Python scoring
```

需要避免的误区：

- 不能把 `keysight.edatoolbox` 与 `keysight.ads.de` 混为一类；前者偏自动化工具箱和跨工具任务，后者偏 ADS Design Environment 对象模型。
- 不能把 ADS HTML Help 里的 AEL 函数直接当成 Python 原生 API；通过 `keysight.ads.ael.call` 桥接时要处理类型转换和上下文限制。
- 不能把“文档里存在”当成“本项目可批量自动化”；必须通过候选 cell smoke test。

### 5.4 Project、Workspace、Library 能力

这部分优先查阅：

```text
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\Workspace_Management_Functions.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\de_open_workspace().html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\de_create_new_workspace().html
```

项目需要支持的能力：

```text
打开既有 workspace
识别 workspace 路径是否有效
定位 library
检查 template cell / candidate cell / view 是否存在
创建或复制 candidate cell
读取和写入 layout view
读取 data directory 中的 dataset
关闭 workspace 并释放资源
```

当前项目不建议自动创建完整正式 ADS workspace，原因是：

- workspace、library、technology、substrate、layer map 经常包含工程级状态；
- 自动新建 workspace 后仍需要人工确认 substrate、license、library reference；
- 公司/家里工程结构不同，强行统一会降低可复现性；
- 当前目标是批量优化版图，不是替代 ADS 工程初始化向导。

推荐策略：

```text
ADS workspace 由人工或模板工程预先建立。
自动化脚本只在已验证 workspace/library 内创建 candidate cell。
profile 必须明确 workspace、library、template cell、layout view 和 substrate。
```

验收标准：

- 脚本启动时检查 workspace 是否存在。
- 检查 library 是否存在。
- 检查 template cell 和 setup view 是否存在。
- 如果 profile 指向错误工程，立即停止，不继续写入。
- company/home profile 的 workspace 检查结果分别记录。

### 5.5 Cell、View、Layout 与 Pcell 能力

这部分优先查阅：

```text
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pypde\docs\reference\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pypde\docs\examples\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pydocs\howto\exporter.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pydocs\howto\pcell.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\Layout_Command_Line_Editor.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\Examples_DXF_Import.html
D:\Hardware\Keysight\ADS2026_Update1\examples\DesignKit\DemoKit_mmWave\circuit\ael
D:\Hardware\Keysight\ADS2026_Update1\examples\DesignKit\DemoKit_mmWave\circuit\artwork
```

项目需要支持的版图能力：

```text
创建 candidate cell
创建或清空 layout view
导入 DXF/GDS/OA 版图
绘制基础图元：rect、path、polygon、via、pin、port、text、boundary
读取图元 bbox、layer、net、pin 信息
放置端口并建立 net 连接
导出版图用于复核：DXF/SVG/截图/GDS
```

当前主路径仍建议是：

```text
几何真值：params.json + DXF/SVG
ADS 承载：导入 DXF、映射 layer、放置 port、运行 EM
```

原因是论文复现和优化迭代更需要“几何可审计”。如果直接在 ADS 内逐个 API 绘制复杂 shape，很容易出现三类问题：

- ADS 内部对象与项目参数文件不同步；
- 图形结果难以在不启动 ADS GUI 的情况下复核；
- 后续换器件类型时，生成器、报告图和仿真版图难以共用同一套几何模型。

但是仍应研究 ADS 直接绘图能力，因为它适合：

- 自动放置端口、pin、marker、label；
- 生成简单测试结构；
- 从 ADS 导出的 Python 设计反推 API 调用模式；
- 后续实现 Python Pcell，把论文参数直接变成可编辑 ADS 参数化器件。

### 5.6 Layer、Technology、Substrate 和层叠能力

这部分优先查阅：

```text
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pysubst\docs\reference\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\de\html\pysubst\docs\examples\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\Technology_Functions_-_Substrate.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\db_get_lib_master_substrate_name().html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\ael\db_set_lib_master_substrate_name().html
```

已从本地 `keysight.edatoolbox.ads` 中确认存在的相关对象名包括：

```text
ConductorMaterial
DielectricMaterial
MaterialDatabase
SubstrateMaterial
SubstrateLayer
SubstrateVia
SubstrateStack
SubstrateModel
```

这说明“脚本构建层叠”具备研究基础，但正式策略仍要保守：

| 操作 | 自动化程度 | 说明 |
|---|---|---|
| 读取当前 library 的 substrate 名 | L3 | 可作为仿真前门禁。 |
| 选择已有 substrate | L3 | profile 明确指定，例如 `BFP_lib:substrate4`。 |
| 检查 layer 名和 layout unit | L3 | 导入前必须执行。 |
| 复制模板 substrate | L2/L3 | 可研究，但必须记录来源和 diff。 |
| 修改 er/h/t/tanD | L2 | 用于材料 sweep 时单独分支管理。 |
| 从零构建正式 substrate | L1/L2 | 需要人工 GUI 复核和 baseline repeat。 |
| 优化闭环中同时改几何和 substrate | 禁止默认启用 | 会混淆几何敏感性和材料敏感性。 |

当前 home 层叠：

```text
BFP_lib:substrate4
```

层叠记录必须包含：

```text
substrate library/cell/view
介电常数 er
板厚 h
铜厚 t
损耗角正切 tanD
金属电导率
via layer 定义
上下边界条件
layout unit / resolution
适用 ADS profile
验证日期
```

### 5.7 EM Setup、RFPro/FEM 与仿真控制能力

这部分优先查阅：

```text
D:\Hardware\Keysight\ADS2026_Update1\doc\python\edatoolbox\html\How-To\sipro.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\edatoolbox\html\Examples\ex_odbpp_simulate_rfpro.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\edatoolbox\html\Examples\ex_rfpro_stop_nets.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\edatoolbox\html\API_Reference\xxpro\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\ads\Content\ads2026update1\dgnflow\Post-Layout_Verification_Using_Momentum*.html
```

当前自动化主路径是克隆已验证模板 EM Setup，再通过 RFPro/FEM API 启动仿真。

项目需要支持的能力：

```text
克隆 candidate 的 emSetup
修补 cell 名、layout/view 引用、substrate 引用
创建或更新 RFPro view
设置频率范围和扫频点，例如 4-10 GHz
启动 FEM 仿真
记录 mesh / solve / export 阶段日志
等待仿真结束或超时
导出 RFPro CSV 或 ADS dataset
```

当前对应脚本：

```text
tools\ads_clone_emsetup_template.py
tools\ads_run_rfpro_fem.py
tools\export_ads_fem_dataset.py
```

能力边界：

- RFPro/FEM 的 GUI 设置不一定全部有稳定公开 API。
- 网格、边界、端口校准等高级设置应优先固化在模板 cell 中。
- API 修改频率计划后，必须从导出结果确认实际频率范围和点数。
- 批量仿真必须有阶段日志，区分准备失败、启动失败、mesh 失败、solve 失败、导出失败。

### 5.8 Dataset、S 参数和结果导出能力

这部分优先查阅：

```text
D:\Hardware\Keysight\ADS2026_Update1\doc\python\dataset\html\index.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\pwdatatools\html\howto\work_with_ADS_data.html
D:\Hardware\Keysight\ADS2026_Update1\doc\python\pwdatatools\html\howto\work_with_s_parameter_data.html
D:\Hardware\Keysight\ADS2026_Update1\tools\python\Lib\site-packages\keysight\ads\dataset
D:\Hardware\Keysight\ADS2026_Update1\tools\python\Lib\site-packages\keysight\pwdatatools
```

项目应同时支持两条结果通道：

```text
RFPro CSV：当前主路径，便于 host Python 评分。
ADS .ds dataset：复核路径，用于验证 CSV 导出和后续更复杂数据类型。
Touchstone/MDIF：通用交换格式，用于外部工具复测。
```

数据导出要求：

- 自动识别频率单位：Hz、MHz、GHz。
- 自动识别 S 参数列：S11、S21、S12、S22。
- 支持 complex、magnitude 和 dB 三种形式的输入。
- 输出统一评分字段。
- 导出失败要保留原始 dataset 路径和错误信息。
- 同一结果用 RFPro CSV 和 ADS dataset 评分时，关键指标应一致或差异可解释。

### 5.9 API 自动化深度分级

为了避免过度承诺，所有 ADS 能力按自动化深度分级：

| 等级 | 定义 | 示例 | 项目策略 |
|---|---|---|---|
| L0 手工 | 只能人工操作或人工确认 | 最终 GUI 复测、复杂 substrate 审阅 | 只用于冻结前复核。 |
| L1 半自动 | 脚本准备，人工点击或确认 | 新 substrate 从零创建、模板工程初始化 | 有 playbook 和检查表。 |
| L2 文件自动化 | 通过复制/patch 工程文件实现 | emSetup view 修补、模板 substrate 复制 | 必须备份、记录 diff、可回滚。 |
| L3 API 自动化 | 通过 ADS Python/RFPro API 完成 | 导入 DXF、放端口、运行 RFPro、导出 dataset | 批量主路径。 |
| L4 闭环自动化 | 与评分和优化器联动 | sweep、score-only、propose-next | 项目目标状态。 |

当前本项目能力评估：

| 能力 | 当前等级 | 说明 |
|---|---|---|
| 候选 DXF/JSON 生成 | L4 | host Python 已稳定。 |
| ADS workspace 从零创建 | L1 | 暂不作为主路径。 |
| library/cell/layout 写入 | L3 | 通过 ADS Python 和模板工程。 |
| 端口放置 | L3 | 由 params.json 驱动。 |
| emSetup 复用 | L2/L3 | 模板克隆 + patch。 |
| substrate 选择 | L3 | profile 指定已有 substrate。 |
| substrate 从零构建 | L1/L2 | 有 API 研究基础，但正式使用前需复核。 |
| RFPro/FEM 启动 | L3 | 当前主路径，但需更细日志和超时保护。 |
| Dataset 导出和评分 | L4 | 可进入优化闭环。 |
| GUI 最终复测 | L0 | 关键候选冻结前保留。 |

### 5.10 API 探测和能力登记

ADS API 能力不应靠记忆判断，必须在本机环境中探测并登记。项目新增能力登记文档：

```text
docs\env\ENV_ADS_API_CAPABILITY_MATRIX.md
```

登记字段：

```text
ADS version
profile
API/module
function/class
capability
documentation path
tested_script
test_date
status
known_limitations
fallback
```

API 验证分三步：

```text
Step 1: import smoke test
  验证 Python 环境、HPEESOF_DIR、sys.path、wheel 是否正确。

Step 2: object smoke test
  验证 workspace/library/cell/view/substrate/dataset 的最小读写或读取能力。

Step 3: workflow smoke test
  验证导入 DXF、放端口、克隆 emSetup、RFPro/FEM、导出、评分的完整链路。
```

### 5.11 API 相关近期任务

```text
P0-API-01 维护 ENV_ADS_API_CAPABILITY_MATRIX.md，记录本机 ADS 文档源和已验证 API。
P0-API-02 为 home profile 跑 ADS API import smoke test，记录 keysight.ads.de/ael/dataset/edatoolbox/pwdatatools。
P0-API-03 为 workspace/library/template/substrate 增加启动前门禁。
P0-API-04 给 RFPro/FEM 启动和导出增加明确日志阶段。
P0-API-05 把 API 失败分类接入 sweep_summary。
P1-API-01 验证 substrate 读取和存在性检查 API。
P1-API-02 验证是否可以安全复制 substrate 模板，但不进入正式优化闭环。
P1-API-03 建立 API fallback playbook：API 失败时哪些步骤可人工复测。
P2-API-01 研究 ADS workspace/library 从零初始化能力。
P2-API-02 评估 Python Pcell 是否适合作为论文版图参数化入口。
```
### 5.12 ADS API Smoke Test Gate

API smoke test 是环境切换和 ADS 自动化改动后的强制门禁。它必须在真正 FEM 前运行，因为这些检查耗时短，能快速定位路径、环境变量、workspace、library、template 和 dataset 问题。

| Gate | 验证内容 | 通过标准 | 失败处理 |
|---|---|---|---|
| ADS-PY-01 | ADS Python 可启动，`HPEESOF_DIR` 正确。 | 打印 ADS root、Python version、sys.path 关键项。 | 停止整轮。 |
| ADS-PY-02 | 导入 `keysight.ads.de/ael/dataset` 和 `keysight.edatoolbox/pwdatatools`。 | 项目需要的模块全部 import 成功。 | 停止整轮并提示 wheel/path。 |
| ADS-WS-01 | 打开 workspace。 | profile 指向的 workspace 存在且可打开。 | 停止整轮。 |
| ADS-LIB-01 | 读取 library、template cell、layout view。 | `library/template_cell/setup_view` 均存在。 | 停止整轮。 |
| ADS-SUB-01 | 读取 substrate。 | `BFP_lib:substrate4` 或 profile substrate 可定位。 | 停止整轮。 |
| ADS-LAY-01 | 创建临时 candidate cell 并写入最小图元。 | 临时对象可创建、可读取、可清理。 | 禁止批量导入。 |
| ADS-EM-01 | 克隆或读取模板 emSetup。 | emSetup 来源、view 名、substrate 引用可记录。 | 禁止启动 FEM。 |
| ADS-DS-01 | 读取已知 dataset/Touchstone。 | 能导出或解析 S 参数，单位正确。 | 禁止评分。 |

运行策略：

- 新机器、新 ADS 版本、新 profile、新 workspace 或脚本改动后必须跑完整 smoke test。
- 日常候选仿真前至少跑 ADS-PY、ADS-WS、ADS-LIB、ADS-SUB 快速 gate。
- smoke test 输出应写入 `logs/env_smoke_<profile>_<timestamp>.log`，并把结果摘要写入环境文档。
- smoke test 不应修改正式 template cell；需要写入测试时必须使用临时 cell，并带自动清理或人工清理记录。

## 6. Python 脚本与可复用模块管理

Python 脚本是本项目的执行层，不能长期维持为一组松散的 `tools/*.py`。后续项目会扩展到不同滤波器、匹配网络、谐振器、功分器、耦合器和其他 ADS 版图仿真任务，因此必须把“可复用模块”和“一次性任务脚本”分开管理。

本章只定义管理规则，不要求立即迁移目录。当前阶段可以继续保留 `tools/`，但每个脚本都必须能被归类、登记、复用或淘汰。

### 6.1 脚本分层

Python 代码分为七层：

| 层级 | 类型 | 典型职责 | 是否应复用 |
|---|---|---|---|
| CLI 入口层 | `run_*`、面向用户的命令 | 串联 profile、生成、导入、仿真、导出、评分 | 入口本身可复用，但不承载核心逻辑。 |
| ADS 自动化层 | `ads_*`、`export_ads_*` | ADS Python、AEL、RFPro/FEM、workspace、layout、dataset | 高复用，必须封装。 |
| 几何内核层 | layout primitives、DXF/SVG writer | Rect、Path、Polygon、Via、Port、Layer、BBox、坐标单位 | 最高复用，应尽快从生成脚本中抽出。 |
| 器件生成层 | `generate_*_layout.py` | 按器件拓扑生成具体版图 | 部分复用，拓扑专用逻辑保留在器件层。 |
| 评分与数据层 | `analyze_*`、dataset builder | 读取 S 参数、计算指标、合并训练集、输出 summary | 高复用，应独立于具体器件。 |
| 优化策略层 | `make_*`、`propose_*` | 候选生成、代理模型、信赖域、EI、筛选 | 高复用，但目标函数和参数空间可插拔。 |
| 探测与维护层 | `check_*`、`probe_*`、`patch_*` | 环境检查、API 探测、一次性修补、迁移辅助 | 可复用程度不一，必须标注实验/维护状态。 |

### 6.2 当前脚本归类

当前 `tools/` 中脚本可先按如下方式登记：

| 脚本 | 当前定位 | 后续处理 |
|---|---|---|
| `ads_profiles.py` | profile 配置模块 | 提升为稳定配置模块，拆分 home/company/schema。 |
| `run_ads_filter_candidate.py` | 单候选 ADS 仿真入口 | 保留为 CLI，内部调用通用 workflow。 |
| `run_ads_filter_sweep.py` | 批量 sweep 入口 | 保留为 CLI，调度逻辑抽到 workflow。 |
| `ads_import_dxf_add_ports.py` | ADS 导入 DXF 和端口放置 | ADS 自动化核心模块，需抽出 import/layout/port API。 |
| `ads_clone_emsetup_template.py` | emSetup 模板复制 | ADS 自动化核心模块，需抽出 setup manager。 |
| `ads_run_rfpro_fem.py` | RFPro/FEM 启动 | ADS 自动化核心模块，需增加阶段日志和错误分类。 |
| `export_ads_fem_dataset.py` | ADS/RFPro 结果导出 | 数据导出模块，需与 dataset 读取统一。 |
| `analyze_ads_dataset.py` | ADS dataset 分析 | 结果分析模块，可复用。 |
| `analyze_filter_s2p.py` | S 参数评分 | 评分核心，应改成器件无关 score engine。 |
| `generate_interdigital_filter_layout.py` | 交指滤波器版图生成 | 器件生成层；几何 primitive 应抽离。 |
| `generate_folded_sir_bpf_layout.py` | 折叠 SIR 版图生成 | 器件生成层；复用几何 primitive。 |
| `generate_hilo_sir_bpf_layout.py` | 高低阻抗 SIR 版图生成 | 器件生成层；复用几何 primitive。 |
| `generate_stub_bpf_layout.py` | stub BPF 版图生成 | 器件生成层；复用几何 primitive。 |
| `generate_paper_mixed_sir_bpf_layout.py` | 论文 mixed SIR 版图生成 | 器件生成层；保留论文复现元数据。 |
| `generate_filter_sweep.py` | sweep 几何批生成 | 入口脚本；生成逻辑改为调用器件生成器。 |
| `make_*_candidates.py` | 手工轮次候选生成 | 历史/实验脚本；迁移为 optimizer 配置。 |
| `propose_i7_fr4_surrogate_candidates.py` | 代理模型候选生成 | 优化策略核心，应抽象为通用 propose engine。 |
| `build_i7_fr4_optimization_dataset.py` | I7 FR4 训练集构建 | 数据集构建模块；器件字段可配置化。 |
| `check_ads_python_env.py` | ADS Python 环境检查 | smoke test 稳定入口。 |
| `ads_probe_ael_words.py` | AEL 探测 | API 研究脚本，登记到能力矩阵。 |
| `patch_ads_substrate_pcvia.py` | substrate/via 修补 | 维护脚本，正式流程中默认禁用。 |

### 6.3 可复用模块池

后续应沉淀以下可复用模块。模块名只是建议，先作为设计边界，不立即强制改目录。

| 模块 | 职责 | 可复用原因 |
|---|---|---|
| `simads.config` | profile、路径、ADS root、workspace、library、template、substrate | home/company 和不同项目都需要。 |
| `simads.logging` | 阶段日志、命令日志、错误分类、耗时统计 | 排查 ADS 超时和批量仿真失败必须统一。 |
| `simads.geometry` | Point、BBox、Rect、Polygon、Path、Via、Port、Transform、Unit | 所有版图器件共享。 |
| `simads.exporters` | DXF、SVG、params.json、dimension_check、DRC 文本 | 论文复现、报告和 ADS 导入都共享。 |
| `simads.ads.workspace` | workspace/library/cell/view 检查和创建 | 所有 ADS 工程共享。 |
| `simads.ads.layout` | DXF/GDS 导入、端口、pin、layer、unit 检查 | 所有 layout 仿真共享。 |
| `simads.ads.emsetup` | emSetup 模板克隆、view 引用、substrate 绑定 | 所有 EM 仿真共享。 |
| `simads.ads.rfpro` | RFPro/FEM 启动、等待、超时、结果定位 | 所有 FEM/RFPro 仿真共享。 |
| `simads.ads.dataset` | ADS dataset、RFPro CSV、Touchstone 读取和转换 | 所有评分共享。 |
| `simads.scoring` | S 参数指标、目标函数、硬约束、软评分 | 不应绑定交指滤波器。 |
| `simads.optimizer` | 参数空间、候选生成、代理模型、EI、信赖域 | 多种器件都能使用。 |
| `simads.reports` | HTML/PDF 报告资产、图表、指标表 | 不同项目报告共享。 |
| `simads.registry` | 脚本、器件、profile、实验轮次登记 | 保证可追溯和可迁移。 |

其中最优先抽取的是：

```text
P0: config / logging / scoring / dataset
P1: geometry / exporters / ads.workspace / ads.layout
P2: ads.emsetup / ads.rfpro / optimizer / reports
```

### 6.4 可复用与不可复用边界

判断一个脚本或函数能否沉淀为模块，使用以下规则：

| 判断问题 | 结论 |
|---|---|
| 是否依赖具体候选名、round 编号、文件名 | 是则先保留在 CLI 或实验脚本，不进入核心模块。 |
| 是否只依赖 profile、输入路径、输出路径和参数对象 | 可以抽成通用模块。 |
| 是否被两个以上器件或流程使用 | 应抽成可复用模块。 |
| 是否封装 ADS API 或环境变量 | 应抽成可复用模块，并配 smoke test。 |
| 是否包含论文特定尺寸、图片复原假设、拓扑规则 | 留在器件生成层，但调用通用几何模块。 |
| 是否包含目标频段、S 参数阈值、评分权重 | 抽成 Objective/Profile，不写死在算法里。 |
| 是否是一次性修补工程文件 | 保留为维护脚本，默认不可批量运行。 |

核心原则：

```text
模块保存能力。
CLI 编排流程。
配置表达差异。
数据文件记录实验。
```

### 6.5 运行时声明

每个 Python 脚本头部或登记表必须声明运行时：

| Runtime | 含义 | 示例 |
|---|---|---|
| `host` | 在 uv/普通 Python 中运行，不需要 ADS Python 运行时 | 候选生成、评分、报告生成。 |
| `ads` | 必须由 ADS Python 或 ADS 内部 Python 运行 | `keysight.ads.de`、AEL、RFPro/FEM。 |
| `both` | host 和 ADS Python 都可运行，但功能可能降级 | dataset 读取、环境探测。 |

运行时声明最少包含：

```text
runtime: host / ads / both
requires_ads_root: true / false
requires_workspace: true / false
requires_license: true / false
inputs:
outputs:
side_effects:
```

### 6.6 输入输出契约

所有稳定脚本必须固定输入输出契约。建议每个脚本登记：

```text
script_name
runtime
owner layer
input files
output files
profile fields used
writes ADS workspace: yes/no
writes filesystem: yes/no
idempotent: yes/no
safe to rerun: yes/no
log path
failure classes
```

对 ADS 自动化脚本，必须额外记录：

```text
workspace
library
source cell
target cell
layout view
em setup view
substrate
ADS Python executable
ADS version
```

### 6.7 稳定、实验和废弃状态

脚本状态分为四类：

| 状态 | 定义 | 管理规则 |
|---|---|---|
| `stable` | 当前流程依赖，允许长期复用 | 修改前必须知道输入输出影响，必要时做 baseline smoke test。 |
| `candidate` | 准备沉淀为 stable | 需要补 runtime、日志、异常、文档。 |
| `experimental` | 新算法、新器件、新 API 探测 | 可以快速迭代，但不得成为主流程隐性依赖。 |
| `deprecated` | 历史脚本或已被替代 | 保留原因、替代脚本和最后可用日期。 |

当前 `make_filter_round*`、`make_i7_fr4_round*` 属于明显的历史轮次脚本，后续应把其中有效的参数扰动策略收敛到 `optimizer` 配置，而不是无限增加 round 专用脚本。

### 6.8 迁移路线

不建议现在立刻大规模搬目录。合理路线是：

```text
P0: 建立脚本登记表，标注 runtime/status/input/output。
P0: 抽出 ads_profiles.py 为稳定配置入口。
P0: 给 run_ads_filter_candidate.py 和 run_ads_filter_sweep.py 增加阶段日志。
P1: 从 generate_*_layout.py 抽出 geometry/exporters。
P1: 从 analyze_* 抽出 dataset/scoring。
P1: 从 ads_* 抽出 workspace/layout/emsetup/rfpro 子模块。
P2: 建立 simads 包，CLI 只保留薄入口。
P2: 将 round 专用候选脚本收敛为 optimizer 配置文件。
```

最终目录形态可以演进为：

```text
src/simads/
  config/
  geometry/
  devices/
  ads/
  data/
  scoring/
  optimizer/
  reports/
cli/
  run_candidate.py
  run_sweep.py
  propose_candidates.py
tools/
  probes/
  maintenance/
  deprecated/
```

迁移前必须保证现有 `tools/` 命令仍可运行，或提供兼容入口。
### 6.9 兼容 CLI 和模块迁移约束

脚本模块化必须保持当前可运行命令的兼容性。迁移期间采用“旧 CLI 保留，内部调用新模块”的方式。

| 迁移对象 | 规则 |
|---|---|
| `run_ads_filter_candidate.py` | 保留参数兼容；内部逐步调用 `simads.config`, `simads.ads.*`, `simads.scoring`。 |
| `run_ads_filter_sweep.py` | 保留 round 批量入口；新增 manifest、state、resume、候选白名单和 summary schema。 |
| `generate_*_layout.py` | 逐步抽出通用 geometry/exporter，器件脚本只保留拓扑和参数规则。 |
| `analyze_*` | 抽出 dataset parser、metric calculator、target profile evaluator。 |
| `make_*_candidates.py` | 收敛为 optimizer 配置和候选生成策略，不继续增加 round 专用脚本。 |
| `ads_*` | 分为 workspace、layout、emsetup、rfpro、dataset 五类模块，并各自配 smoke test。 |

迁移验收：

```text
1. 旧命令仍可运行，或有同名兼容入口。
2. 旧输出路径不被破坏。
3. 新输出额外补 manifest/state/log，不改变历史 CSV 语义。
4. 新模块不读取全局硬编码路径，只接受 profile/project/context。
5. 无 ADS 依赖的模块必须能在 uv host Python 中单元测试。
```

## 7. 关键数据流

### 7.1 当前可执行闭环

```text
filter_opt_i7_fr4_roundN.csv
  -> generate_filter_sweep.py 或 make_i7_fr4_roundN_candidates.py
  -> ADS\interdigital_7o_fr4_210um_roundN\*.dxf/*.json
  -> run_ads_filter_sweep.py
  -> ADS workspace: BFP_lib:<cell>
  -> RFPro/FEM
  -> ADS\results\interdigital_7o_fr4_210um_roundN\*_rfpro.csv
  -> *_score.csv
  -> sweep_summary.csv
```

### 7.2 优化闭环

```text
历史 plan CSV + sweep_summary.csv
  -> build_i7_fr4_optimization_dataset.py
  -> training_dataset.csv
  -> propose_i7_fr4_surrogate_candidates.py
  -> filter_opt_i7_fr4_roundN.csv
  -> run_ads_filter_sweep.py
  -> 新 sweep_summary.csv
  -> 回填 training_dataset.csv
```

### 7.3 后续通用命令形态

未来希望收敛到项目配置驱动：

```powershell
ads-auto build-layouts --project projects\bfp_6_8g_i7_fr4\project.yaml --round round7
ads-auto run-sweep     --project projects\bfp_6_8g_i7_fr4\project.yaml --round round7 --profile home
ads-auto score         --project projects\bfp_6_8g_i7_fr4\project.yaml --round round7
ads-auto propose       --project projects\bfp_6_8g_i7_fr4\project.yaml --next-round round8
ads-auto report        --project projects\bfp_6_8g_i7_fr4\project.yaml --round round8
```

### 7.4 Run State Machine

线性脚本链必须升级为可恢复状态机。每个候选 run 的状态写入 `state.json`，用于判断是否跳过、重跑、恢复或标记失败。

状态定义：

| 状态 | 进入条件 | 完成产物 | 可 resume |
|---|---|---|---|
| `planned` | candidate 进入执行队列。 | `candidate.json` 或 plan row snapshot。 | 是。 |
| `layout_generated` | 参数已生成 DXF/SVG/JSON/DRC。 | layout 文件和 geometry hash。 | 是。 |
| `ads_imported` | DXF 已导入 ADS candidate cell，端口已放置。 | ADS cell ref、import log。 | 是。 |
| `emsetup_ready` | emSetup 已克隆/修补，substrate 和频率计划确认。 | emSetup patch log。 | 是。 |
| `sim_running` | RFPro/FEM 已启动。 | RFPro log、start time。 | 谨慎；需判断 ADS 进程和 dataset。 |
| `dataset_exported` | S 参数 raw data 已导出。 | RFPro CSV、dataset ref、Touchstone。 | 是。 |
| `scored` | 指标和约束已计算。 | score.csv/json。 | 是。 |
| `reported` | 报告或 summary 已更新。 | summary row、report artifact。 | 是。 |
| `failed` | 任一阶段不可恢复失败。 | error_class、failed_step、log_path。 | 视错误类型。 |

Resume 规则：

- 默认按 hash 判断输入是否变化；未变化时复用已完成阶段。
- candidate 参数、profile、substrate、target profile、ADS 版本或评分版本变化时，必须生成新 run_id。
- `sim_running` 超时后不能直接覆盖，应先检查 ADS 进程、dataset 文件和日志时间戳。
- `score-only` 只能从 `dataset_exported` 或更晚状态进入。
- `report-only` 只能引用 `scored` 或 `reported` 状态。

### 7.5 Manifest 和结果追溯

每个 run 必须输出 `run_manifest.json` 和 `artifact_manifest.json`。二者是报告、训练集和结果复盘的根索引。

`run_manifest.json` 最小字段：

```json
{
  "schema_version": "1.0",
  "run_id": "bfp_6_8g_i7_fr4_round7_i7_fr4_r7_bo04_home_20260801_001",
  "project_id": "bfp_6_8g_i7_fr4",
  "round_id": "round7",
  "candidate_id": "i7_fr4_r7_bo04",
  "profile_id": "home",
  "ads_root": "D:/Hardware/Keysight/ADS2026_Update1",
  "workspace": "D:/Work/ADS/BFP/BFP",
  "library": "BFP_lib",
  "template_cell": "BFP",
  "target_cell": "i7_fr4_r7_bo04",
  "substrate": "BFP_lib:substrate4",
  "target_profile_id": "fr4_25db_rl6",
  "score_version": "1.0",
  "input_hash": "...",
  "layout_hash": "...",
  "status": "scored",
  "created_at": "2026-08-01T00:00:00+08:00"
}
```

`artifact_manifest.json` 最小字段：

```json
{
  "schema_version": "1.0",
  "run_id": "...",
  "artifacts": [
    {"type": "params", "path": "layout/params.json", "hash": "..."},
    {"type": "dxf", "path": "layout/candidate.dxf", "hash": "..."},
    {"type": "rfpro_csv", "path": "dataset/exported_rfpro.csv", "hash": "..."},
    {"type": "score", "path": "score/score.csv", "hash": "..."}
  ]
}
```

追溯规则：任意报告图、S 参数曲线、score 行和训练集样本，都必须能追到 `run_id -> candidate_id -> layout_hash -> profile_id -> ADS version -> target_profile_id`。

## 8. 工程治理体系

### 8.1 配置管理

配置管理用于保证路径、层叠、目标和输出目录可复现。

配置分层：

```text
全局环境配置：ADS root、ADS Python、host Python、license 环境。
ADS 工程配置：workspace、library、template cell、setup view、substrate。
项目配置：器件类型、频率范围、目标指标、默认输出目录。
候选配置：candidate 几何参数、notes、生成算法版本。
本机私有配置：只在本机存在，不作为共享基准。
```

验收标准：

- 任意仿真结果都能追溯到 profile、substrate 和 target profile。
- home/company 两套配置共存，切换不需要改代码。
- 命令行覆盖项进入 log 和 summary。
- 个人路径不进入通用模板，除非明确作为本机 profile 记录。

### 8.2 实验数据治理

每个 candidate 的最小追溯链：

```text
round_id
  -> plan CSV row
  -> params.json
  -> DXF/SVG/DRC
  -> ADS library:cell:view
  -> RFPro/FEM raw result
  -> exported S-parameter CSV
  -> score CSV
  -> sweep_summary.csv
  -> training_dataset.csv
  -> report/decision record
```

建议统一标识：

```text
project_id
round_id
candidate_id
run_id
geometry_hash
score_version
optimizer_version
```

规则：

- 不覆盖历史 round summary。
- 每轮至少保留一个 baseline repeat，监控 ADS/FEM 设置漂移。
- 同一几何重复仿真时保留多条 measurement，同时提供唯一几何聚合视图。
- training dataset 由脚本生成，不手工编辑。
- 报告引用结果时必须写明 plan、summary、target profile 和 ADS profile。

### 8.3 日志与可观测性

除 FEM 本身外，其它步骤理论上都应很快。每一步必须记录时间戳、耗时、命令和返回码。

推荐日志目录：

```text
ADS\results\<round>\logs\
├─ sweep_<timestamp>.log
├─ <candidate>_candidate.log
├─ <candidate>_ads_import.log
├─ <candidate>_rfpro.log
└─ <candidate>_score.log
```

每个候选至少记录：

```text
profile / workspace / library / template cell
输入 DXF / params.json
ADS cell 名称
执行命令
返回码
stdout/stderr 摘要
RFPro 开始和结束时间
导出文件路径
评分结果
异常类型和堆栈
```

验收标准：看到超时后能判断卡在导入、emSetup、RFPro、导出还是评分。

### 8.4 错误分类与恢复

错误分类：

| 类别 | 典型原因 | 默认处理 |
|---|---|---|
| `ENV_ERROR` | ADS Python 不存在、uv 缺包、license 不可用 | 停止整轮。 |
| `PROFILE_ERROR` | workspace/library/template/substrate 不存在 | 停止整轮。 |
| `LAYOUT_ERROR` | DXF 不存在、DRC 失败、端口非法 | 跳过候选。 |
| `ADS_IMPORT_ERROR` | DXF 导入或 layer 映射失败 | 跳过候选。 |
| `EMSETUP_ERROR` | emSetup 克隆或 substrate 修补失败 | 视模板问题决定停止或跳过。 |
| `RFPRO_ERROR` | RFPro API、mesh、仿真启动失败 | 跳过候选。 |
| `TIMEOUT` | FEM 或 ADS API 长时间无响应 | 标记超时并继续。 |
| `DATA_ERROR` | dataset 缺失、CSV 缺列、频率单位异常 | 尝试重导出，否则标记无效。 |
| `SCORE_ERROR` | 指标计算或 target profile 异常 | 停止评分。 |

summary 建议补充字段：

```text
status,error_class,error_message,failed_step,elapsed_s,log_path
```

### 8.5 仿真任务调度

执行层级：

```text
smoke test：只跑 1 个候选，验证环境和模板。
priority batch：跑优化器推荐的前 3-5 个候选。
full round：跑完整 round 候选。
score-only：只重新评分已有数据。
report-only：只生成报告。
```

规则：

- 新环境或新模板先跑 baseline smoke test。
- 新优化算法候选先跑前 3-4 个，不一次性全跑。
- ADS workspace 同一时间只允许一个写入任务。
- 支持候选白名单、黑名单、最大耗时、最大连续失败数。
- 支持断点续跑和失败候选重跑。

### 8.6 验证与回归测试

测试层级：

```text
unit：单位转换、评分、CSV schema。
layout：DXF/SVG/params.json 一致性。
drc：最小线宽、最小间距、端口位置。
score：固定 RFPro CSV 样例评分回归。
profile：home/company profile 路径和 ADS Python 检查。
smoke：baseline candidate prepare-only 或 skip-fem。
full：关键候选完整 RFPro/FEM 复测。
```

最低门禁：

```powershell
D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile E:\OneDrive\4.Code\SIM\tools\*.py
D:\Microsoft\Python\ads-automation\Scripts\python.exe E:\OneDrive\4.Code\SIM\tools\check_ads_profile.py --profile company --require-template
D:\Microsoft\Python\ads-automation\Scripts\python.exe E:\OneDrive\4.Code\SIM\tools\build_i7_fr4_optimization_dataset.py
```

家里电脑执行同类 gate 时使用 `config/ads_profiles.json` 中的 `home.host_python`，并显式传入 `--profile home --template-cell BFP`。

### 8.7 安全与环境隔离

基本规则：

- 不自动删除 ADS workspace 中已有 cell，除非显式确认。
- 写入 ADS 前打印 profile、workspace、library、template cell。
- 家里默认使用 `--profile home --template-cell BFP`。
- 重要候选先 `prepare-only` 或单候选 smoke test。
- 历史 round 结果默认只读，不覆盖。
- 本机私有路径不写入通用模板。

高风险操作需要单独确认：

```text
删除 ADS cell
覆盖 template cell
修改 substrate
批量清理 results
移动历史报告或训练集
```

### 8.8 依赖与运行环境

职责划分：

| 环境 | 职责 |
|---|---|
| uv host Python | CSV/JSON/XML、候选生成、评分、报告、优化算法。 |
| ADS Python | `keysight.ads`、OA/RFPro API、dataset 导出、ADS 工程操作。 |

规则：

- `numpy` 是 host Python 基础依赖。
- `scikit-learn` 可作为后续可选依赖，不作为当前必需依赖。
- ADS Python 不随意安装第三方包，优先只调用 ADS API。
- 依赖变更必须写入环境文档和 smoke test 记录。

### 8.9 ADS Workspace 写入安全

ADS workspace 是高价值工程资产，自动化脚本必须默认保守写入。

写入策略：

| 对象 | 默认权限 | 规则 |
|---|---|---|
| template cell | 只读 | 任何脚本不得直接覆盖；需要修改时新建模板版本。 |
| candidate cell | 可写 | 名称必须包含 candidate_id 或 run_id，禁止与 template 同名。 |
| emSetup template | 只读 | 克隆后修补，修补记录写入 manifest。 |
| substrate | 只读 | profile 指定已有 substrate；自动创建/修改 substrate 只允许在实验 gate 中。 |
| historical results | 只读 | 默认不覆盖；重跑产生新 run_id 或 measurement_id。 |
| logs/state/manifest | 可追加 | 可更新当前 run 状态，不修改冻结 run。 |

高风险命令必须显式 `--force` 或人工确认：

```text
删除 ADS cell
覆盖已有 candidate cell
修改 substrate 或 technology
清空 results 目录
覆盖 baseline/release candidate
移动历史报告、训练集或 frozen manifest
```

每次写 ADS 前必须打印并记录：

```text
profile_id
workspace
library
template_cell
target_cell
substrate
operation
writes_template: true/false
force: true/false
```

### 8.10 Baseline 漂移和冻结治理

当前 FR4 7 阶交指滤波器的初始模板是已知最好基线，应当从普通候选中提升为 frozen baseline。

Baseline 规则：

- 每个新 profile、ADS 版本、substrate 或 emSetup 变更后，先复跑 baseline。
- baseline repeat 必须与 frozen 指标比较，超出容差则暂停优化并排查环境漂移。
- 新候选只有在 baseline repeat 合格后才可与历史结果比较。
- baseline 记录只补勘误，不随普通实验覆盖。

建议漂移容差：

| 指标 | 默认容差 |
|---|---|
| `S21@5G` | ±0.5 dB |
| `S21@6G` | ±0.3 dB |
| `S21@8G` | ±0.3 dB |
| `passband_min_s21` | ±0.3 dB |
| `worst_s11_6_8` | ±0.5 dB |
| `worst_s22_6_8` | ±0.5 dB |

### 8.11 人工介入记录

自动化过程中允许 ADS GUI 人工复核或临时修补，但必须留下记录，不能让人工操作成为隐性输入。

每次人工介入记录：

```text
run_id
operator
time
ADS profile
workspace/library/cell/view
manual action
reason
before/after screenshot or exported file
impact on reproducibility
whether automation script needs update
```

若人工介入改变了 ADS cell、emSetup、substrate 或导出数据，该 run 不能直接作为自动化训练样本，除非 manifest 中明确标记并解释。

## 9. 版图、评分与优化设计

### 9.1 论文、公式和图片到版图的重建规则

从论文、公式或图片生成 ADS 可仿真的版图时，不能把图片直接描成 DXF。正确流程是把外部资料转成可追溯的参数化版图模型：

```text
资料来源
  -> 电气目标提取
  -> 拓扑识别
  -> 尺寸归一化
  -> 参数化建模
  -> 规则约束和 DRC
  -> DXF/SVG/params.json 输出
  -> ADS EM 仿真校准
```

该流程必须满足三个要求：

- 可追溯：每个关键尺寸都能说明来自公式、论文表格、图片量测、经验初值还是优化结果。
- 可复现：同一组参数可以重新生成相同 DXF、SVG、端口和 DRC 报告。
- 可约束：孔、shape、端口、层叠、边界和最小制造尺寸都由规则检查，不靠人工肉眼判断。

#### 8.1.1 资料来源可信度分级

不同来源的可信度不同，不能同等使用。

| 来源 | 可用于 | 风险 | 处理规则 |
|---|---|---|---|
| 论文尺寸表 | 初始几何参数 | 单位、基板和工艺可能不同 | 直接入参数表，但记录原始单位和缩放规则。 |
| 论文公式 | 电长度、阻抗、耦合系数、外部 Q 初值 | 公式多为准静态或理想模型 | 只作为初始值，必须 EM 校准。 |
| 论文版图图片 | 拓扑、相对位置、弯折方式、孔位置 | 缺比例尺、截图变形、线宽不准 | 仅在有已知尺寸标定后提取坐标。 |
| ADS/仿真截图 | 结构复核、端口位置参考 | 可能不是最终版 | 只能作为辅助，不作为唯一尺寸来源。 |
| 实物照片 | 拓扑、孔阵列、布局风格 | 透视畸变、铜皮不可见 | 需要透视校正和至少两个已知尺寸。 |
| 经验规则 | 初始估计、缺失尺寸补齐 | 不唯一 | 必须标记为 assumption，并进入优化变量。 |

来源记录应写入 `params.json` 或同名 metadata：

```json
{
  "sources": {
    "L1_mm": {"type": "paper_table", "ref": "Table 1", "raw": "5.50 mm"},
    "gap_mm": {"type": "image_measurement", "scale": "0.0125 mm/px"},
    "tap_mm": {"type": "assumption", "reason": "external-Q initial estimate"}
  }
}
```

#### 8.1.2 公式到几何参数的映射

公式不能直接等价为最终版图，只能生成初始参数和约束范围。

常见映射：

| 公式/指标 | 几何含义 | 输出参数 |
|---|---|---|
| 中心频率 `f0` | 谐振器电长度 | `resonator_l_mm`, `stub_len_mm` |
| 分数带宽 `FBW` | 级间耦合强度 | `gap_mm`, `coupling_spacing_mm` |
| 低通原型 `g_i` | 外部 Q 和耦合矩阵 | `tap_mm`, `feed_gap_mm`, `S1..Sn` |
| 微带阻抗 `Z0` | 线宽 | `feed_width_mm`, `resonator_w_mm` |
| 有效介电常数 `er_eff` | 导波波长 | `lambda_g_mm`, `quarter_wave_mm` |
| 传输零点位置 | 开路/短路枝节长度 | `stub_len_mm`, `sir_ratio` |
| 接地短路条件 | via 位置和孔径 | `via_x`, `via_y`, `via_diameter_mm` |

公式输出必须包含容差范围：

```text
nominal: 5.55 mm
lower_bound: 5.535 mm
upper_bound: 5.565 mm
reason: quarter-wave initial estimate + current EM calibrated trust region
```

#### 8.1.3 图片到几何的坐标化规则

图片转换成版图前必须建立坐标系。

步骤：

```text
1. 选择图片原点，建议使用版图左下角或输入端口中心。
2. 确认至少一个已知尺寸；如果可能，使用两个正交方向尺寸。
3. 计算 x/y 像素到 mm 的比例。
4. 检查图片是否存在透视或非等比缩放。
5. 提取中心线、边界、孔中心、端口位置。
6. 将像素坐标转成 mm 坐标。
7. 用参数化 shape 重建，而不是直接保留像素轮廓。
```

图片没有比例尺时，只允许提取：

```text
拓扑结构
连接关系
相对顺序
对称关系
孔的大致数量和分布
端口所在边
```

不允许直接提取：

```text
绝对线宽
绝对间距
谐振器长度
孔径
端口尺寸
```

图片量测必须输出校准信息：

```text
image_file
pixel_width
pixel_height
scale_x_mm_per_px
scale_y_mm_per_px
reference_dimension
origin_definition
rotation_deg
measurement_uncertainty_mm
```

#### 8.1.4 拓扑识别规则

版图重建首先识别拓扑，而不是尺寸。

需要明确：

```text
器件类型：滤波器、耦合器、功分器、天线、匹配网络。
传输线类型：微带、共面波导、带状线、短截线、SIR。
谐振器类型：开路、短路、交指、发夹、折叠、阶跃阻抗。
连接关系：串联、并联、耦合、接地、开路端。
对称关系：左右对称、上下对称、镜像端口、差分结构。
端口定义：单端、差分、接地参考、端口方向。
接地方式：过孔、边界地、背面整铜、via fence。
```

拓扑识别输出建议为结构化描述：

```yaml
topology:
  device_type: filter.interdigital
  order: 7
  resonators:
    - id: R1
      shorted_end: bottom
      coupled_to: [R2]
    - id: R2
      shorted_end: top
      coupled_to: [R1, R3]
  ports:
    - id: P1
      role: input
      attached_to: feed_left
    - id: P2
      role: output
      attached_to: feed_right
  symmetry: mirror_x
```

#### 8.1.5 参数化建模规则

所有正式版图都必须参数化，不能只保存一张静态 DXF。

参数分三类：

| 类型 | 示例 | 规则 |
|---|---|---|
| 电气主参数 | `L_mm`, `gap_mm`, `tap_mm` | 进入优化向量。 |
| 工艺参数 | `min_gap_mm`, `via_diameter_mm`, `copper_thickness_mm` | 来自工艺和 substrate，不随意优化。 |
| 派生参数 | `field_width_mm`, `port_x`, `boundary_w` | 由脚本计算，不手工填写。 |

`params.json` 至少包含：

```text
parameters
ports
derived
rectangles/shapes summary
sources
constraints
```

参数命名规则：

- 长度使用 `_mm` 后缀。
- 频率使用 `_ghz` 或 `_hz` 后缀。
- dB 指标使用 `_db` 后缀。
- 布尔选项使用明确语义，例如 `via_half_outside`。
- 不使用只有论文局部意义的名字，例如 `a`, `b`, `d1`，除非同时提供 alias。

#### 8.1.6 Shape 基础图元规则

版图生成应使用统一基础图元：

```text
Rect
Quad
Polygon
Path
Via
Port
Boundary
Text/Marker
Keepout
```

每个 shape 必须包含：

```text
name
kind
layer
role
coordinates
net 或 connection role
source 或 derived_from
```

推荐字段：

```json
{
  "name": "resonator_1",
  "kind": "rect",
  "layer": "cond",
  "role": "resonator",
  "x_mm": 0.0,
  "y_mm": 0.0,
  "w_mm": 0.3648,
  "h_mm": 5.55,
  "net": "floating_or_shorted_by_via"
}
```

Shape 约束：

- 坐标内部统一使用 mm。
- 所有金属 shape 必须闭合。
- Polygon 顶点顺序必须一致，建议逆时针。
- 禁止零面积、负宽度、负高度 shape。
- 禁止小于制造最小线宽的孤立尖角。
- 重叠铜皮允许，但必须可解释；不允许由重复 shape 意外造成短路。
- shape 必须落在 EM boundary 内，除非明确是边界辅助层。
- 输出 DXF 前必须做 layer name 映射检查。

#### 8.1.7 Via 和孔规则

孔是 ADS EM 建模和制造约束中最容易出错的对象，必须单独建模，不能只画一个圆形金属 pad。

Via 必需参数：

```text
via_id
x_mm
y_mm
via_diameter_mm
via_pad_mm
via_layer
pad_layer
connect_from_layer
connect_to_layer
role
```

常见 role：

```text
ground_short
via_fence
thermal_via
signal_transition
alignment_or_marker
```

制造约束：

```text
via_diameter_mm >= min_drill_mm
via_pad_mm >= via_diameter_mm + 2 * min_annular_ring_mm
via_edge_to_copper_edge_mm >= min_copper_clearance_mm
via_to_via_pitch_mm >= min_via_pitch_mm
via_center 必须落在 pad 内
```

ADS/FEM 约束：

- via layer 必须匹配 ADS substrate 中定义的 via 层，例如当前 `pcvia1`。
- pad 必须画在金属层，例如当前 `cond`。
- 接地 via 必须与短路端金属发生明确连接。
- via 不应压到端口 reference plane。
- 半出界 via、外置 pad 等特殊做法必须参数化，例如 `via_half_outside`, `via_pad_outside`。
- via fence 需要定义 pitch、边界距离、首尾位置，不能手工散点。

当前 FR4 交指滤波器相关参数：

```text
via_diameter_mm = 0.254
via_pad_mm = 0.3556
via_layer = pcvia1
metal_layer = cond
via_half_outside = true
via_pad_outside = false
```

#### 8.1.8 端口规则

端口定义直接影响 S 参数，必须结构化输出。

端口必需字段：

```text
port_id
role
x_mm
y_mm
orientation
impedance_ohm
attached_shape
reference
calibration_plane
```

端口约束：

- 端口必须落在金属 feed 的中心线或边缘 reference plane 上。
- P1/P2 的方向必须和信号传播方向一致。
- 端口阻抗默认 50 ohm，但必须写入参数。
- 差分端口必须成对定义，不能用两个无关系单端端口代替。
- 端口不能与 via、边界或其它金属孤岛重叠。
- 端口位置必须随 feed 几何派生，不能手工独立漂移。

端口输出示例：

```json
{
  "ports": {
    "P1": {"x_mm": -3.54, "y_mm": 1.95, "z0_ohm": 50, "role": "input"},
    "P2": {"x_mm": 7.0502, "y_mm": 1.95, "z0_ohm": 50, "role": "output"}
  }
}
```

#### 8.1.9 Layer 和 substrate 规则

Layer 名称必须来自 ADS 工程和 substrate，不应由器件脚本随意发明。

当前 home 环境：

```text
metal_layer = cond
via_layer = pcvia1
substrate = BFP_lib:substrate4
```

Layer 规则：

- 每个 shape 必须有 layer。
- 每个 layer 必须能映射到 ADS library 的真实 layer。
- via layer 必须存在于 substrate stackup。
- 不同 profile 的 layer 名如果不同，由 profile 或 layer map 处理。
- 输出文件必须记录 layer map 版本。

Substrate 规则：

```text
材料 er
板厚 h
铜厚 t
损耗角正切 tanD
金属电导率
via 定义
上下边界条件
```

都必须可追溯。不能只在报告里说“FR4”，而不说明实际 ADS substrate cell。

#### 8.1.10 EM Boundary 和仿真区域规则

EM boundary 决定边缘场和端口参考，必须由版图外形自动计算。

规则：

- boundary 必须包住所有金属、via、port 和 pad。
- boundary margin 应参数化，例如 `boundary_margin_mm`。
- 高频结构不能让金属过于贴近 boundary。
- 端口 reference plane 到 boundary 的关系必须稳定。
- 如果论文图片中没有边界，边界由 EM 规则生成，不从图片量测。

推荐派生：

```text
boundary_min_x = min(all_shape_x) - boundary_margin_mm
boundary_max_x = max(all_shape_x) + boundary_margin_mm
boundary_min_y = min(all_shape_y) - boundary_margin_mm
boundary_max_y = max(all_shape_y) + boundary_margin_mm
```

#### 8.1.11 DRC 检查规则

DRC 是版图生成的硬门禁。未通过 DRC 的候选不应进入 ADS FEM。

最小 DRC 项：

| 检查项 | 说明 |
|---|---|
| `min_trace_width` | 所有金属 shape 最小宽度。 |
| `min_gap` | 金属之间最小间距。 |
| `min_via_diameter` | 钻孔直径下限。 |
| `min_annular_ring` | via pad 环宽。 |
| `via_inside_pad` | via 中心和孔径必须被 pad 覆盖。 |
| `port_on_metal` | 端口必须连接到金属。 |
| `boundary_contains_all` | EM boundary 包住所有关键对象。 |
| `layer_exists` | 所有 layer 在 ADS/profile 中存在。 |
| `no_zero_area_shapes` | 禁止零面积 shape。 |
| `unit_consistency` | mm/mil/Hz/GHz 单位一致。 |

DRC 输出：

```text
candidate_drc.txt
candidate_dimension_check.txt
```

DRC 结果建议分级：

```text
PASS
WARN
FAIL
```

`FAIL` 不进入 ADS。`WARN` 可以进入 ADS，但必须写入 notes 和报告。

#### 8.1.12 输出文件契约

从论文或图片重建出来的每个候选必须输出同一套文件：

```text
<candidate>.dxf
<candidate>_mm_coords.dxf
<candidate>_ads_mil_coords.dxf
<candidate>.svg
<candidate>_params.json
<candidate>_drc.txt
<candidate>_dimension_check.txt
<candidate>_tuning_table.csv
<candidate>_source_map.json
```

其中：

| 文件 | 职责 |
|---|---|
| `_params.json` | 几何真值、端口、派生尺寸、材料和约束。 |
| `_source_map.json` | 每个关键尺寸的来源、置信度、量测方式。 |
| `_drc.txt` | 制造和仿真前规则检查。 |
| `_dimension_check.txt` | 总尺寸、最小特征、端口位置等摘要。 |
| `_tuning_table.csv` | 参数名、当前值、建议范围、影响方向。 |
| `.svg` | 人工审阅和报告图。 |
| `_mm_coords.dxf` | ADS 推荐导入文件。 |

#### 8.1.13 当前交指滤波器的落地规则

当前 7 阶 FR4 交指滤波器已经符合部分规则：

```text
Rect/Quad 生成谐振器和馈线。
via_pad 和 ground_via 显式生成。
P1/P2 写入 params.json。
DXF/SVG/DRC/params.json 同步输出。
候选参数进入 filter_opt_i7_fr4_round*.csv。
```

需要继续补齐：

```text
source_map.json：记录基线尺寸来自论文、图片、公式还是 EM 校准。
更完整 DRC：尤其是 via 环宽、port_on_metal、layer_exists。
端口结构化字段：orientation、attached_shape、calibration_plane。
layer map：从 profile 读取 cond/pcvia1，而不是候选脚本散落指定。
图片量测记录：如果从文章版图提取尺寸，必须保存 scale 和 uncertainty。
```

#### 8.1.14 版图重建验收清单

任何“从论文/图片/公式重建”的版图，进入 ADS 仿真前必须满足：

```text
[ ] 明确资料来源和可信度。
[ ] 明确器件拓扑和端口定义。
[ ] 至少一个可靠比例尺，或明确声明图片只用于拓扑。
[ ] 所有关键尺寸参数化。
[ ] 所有 shape 有 name、layer、role 和坐标。
[ ] 所有 via 有孔径、pad、layer、连接角色。
[ ] 所有 port 有位置、方向、阻抗和 attached shape。
[ ] substrate、metal layer、via layer 与 ADS profile 一致。
[ ] EM boundary 自动包住所有对象。
[ ] DRC 无 FAIL。
[ ] 输出 DXF/SVG/params.json/DRC/source map。
[ ] 报告能追溯每个关键尺寸的来源。
[ ] ADS smoke test 至少完成 prepare-only 或 skip-fem。
```

### 9.2 版图与器件抽象

器件层应只负责从参数到版图，不负责 ADS 仿真和优化决策。

每个器件实现：

```text
validate_params(params) -> DRCResult
build_layout(params) -> Layout
ports(params, layout) -> list[Port]
tuning_table(params) -> CSV rows
write_outputs(params, out_dir)
```

可扩展器件类型：

```text
filter.interdigital
filter.folded_sir
filter.hilo_sir
filter.stub
coupler.branchline
divider.wilkinson
antenna.patch
matching.lumped_distributed
```

### 9.3 参数向量化

当前 FR4 7 阶交指滤波器先保持对称参数：

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

展开到版图：

```text
S1 = S6 = S1S6
S2 = S5 = S2S5
S3 = S4 = S3S4
```

如果后续 S11/S22 不对称明显，再打开非对称自由度：

```text
S1_delta = S1 - S6
S2_delta = S2 - S5
S3_delta = S3 - S4
```

### 9.4 参数影响方向

| 参数 | 主要影响 | 当前策略 |
|---|---|---|
| `L_mm` | 中心频率、6/8 GHz 边缘、5 GHz 阻带 | 小步长，不再大幅缩短。 |
| `tap_mm` | 外部 Q、输入/输出匹配、边缘插损 | 1.94-1.96 附近局部搜索。 |
| `Egap_mm` | 端部加载、阻带/高端边缘折中 | 用于补偿 5 GHz 阻带。 |
| `S1/S6` | 输入/输出端耦合、S11/S22 | 先对称，后续再开放非对称。 |
| `S2/S5` | 次外侧耦合、通带形状 | 小扰动。 |
| `S3/S4` | 中心耦合、带宽和纹波 | 小扰动。 |
| `W0_mm` | 馈线阻抗 | 大改容易恶化，窄范围。 |
| `feed_len_mm` | 馈线相位/变换 | 控制在 2.85-3.25。 |
| `feed_taper_len_mm` | 馈线过渡 | 避免 0.75 这类明显恶化点。 |
| `feed_tip_w_mm` | 抽头局部耦合 | 0.18-0.20 是重点方向。 |
| `feed_overlap_mm` | 馈线加载强度 | 小范围配合 tip/tap 搜索。 |

### 9.5 搜索算法路线

普通梯度下降不适合作为第一选择，因为 ADS FEM 是昂贵黑盒，没有解析梯度，且响应可能受网格和几何拓扑影响而非光滑。

推荐路线：

| 阶段 | 样本量 | 推荐算法 |
|---|---:|---|
| 初始探索 | 0-20 | 理论模板 + LHS/Sobol 小样本。 |
| 局部收敛 | 20-80 | Pattern Search/MADS + 信赖域。 |
| 代理优化 | 40-150 | Ridge/RBF/RandomForest/Gaussian Process + EI。 |
| 神经网络 | 150-300+ | 小型 MLP ensemble 或多输出 surrogate。 |
| 鲁棒优化 | 稳定候选出现后 | 对 er、h、铜厚、蚀刻偏差做容差扫描。 |

当前实现的是轻量代理优化：

```text
tools\build_i7_fr4_optimization_dataset.py
tools\propose_i7_fr4_surrogate_candidates.py
```

它使用 bootstrap 线性岭回归、对称信赖域候选池、Expected Improvement 和硬约束过滤。当前样本量不足以可靠使用神经网络。
### 9.6 制造约束和鲁棒优化 Gate

单点仿真最优不等于可制造最优。进入 release candidate 前必须做制造和材料扰动检查。

制造约束至少包含：

| 类别 | 检查项 |
|---|---|
| 线宽 | 最小线宽、窄线连续长度、阻抗线宽上下限。 |
| 间距 | 谐振器间距、端口间距、开路端间距、地间隙。 |
| 铜层 | 铜厚、表面粗糙度、导体损耗模型。 |
| 介质 | FR4 介电常数、损耗角、板厚、批次偏差。 |
| 过孔 | 孔径、焊盘、反焊盘、via-to-edge、via-to-line。 |
| 边界 | EM box、空气层、辐射边界、端口参考地。 |
| 制造 | 最小蚀刻能力、拼板/板边、阻焊开窗、加工公差。 |

鲁棒优化流程：

```text
1. 普通优化找到可行候选。
2. 对入围候选做局部 tolerance sweep。
3. 统计最差值、均值、标准差和约束失效率。
4. 若单点最优对容差高度敏感，优先选择鲁棒性更高的候选。
5. 最终报告同时给出 nominal 和 tolerance 结论。
```

当前 FR4 7 阶交指滤波器优先扰动：

```text
线宽 ±0.03 mm
耦合间距 ±0.03 mm
谐振器长度 ±0.05 mm
FR4 Er ±0.2
板厚 ±0.03 mm
铜厚按 1 oz / 0.5 oz 两档复核
```

## 10. 文档与报告体系

### 10.1 docs/README.md 总入口

`docs\README.md` 是文档总入口，必须维护：

- canonical 主文档；
- 当前流程入口；
- 优化、理论、报告和结果索引；
- 进度记录路由；
- 新增文档规则；
- 迁移约束。

新增正式文档后必须更新 `docs\README.md`。

### 10.2 文档元数据

所有新的 Markdown 文档标题下方应包含：

```text
Status: Draft | Active | Frozen | Deprecated
Domain: <DOMAIN>
Canonical: `docs/<FILE>.md`
Related: `docs/<RELATED>.md`
Last updated: YYYY-MM-DD
Owner: ADS Automation
```

### 10.3 文档领域和命名

建议领域前缀：

| Domain | 范围 |
|---|---|
| `ARCH` | 顶层架构、模块边界、迁移路线。 |
| `ENV` | ADS 安装、profile、Python、workspace、library、license。 |
| `FLOW` | 自动仿真流水线、命令、异常处理、日志。 |
| `LAYOUT` | 版图基础对象、DXF/SVG、DRC、端口、层映射。 |
| `DEVICE` | 器件级参数化模型。 |
| `FILTER` | 滤波器专项设计、理论、调参结论。 |
| `OPT` | 搜索算法、目标函数、代理模型、训练数据。 |
| `RESULT` | 仿真汇总、轮次报告、候选比较。 |
| `REPORT` | HTML/PDF 报告模板、图片资产和发布版报告规则。 |
| `DOCS` | 文档治理、命名、索引、迁移记录。 |

新正式文档建议使用：

```text
<DOMAIN>_<SUBJECT>_<TYPE>.md
```

当前中文文档先保留，不强制立即迁移。

### 10.4 进度记录路由

| 领域 | 进度入口 | 规则 |
|---|---|---|
| ADS 环境 | `env/ENV_UV_COMPANY_20260801.md`、`env/ENV_ADS_API_CAPABILITY_MATRIX.md` | 记录 Python、license、workspace、library、substrate、template 修复。 |
| 自动化流程 | `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`、`flow/FLOW_MANUAL_INTERVENTION_LOG.md` | 记录导入、emSetup、RFPro、导出、日志、超时排查和人工介入。 |
| 交指滤波器优化 | `result/RESULT_I7_FR4_ROUND_INDEX.md`、`opt/FR4交指滤波器搜索算法改进方案.md` | 记录 roundN 候选、仿真结果、评分、下一轮决策。 |
| 文档治理 | `ARCH_DIRECTORY_GOVERNANCE.md`、`ARCH_REFACTOR_TODO.md` | 记录文档改名、索引补齐和迁移计划。 |
| 报告输出 | `report/REPORT_TEMPLATE_PLAYBOOK.md` | 记录 HTML/PDF 模板、图片、公式、版图分析报告调整。 |

任务记录格式：

```text
### <DOMAIN>-TASK-YYYYMMDD-NNN - 任务标题

- 目标：
- 输入：
- 操作：
- 结果：
- 验证：
- 结论：
- 风险：
- 后续：
- 涉及文件：
```

### 10.5 仿真轮次文档规则

每一轮优化都需要能复盘。至少记录：

```text
round id
设计中心点
参数边界
候选生成算法
候选 CSV
版图输出目录
ADS profile
template cell
substrate
target profile
结果 summary
最佳候选
失败原因
下一轮动作
```

建议建立：

```text
docs\result\RESULT_I7_FR4_ROUND_INDEX.md
```

### 10.6 报告与资产管理

报告必须包含：

```text
生成日期
数据来源
ADS profile
target profile
仿真频率范围
候选版本
关键指标表
S 参数曲线
版图图
结论和下一步
```

规则：

- 图片必须实际嵌入或可访问。
- 公式必须可读，不能只截图不解释。
- 版图分析必须说明关键尺寸和耦合关系。
- HTML/PDF 结果和原始 CSV 指标一致。
- 报告中所有候选名能追溯到 plan CSV。

中长期建议报告目录：

```text
reports\<report_id>\
├─ report.md
├─ report.html
├─ report.pdf
└─ assets\
```

### 10.7 文档状态、冻结和发布规则

文档状态必须影响后续使用方式：

| 状态 | 含义 | 使用规则 |
|---|---|---|
| Draft | 设计或评审中。 | 可讨论，不作为自动化实现唯一依据。 |
| Active | 当前有效规则。 | 脚本、流程和报告可以引用。 |
| Frozen | 历史基线、正式报告或已发布结论。 | 只补勘误，不改结论；变更需新文档或新版本。 |
| Deprecated | 已被替代。 | 保留迁移说明和替代入口。 |

正式报告发布 gate：

```text
REPORT-GATE-01 报告引用 run_manifest 和 artifact_manifest。
REPORT-GATE-02 报告中的曲线、表格和 score 文件一致。
REPORT-GATE-03 图片资产实际存在并嵌入或可访问。
REPORT-GATE-04 公式可读且符号有解释。
REPORT-GATE-05 版图图注说明关键尺寸、端口、层和耦合关系。
REPORT-GATE-06 若包含优化结论，必须说明 baseline 和 target profile。
REPORT-GATE-07 发布后状态可转 Frozen，后续只补勘误。
```

### 10.8 建议补齐的子文档

按照独立评审，主框架后续应拆出以下子文档，避免单文件继续膨胀：

| 优先级 | 文档 | 目的 |
|---|---|---|
| P0 | `ARCH_REQUIREMENTS_AND_ACCEPTANCE.md` | 平台需求、非目标、MVP/V1/V2 验收。 |
| P0 | `data/DATA_SCHEMA_REGISTRY.md` | JSON/CSV/Touchstone/报告输入输出契约。 |
| P0 | `data/DATA_RUN_MANIFEST_SCHEMA.md` | run manifest 和 artifact manifest 字段。 |
| P0 | `flow/FLOW_RUN_STATE_MACHINE.md` | 状态机、resume、幂等和失败处理。 |
| P0 | `test/TEST_STRATEGY.md` | 单元测试、几何 golden、ADS smoke、baseline full run。 |
| P1 | `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` | 论文/公式/图片到版图的审查清单。 |
| P1 | `flow/FLOW_JOB_SCHEDULING_POLICY.md` | license、并发、锁、超时和队列。 |
| P1 | `result/RESULT_BASELINE_FREEZE_POLICY.md` | baseline 冻结、复测和漂移检测。 |
| P1 | `DEVICE_PLUGIN_CONTRACT.md` | 多器件扩展接口。 |
| P1 | `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` | 制造容差和鲁棒优化。 |

## 11. 当前滤波器用例

### 11.1 当前最好候选

当前最好候选仍是初始模板重复点：

```text
i7_fr4_r3_base / i7_fr4_r4_base / i7_fr4_r5_base / i7_fr4_r6_base
```

关键指标：

```text
S21@5G = -27.15 dB
S21@6G = -2.13 dB
S21@8G = -4.28 dB
passband_min_s21 = -4.28 dB
ripple = 2.83 dB
worst S11 = -5.55 dB
worst S22 = -5.98 dB
```

结论：硬约束基本满足，主要缺口是 `worst S11` 距离 `-6 dB` 还差约 `0.45 dB`。

### 11.2 round7 定位

round7 不是大范围随机搜索，而是补充局部模型信息，重点验证代理模型在基线附近提出的高信息量点。

已生成：

```text
projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round7.csv
projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7\
projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_round7_predictions.csv
```

建议先跑 4 个候选：

```powershell
$SIM_ROOT = 'E:\OneDrive\4.Code\SIM'
$PY = 'D:\Microsoft\Python\ads-automation\Scripts\python.exe'
& $PY "$SIM_ROOT\tools\run_ads_filter_sweep.py" --profile company --target-profile fr4_25db_rl6 --plan "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round7.csv" --out-dir "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7" --results-dir "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7" --summary "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7\sweep_summary.csv" --skip-generate --continue-on-error --candidates i7_fr4_r7_bo04 i7_fr4_r7_bo01 i7_fr4_r7_bo03 i7_fr4_r7_bo05
```

跑完后更新训练集：

```powershell
& $PY "$SIM_ROOT\tools\build_i7_fr4_optimization_dataset.py"
```

再生成 round8：

```powershell
& $PY "$SIM_ROOT\tools\propose_i7_fr4_surrogate_candidates.py" --round-name round8 --out-dir "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round8" --plan "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round8.csv" --prediction-report "$SIM_ROOT\projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_round8_predictions.csv"
```

## 12. 迁移路线

迁移原则：新架构边界优先；项目资产先从旧 `ADS/` 拆入 `projects/<project_id>/...`；旧 CLI 先保留兼容，再抽模块；先跑 smoke，再跑 FEM；先冻结 baseline，再比较新候选。

### 12.1 P0：补齐平台化前置 Gate

```text
P0-01 建立 ARCH_REQUIREMENTS_AND_ACCEPTANCE.md，明确 MVP/V1/V2 和非目标。
P0-02 建立 DATA_SCHEMA_REGISTRY.md，登记 profile、project、candidate、layout、run、artifact、score、training dataset。
P0-03 让 run_ads_filter_candidate.py 输出 run_manifest.json、artifact_manifest.json、state.json。
P0-04 建立 FLOW_RUN_STATE_MACHINE.md，明确 planned 到 reported/failed 的状态和 resume 规则。
P0-05 建立 TEST_STRATEGY.md，并把 ADS API smoke test 作为 home/company 环境切换 gate。
P0-06 强化 ADS workspace 写入安全：template 只读、candidate cell 命名、--force 策略、历史结果只读。
P0-07 冻结当前 FR4 7 阶交指 baseline，记录 run、layout hash、score version 和漂移容差。
P0-08 run_ads_filter_sweep.py 输出候选级结构化 log、错误分类和 elapsed_s。
P0-09 sweep_summary.csv 增加 status、error_class、failed_step、elapsed_s、run_id、profile_id、score_version。
P0-10 docs/README.md 登记所有新增 P0 文档。
```

P0 完成标准：单候选 run 可以完整追溯，失败可以定位阶段，重复运行不会误覆盖 ADS 模板或历史结果。

### 12.2 P1：稳定批量优化闭环

```text
P1-01 target_profile.json 固化硬约束、软目标、权重、采样点和评分版本。
P1-02 plan CSV 和 training_dataset.csv 通过 schema 校验。
P1-03 round7 小批量候选完成仿真，结果回填训练集。
P1-04 建立 RESULT_I7_FR4_ROUND_INDEX.md，记录 round2-roundN 的最佳点、失败点和下一轮决策。
P1-05 建立 optimizer policy：信赖域、EI/PI、可行概率、探索/开发比例、随机种子。
P1-06 建立 baseline repeat 漂移监控，环境变更后先复跑 baseline。
P1-07 建立人工 ADS GUI 介入记录格式。
P1-08 建立 report release gate，HTML/PDF 报告引用 manifest 和 artifact hash。
```

### 12.3 P2：模块化重构

```text
P2-01 配置 YAML/JSON 化，并保留 ads_profiles.py 兼容层。
P2-02 建立 src/simads 包，旧 tools CLI 改成薄入口。
P2-03 抽象 geometry primitives、DXF writer、SVG writer、DRC checker。
P2-04 抽象 ads.workspace、ads.layout、ads.emsetup、ads.rfpro、ads.dataset。
P2-05 把 interdigital/folded_sir/hilo_sir/stub 迁移为 device plugin。
P2-06 把评分、训练集构建和优化器泛化为 project + schema + target profile 驱动。
P2-07 统一 run 目录、报告目录和资产目录。
```

### 12.4 P3：多器件、高级优化和鲁棒设计

```text
P3-01 支持匹配网络、功分器、耦合器、巴伦、天线等非滤波器器件。
P3-02 引入 RandomForest/ExtraTrees/Gaussian Process 等代理模型，并保存模型评估报告。
P3-03 样本足够后尝试小型 MLP ensemble，但必须与基线代理模型对照。
P3-04 对介电常数、板厚、铜厚、蚀刻偏差做容差扫描。
P3-05 建立 release candidate 的人工 ADS 复测、制造约束复核和 Frozen 报告发布流程。
```

## 13. 风险清单

| 风险 | 后果 | 控制措施 |
|---|---|---|
| home/company profile 混用 | 结果不可比，可能写错 ADS 工程。 | 每次运行打印 profile/workspace/library/template。 |
| substrate 或 layer 错误 | 仿真结论失效。 | summary 记录 substrate，baseline repeat 监控漂移。 |
| 评分版本不一致 | 历史候选排序失真。 | score_version 入表，必要时重算历史结果。 |
| 单变量扫参继续扩大 | FEM 时间浪费，难以改善基线。 | 使用信赖域、硬约束和 EI 排序。 |
| 文档和数据脱节 | 后续无法复盘。 | docs/README、round index、task progress 强制更新。 |
| 自动覆盖历史结果 | 丢失可追溯性。 | 新 round 新目录，历史结果默认只读。 |
| 过早神经网络化 | 过拟合，候选方向误导。 | 样本不足时使用 Pattern Search/轻量代理模型。 |
| 缺少 manifest | 报告、score、s2p、layout 无法稳定追溯。 | 每个 run 输出 run_manifest 和 artifact_manifest。 |
| 缺少状态机 | 超时或失败后不知道从哪一步恢复。 | 使用 state.json 记录 stage、failed_step、resume 策略。 |
| template cell 被误写 | 基线工程被污染，后续结果不可比较。 | template 默认只读，candidate cell 必须带 run_id/candidate_id。 |
| baseline 漂移 | 新旧候选比较失真。 | 环境变更后先复跑 frozen baseline。 |
| 多器件接口失控 | 滤波器专用字段扩散到通用框架。 | 新器件必须实现 Device Plugin Contract。 |

## 14. 近期验收清单

当前框架进入可执行状态前，至少完成：

```text
[ ] docs/README.md 已存在，并包含当前 canonical 主文档和独立评审文档。
[ ] ADS版图自动仿真项目框架设计.md 保持 Active，并已回填 P0/P1 gate。
[ ] ADS自动仿真流程说明.md 明确 home/company profile。
[ ] profile schema 已定义，home profile 可通过启动校验。
[ ] ADS API smoke test 覆盖 import、workspace、library、template、substrate、dataset。
[ ] 单候选 run 能输出 run_manifest.json、artifact_manifest.json、state.json。
[ ] run_ads_filter_sweep.py 输出候选级结构化 log。
[ ] sweep_summary.csv 增加 status、error_class、failed_step、elapsed_s、run_id、profile_id、score_version。
[ ] ADS workspace 写入策略生效，template cell 和 historical results 默认只读。
[ ] 当前最好点和 baseline repeat 已 frozen，并定义漂移容差。
[ ] round7 前 4 个候选完成 ADS/FEM 仿真。
[ ] training_dataset.csv 回填 round7 结果，并通过 schema 校验。
[ ] RESULT_I7_FR4_ROUND_INDEX.md 建立并记录 round2-round7。
[ ] 下一轮候选由数据集和算法生成，而不是手工猜参。
[ ] 报告引用 manifest、score、曲线和版图资产，能够追溯到 run_id。
```



















