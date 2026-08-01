# ADS 自动仿真 Run / Artifact Manifest Schema

Status: Active
Domain: DATA
Canonical: `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Related: `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/flow/FLOW_RUN_STATE_MACHINE.md`, `docs/ARCH_REFACTOR_TODO.md`, `docs/ADS版图自动仿真项目框架设计.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档冻结当前 P0 阶段 `run_manifest.json`、`artifact_manifest.json` 和 `state.json` 的最小字段。脚本可以追加兼容字段，但不得删除或改变本文档定义字段的语义。

## 1. 文件位置

推荐位置：

```text
projects/<project_id>/runs/<run_id>/
├─ run_manifest.json
├─ artifact_manifest.json
├─ state.json
└─ logs/
```

当前实现兼容位置：

```text
projects/<project_id>/results/<round>/runs/<run_id>/
├─ run_manifest.json
├─ artifact_manifest.json
└─ state.json
```

当前 `tools/run_ads_filter_sweep.py` 和单候选 runner 在 round 结果目录下写入该兼容位置。P0 阶段允许继续使用兼容位置；P1 起新 run 应逐步迁移到 `projects/<project_id>/runs/<run_id>/`，round results 下保留 summary、索引或兼容映射。

## 2. Run ID 规则

默认格式：

```text
<project_id>_<round_id>_<candidate_id>_<profile_id>_<YYYYMMDD_HHMMSS>
```

规则：

- `project_id`、`round_id`、`candidate_id`、`profile_id` 必须使用 safe id。
- safe id 只允许 `A-Z`、`a-z`、`0-9`、`_`、`-`、`.`。
- sweep 入口必须在调用单候选 runner 前预生成 `run_id`。
- 手动复跑 baseline 时可显式传入 `--run-id`，但不得覆盖已 frozen run。

## 3. State Schema

文件：

```text
state.json
```

当前版本：

```text
schema_version = 1.0
```

必填字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | string | 固定为 `1.0`。 |
| `run_id` | string | 当前 run ID。 |
| `candidate_id` | string | 候选 ID。 |
| `profile_id` | string | ADS profile。 |
| `stage` | string | 当前阶段。 |
| `status` | string | `planned`、`running`、`completed`、`failed`、`skipped`。 |
| `failed_step` | string/null | 失败步骤，成功为空。 |
| `error_class` | string/null | 失败分类，成功为空。 |
| `message` | string/null | 状态说明。 |
| `elapsed_s` | number/null | 当前耗时，单位 s。 |
| `updated_at` | string | ISO 时间。 |

可选字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `extra` | object | 阶段相关附加信息。 |

允许 stage：

```text
planned
layout_ready
ads_imported
emsetup_ready
rfpro_ready
sim_running
dataset_exported
scored
reported
completed
failed
```

状态机以 `flow/FLOW_RUN_STATE_MACHINE.md` 和 `src/simads/runtime/state_machine.py` 为准；`stage` 描述流程阶段，`status` 描述 run 生命周期状态。

失败分类：

```text
ENV_ERROR
PROFILE_ERROR
DATA_ERROR
LAYOUT_ERROR
EMSETUP_ERROR
RFPRO_ERROR
SCORE_ERROR
SAFETY_ERROR
TIMEOUT
SUBPROCESS_ERROR
UNKNOWN_ERROR
```

## 4. Run Manifest Schema

文件：

```text
run_manifest.json
```

当前版本：

```text
schema_version = 1.0
```

必填字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | string | 固定为 `1.0`。 |
| `run_id` | string | 当前 run ID。 |
| `project_id` | string | 项目 ID。 |
| `round_id` | string | 轮次 ID。 |
| `candidate_id` | string | 候选 ID。 |
| `profile_id` | string | ADS profile ID。 |
| `profile_snapshot` | object | profile 配置快照。 |
| `workspace` | string | ADS workspace 路径。 |
| `library` | string | ADS library。 |
| `template_cell` | string | emSetup 模板 cell。 |
| `target_cell` | string | 当前候选 cell。 |
| `setup_view` | string | 物理 EM setup view。 |
| `rfpro_emsetup_view` | string | RFPro API setup view。 |
| `substrate` | string | substrate 引用。 |
| `target_profile_id` | string | 目标 profile。 |
| `score_source` | string | `rfpro-csv` 或 `fem-dataset`。 |
| `frequency_start_ghz` | number | 仿真起始频率。 |
| `frequency_stop_ghz` | number | 仿真终止频率。 |
| `inputs` | object | 输入文件路径。 |
| `outputs` | object | 输出文件路径。 |
| `flags` | object | CLI 行为开关。 |
| `write_safety` | object | ADS workspace 写入安全策略快照。 |
| `status` | string | `planned`、`running`、`completed`、`failed`、`skipped`。 |
| `stage` | string | 最终或当前阶段。 |
| `error_class` | string/null | 失败分类。 |
| `updated_at` | string | ISO 时间。 |

`inputs` 必填子字段：

| 字段 | 说明 |
|---|---|
| `dxf` | 候选 DXF 路径。 |
| `params` | 候选 params JSON 路径。 |

`outputs` 必填子字段：

| 字段 | 说明 |
|---|---|
| `rfpro_csv` | RFPro CSV 输出路径。 |
| `score_csv` | score CSV 输出路径。 |
| `fem_dataset` | ADS workspace data 下的 FEM dataset 路径。 |
| `log_file` | flow log 路径。 |
| `state` | state.json 路径。 |
| `artifact_manifest` | artifact_manifest.json 路径。 |

`flags` 建议字段：

```text
dry_run
skip_import
reuse_layout
skip_setup
overwrite_setup
prepare_only
skip_fem
skip_score
score_only
force
```

`write_safety` 建议字段：

| 字段 | 说明 |
|---|---|
| `policy_version` | 写入安全策略版本，例如 `ads_write_safety_v1`。 |
| `profile_id` | 当前 ADS profile。 |
| `workspace` | ADS workspace 路径。 |
| `library` | ADS library。 |
| `template_cell` | 受保护模板 cell。 |
| `target_cell` | 当前写入目标 cell。 |
| `target_is_template` | target cell 是否等于 template cell。 |
| `force` | 是否显式允许受保护写入。 |
| `operation` | 写入操作名称，例如 `candidate_flow`。 |
| `allowed` | safety gate 是否允许该操作。 |

规则：

- `profile_snapshot` 必须保存运行时实际生效 profile，而不是只保存 profile 名称。
- `target_cell` 不得等于 `template_cell`，除非显式 `force=true` 且任务记录说明原因。
- `overwrite_setup=true` 只能作用于 `target_cell`，不得作用于 template cell。
- 任何真实 ADS workspace 写入前必须先写入或打印 manifest 核心字段。
- 写入 ADS workspace 的脚本必须记录 `write_safety` 或引用等价 safety policy 记录。

## 5. Artifact Manifest Schema

文件：

```text
artifact_manifest.json
```

当前版本：

```text
schema_version = 1.0
```

必填字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | string | 固定为 `1.0`。 |
| `run_id` | string | 当前 run ID。 |
| `artifacts` | array | artifact 列表。 |
| `updated_at` | string | ISO 时间。 |

Artifact entry 必填字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | string | artifact 类型。 |
| `path` | string/null | 文件路径或外部引用。 |
| `exists` | boolean | 文件是否存在。 |
| `hash` | string/null | 文件 sha256。不存在或外部引用为空。 |
| `producer` | string/null | 生成脚本或外部来源。 |

当前允许 artifact 类型：

```text
dxf
svg
params
drc
tuning_table
rfpro_csv
fem_dataset
fem_txt
score
summary
log
state
run_manifest
report_html
report_pdf
manual_intervention
```

规则：

- 文件型 artifact 必须尽量记录 sha256。
- ADS workspace 内部对象可以用 path/ref 表达，例如 `BFP_lib:cell:layout`。
- 报告引用图片、score、曲线和版图时，必须能在 artifact manifest 中找到对应项或上游 run。

## 6. Score 与 Summary 绑定规则

P0-04 后，score CSV 每行必须写入：

```text
run_id
project_id
round_id
candidate_id
profile_id
target_profile_id
score_version
status
error_class
failed_step
elapsed_s
```

P0-05 后，sweep summary 每行必须写入：

```text
run_id
profile_id
target_profile_id
score_version
status
error_class
failed_step
elapsed_s
```

合并优先级：

```text
state.json > run_manifest.json > score.csv > candidate plan row
```

## 7. 幂等和 Resume 规则

- 相同 `run_id` 不得静默覆盖成功结果。
- 相同输入 hash、相同 profile、相同 target profile 的已完成 FEM 结果可以复用。
- 参数、profile、substrate、emSetup 或 target profile 改变时必须生成新 run。
- `state.status=failed` 时，可以从 `failed_step` 判断恢复入口。
- `stage/status/error_class` 的允许值必须与 `flow/FLOW_RUN_STATE_MACHINE.md` 和 `src/simads/runtime/state_machine.py` 一致。
- `score_only` 只能读取已有 `rfpro_csv` 或 `fem_dataset`，不得修改 ADS layout。
- `reuse_layout` 必须在 manifest 中记录，并保留 layout 来源。

## 8. P0 代码落地检查

当前已落地：

```text
tools/run_ads_filter_candidate.py 输出 state/run_manifest/artifact_manifest 初版。
src/simads/runtime/manifest.py 提供 run_id、hash、state 和 manifest helper。
src/simads/runtime/state_machine.py 提供 stage/status/error_class 允许值和校验。
src/simads/safety 提供 ADS workspace 写入安全 gate。
```

仍需完成：

```text
baseline freeze manifest。
```
