# JSON 输出命名规范

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_JSON_ARTIFACT_NAMING.md`
Related: `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Last updated: 2026-08-09
Owner: ADS Automation

本文档定义 SIM/HFSS 自动化流程中 JSON 文件的命名边界。目标是让 Git 跟踪规则可以稳定区分“可复现设计输入/归档摘要”和“本机运行日志/诊断缓存”，而不是依赖文件格式做区分。

## 1. 基本原则

- 可复现、可复核、会进入报告或下一轮仿真的 JSON 才能跟踪。
- AEDT/HFSS 单次运行 payload、traceback、API 原始 dump、inspect/probe 诊断结果默认不跟踪。
- 正式可查看、可归档、可进入报告的结构化产物统一使用 `.json`；用后缀表达语义，例如 `_summary.json`、`_metrics.json`、`_run_log.json`。
- JSONL 只允许作为本地生命周期事件流，因为它适合逐行追加；不作为报告或归档产物，也不要求 IDE 格式化。
- `--output` 明确传入的路径由调用方负责命名；新脚本和新流程必须使用本文定义的后缀。
- 大型 API 原始提取文件不得直接作为报告依据，必须先蒸馏为 `_summary.json`、`_metrics.json` 或 `_manifest.json`。

## 2. 可跟踪 JSON 后缀

这些文件可以在目录本身属于 curated/baseline/report 时跟踪：

| 后缀/文件名 | 用途 |
|---|---|
| `*_layout.json` | 候选版图或元素级版图输入。默认生成池仍忽略，只有精选候选显式放开。 |
| `*_params.json` | 生成器参数快照。默认生成池仍忽略，基线或精选候选可跟踪。 |
| `*_summary.json` | 人工或脚本蒸馏后的摘要。 |
| `*_metrics.json` | 评分、TDR、Smith、S 参数指标。 |
| `*_manifest.json` | 仿真、归档、baseline、artifact manifest。 |
| `*_comparison.json` | 基线/候选/实板仿真的对比摘要。 |
| `*_score_summary.json` | 多端口或多指标评分汇总。 |
| `run_manifest.json`、`artifact_manifest.json`、`state.json` | 标准 run 契约文件。 |
| `baseline_index.json`、`baseline_manifest.json`、`simulation_manifest.json` | baseline 或仿真批次索引。 |

示例：

```text
projects/bfp_real_board_hfss/layouts/candidates/core_y_offset_p0p10/bfp_core_y_offset_p0p10_layout.json
projects/bfp_real_board_hfss/layouts/candidates/core_y_offset_p0p10/bfp_core_y_offset_p0p10_summary.json
archive/sp8t/20260808/baselines/rf_in_cutout_0201_100pf_baseline_manifest.json
```

## 3. 本地忽略 JSON 后缀

这些文件属于运行日志、诊断或失败 payload，必须保持本地忽略：

| 后缀/模式 | 用途 |
|---|---|
| `*_run_log.json` | 单次工具运行的完整 payload，包括失败 traceback。 |
| `*_dry_run_log.json` | dry-run 完整 payload。 |
| `*_execute_log.json` | execute 模式完整 payload。 |
| `*_operation_log.json` | 修改工程或批处理操作日志。 |
| `*_diagnostic.json` | 临时诊断结果。 |
| `*_inspect.json`、`inspect_*.json` | AEDT/HFSS inspect/probe 输出。 |
| `*_probe.json` | 临时探测输出。 |
| `*_api_extract_raw.json` | 原始 API 提取缓存。 |
| `extract_layout.json` | 历史原始版图提取文件名，后续迁移到 `*_api_extract_raw.json`。 |
| `*_owner.json` | 后台生命周期/进程归属记录。 |
示例：

```text
projects/bfp_real_board_hfss/results/candidates/s11_6g_tune_r1_eval/run_existing_run_log.json
projects/bfp_real_board_hfss/results/candidates/s11_6g_tune_r1_eval/inspect_ports.json
projects/bfp_real_board_hfss/results/candidates/s11_6g_tune_r1_eval/bfp_api_layout_api_extract_raw.json
```

## 4. 本地 JSONL 事件流

JSONL 是“一行一个 JSON 对象”的事件流，不是一个完整 JSON 文档。多数 IDE 可以做基础高亮，部分 IDE 需要选择 JSON Lines 语言模式或插件；整体格式化通常不如 `.json` 稳定。

因此命名规范不把 JSONL 当作可归档产物。若工具需要逐阶段追加生命周期事件，可以生成本地 sidecar：

```text
run_existing_run_log.json
run_existing_events.jsonl
```

`*_events.jsonl` 和历史 `*.events.jsonl` 均由 `.gitignore` 忽略。需要归档时，从主运行日志或事件流中提取稳定字段，生成 `.json` 摘要文件。

## 5. 新脚本命名 API

HFSS 相关新脚本应优先使用：

```python
from simads.hfss.artifact_names import event_log_path_for_json, json_artifact_path

run_log = json_artifact_path(out_dir, "run_existing", "run_log")
event_log = event_log_path_for_json(run_log)
summary = json_artifact_path(out_dir, "rf_in_cutout_0201_100pf", "summary")
```

已注册 kind 由 `simads.hfss.artifact_names.JSON_KIND_SUFFIXES` 管理，避免每个工具自行拼接后缀。

## 6. 旧文件迁移

历史命名可以继续读取，但新输出应逐步迁移：

| 旧名 | 新名 |
|---|---|
| `run_existing.json` | `run_existing_run_log.json` |
| `export_only.json` | `export_only_run_log.json` |
| `run_existing.events.jsonl` | `run_existing_events.jsonl` |
| `export_only.events.jsonl` | `export_only_events.jsonl` |
| `extract_layout.json` | `<candidate>_api_extract_raw.json` |
| `inspect_ports.json` | `ports_inspect.json` 或继续本地忽略 |

若某个历史运行结果确实需要归档，必须从运行日志中提取稳定字段，生成 `_summary.json`、`_metrics.json` 或 `_manifest.json` 后再跟踪。

## 7. 当前待办

- 将 ADS 侧 `--json-out` 也逐步接入同一命名 helper。
- 为 results 目录增加轻量检查脚本，扫描误命名的运行日志 JSON。
- 后续模块化下沉时，所有 HFSS 工具统一从 `simads.hfss.artifact_names` 获取 JSON/JSONL 文件名。

## 8. 2026-08-09 审查处理记录

本轮新增 `tools/audit_json_artifacts.py`，用于重复审查已跟踪 JSON/JSONL 是否符合命名和跟踪策略。

处理结果：

- 已跟踪 JSON 均可按 UTF-8/UTF-8-SIG 正常解析。
- 从 Git 索引取消跟踪 204 个明确的本地运行/诊断 JSON，工作区文件保留不删除。
- 取消跟踪范围包括 `run*.json`、`replace*.json`、`dry_run/execute/nosave` payload、`probe/inspect/diag` 诊断、AEDB `*_hints.json` 启发式 dump。
- `config/` 下 JSON 不按文件名中的 `probe` 等词误判为运行日志，继续作为配置跟踪。
- 剩余 `legacy_or_unclear_json` 暂不批量改名，避免破坏现有报告引用；后续若需要归档，应逐个迁移到 `_summary.json`、`_metrics.json`、`_manifest.json` 或 `_comparison.json`。

复查命令：

```text
python tools/audit_json_artifacts.py --format markdown
```
