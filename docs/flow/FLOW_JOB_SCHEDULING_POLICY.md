# ADS Job Scheduling Policy

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`
Related: `docs/flow/FLOW_RUN_STATE_MACHINE.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/test/TEST_STRATEGY.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真任务的调度策略，覆盖 license、并发、workspace 锁、超时、失败熔断、候选优先级、resume 和残留处理。目标是在后续批量优化中避免多个任务互相覆盖 ADS workspace、浪费 FEM license 或因单个异常候选卡住整轮迭代。

## 1. 调度原则

| 原则 | 要求 |
|---|---|
| 单 workspace 写入串行 | 同一个 ADS workspace 的 layout 导入、cell 删除、emSetup clone、FEM 启动默认串行执行。 |
| 先 profile 后仿真 | 真实 ADS/FEM 前必须先通过 profile check 和 ADS API smoke。 |
| 先 baseline 后候选 | profile、substrate、emSetup、ADS 版本或模板变更后，先复跑 frozen baseline，再跑新候选。 |
| 先单点后批量 | 新脚本、新模板、新层叠或新拓扑先跑一个候选，成功后再放大到 batch。 |
| 失败可追溯 | 失败候选必须写入 `state.json`、`run_manifest.json` 和 summary，不得静默丢弃。 |
| 默认不覆盖 | 已完成 run 默认复用；参数、profile、template 或 target profile 变化必须生成新 run_id。 |

## 2. 任务类型

| 类型 | 是否占用 ADS workspace | 是否占用 FEM/license | 默认并发 | 说明 |
|---|---:|---:|---:|---|
| docs/schema 更新 | 否 | 否 | 多个 | 文档和 JSON schema 维护。 |
| layout 生成 | 否 | 否 | 多个 | 纯 Python 生成 DXF/SVG/params/DRC。 |
| score/plot 分析 | 否 | 否 | 多个 | 基于已导出的 dataset/TXT/CSV 分析。 |
| ADS profile/API smoke | 只读 | 可能占用轻量 ADS 运行时 | 1 | 检查环境、library、cell、substrate、dataset API。 |
| ADS layout 导入 | 是 | 否 | 1/workspace | 写 candidate cell，必须通过 safety gate。 |
| emSetup clone/patch | 是 | 否 | 1/workspace | 从 template 复制设置，不覆盖 template。 |
| FEM/RFPro 仿真 | 是 | 是 | 1/workspace | 默认最重任务，必须串行。 |
| dataset export | 是或只读 | 否 | 1/workspace | 依赖 ADS dataset/DDS/TXT 导出状态。 |

## 3. Workspace 锁

同一个 ADS workspace 下，以下步骤必须持有 workspace 写锁：

```text
ads_imported
emsetup_ready
rfpro_ready
sim_running
dataset_exported
```

锁策略建议：

| 项 | 规则 |
|---|---|
| lock_id | `profile_id + workspace_path_hash`。 |
| lock_file | 后续代码化时建议放在 `projects/<project_id>/runs/.locks/<lock_id>.json`。 |
| owner | 记录 `run_id`、`candidate_id`、host name、PID、start time、stage。 |
| stale 判断 | 只有确认 PID 不存在、ADS/RFPro 进程无对应任务、dataset/log 时间戳不再变化时，才能清理 stale lock。 |
| 强制清理 | 必须人工确认并写入 manual intervention log。 |

当前 P1 阶段先以流程约束为准；P2 再实现文件锁和进程探测。

## 4. License 和并发

在未完成 license 探测 API 前，采用保守并发。

| 资源 | 默认策略 |
|---|---|
| ADS workspace 写入 | `max_workspace_writers = 1`。 |
| FEM/RFPro | `max_fem_jobs_per_workspace = 1`。 |
| ADS API smoke | 与 FEM 不并发。 |
| 纯 Python layout/score | 可并发，但不得写同一个 run_dir。 |
| 多 workspace | 只有确认 license、模板和输出目录隔离后，才能并发。 |

公司电脑当前建议：

```text
profile_id: company
workspace: D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
library: 6-8G_Fillter_lib
default_max_fem_jobs: 1
default_batch_size_before_review: 1 to 3
```

## 5. 候选优先级

批量候选不应按 CSV 顺序盲跑。建议按以下优先级排序：

| 优先级 | 候选类型 | 说明 |
|---:|---|---|
| 1 | baseline drift check | 环境或模板变化后先确认 baseline 是否漂移。 |
| 2 | smoke candidate | 每轮先选 1 个低风险候选验证流程。 |
| 3 | feasible improvement | 预测满足硬约束且相对 baseline 有改进概率的候选。 |
| 4 | diversity candidate | 与当前最优点有足够参数距离，用于防止局部收敛。 |
| 5 | risky exploration | 接近制造下限、回损风险高或模型不确定性大的候选。 |

候选选择应记录：

```text
selection_reason:
baseline_relation:
predicted_constraints:
expected_improvement:
diversity_group:
risk_flags:
```

## 6. 超时策略

超时不是直接删除或覆盖的理由。任务超时后应进入排查状态，先判断是否仍在运行。

| 阶段 | 建议超时 | 超时后处理 |
|---|---:|---|
| layout 生成/DRC | 2 min | 标记 `failed`，检查参数或几何生成器。 |
| ADS import | 5 min | 检查 DXF、layer map、unit、ADS 日志。 |
| emSetup clone/patch | 5 min | 检查 template cell、target cell、safety gate。 |
| FEM/RFPro 启动 | 10 min | 检查 license、RFPro 日志、进程。 |
| FEM/RFPro 仿真 | 60 min 起 | 检查 dataset/log 时间戳；仍变化则继续等待或人工决策。 |
| dataset export | 10 min | 检查 DDS/TXT/CSV 导出接口和 dataset 名称。 |
| scoring | 2 min | 检查导出文件格式和目标 profile。 |

不同拓扑、网格和频点数量可能需要更长 FEM 时间。实际超时值应写入 target/project config，而不是硬编码到脚本。

## 7. 失败熔断

批量运行必须设置最大连续失败数。

| 条件 | 动作 |
|---|---|
| 连续 1 个失败 | 记录失败，继续前检查是否为候选局部问题。 |
| 连续 2 个同类失败 | 暂停扩大批量，优先检查 profile/template/import/emSetup。 |
| 连续 3 个同类失败 | 熔断本轮 batch，生成 failure summary，不再继续新候选。 |
| template/safety 失败 | 立即停止，不允许自动 `--force`。 |
| license 失败 | 停止 FEM 阶段，保留已完成 layout/import 产物。 |
| dataset/export 失败 | 不重跑 FEM 前先尝试只读导出恢复。 |

失败分类必须使用 `flow/FLOW_RUN_STATE_MACHINE.md` 中定义的 `error_class`。

## 8. Resume 规则

自动 resume 必须读取 `state.json` 和 `run_manifest.json`。

| 已完成阶段 | 可复用内容 | 下一步 |
|---|---|---|
| `layout_ready` | params、DXF、SVG、DRC | ADS import。 |
| `ads_imported` | candidate cell layout | emSetup clone/check。 |
| `emsetup_ready` | emSetup view | RFPro/FEM 设置检查。 |
| `sim_running` | 不默认覆盖 | 检查进程和 dataset/log 时间戳。 |
| `dataset_exported` | dataset/TXT/CSV | scoring。 |
| `scored` | score CSV | summary/report。 |
| `completed` | 全部产物 | 默认跳过，除非新 run_id。 |
| `failed` | 失败记录 | 根据 failed_step 决定恢复点。 |

禁止在不知道当前 stage 的情况下直接删除 candidate cell 或覆盖 run_dir。

## 9. 残留处理

残留处理是独立流程，不应混入正常 batch。

| 残留类型 | 处理 |
|---|---|
| ADS/RFPro 进程仍存在 | 先确认是否对应当前 run；不确认时不清理。 |
| dataset 文件未生成 | 检查 FEM 日志、DDS、dataset 目录和仿真是否真正结束。 |
| candidate cell 部分导入 | 通过 safety gate 后，可重新导入同名 candidate；不得影响 template。 |
| emSetup 半成品 | 只允许清理 target candidate 的 emSetup 目录。 |
| run_dir 半成品 | 保留原始 state/log，下一次生成新 run_id 或按 resume 规则继续。 |
| stale lock | 记录清理原因、时间、操作者和证据。 |

## 10. Manifest 字段建议

后续代码化 job scheduler 时，建议在 `run_manifest.json` 中增加兼容字段：

```json
{
  "scheduler": {
    "policy_version": "ads_job_scheduling_policy_v1",
    "job_type": "fem",
    "priority": 3,
    "selection_reason": "feasible_improvement",
    "workspace_lock_id": "...",
    "timeout_s": 3600,
    "max_consecutive_failures": 3,
    "resume_from_stage": null
  }
}
```

字段新增必须保持向后兼容，不得改变 P0 manifest 已冻结字段语义。

## 11. 最小批量流程

```text
1. profile check
2. ADS API smoke
3. baseline drift check if environment changed
4. select one smoke candidate
5. run layout/import/emSetup/FEM/export/score
6. review score, layout image, logs and manifest
7. if pass, expand to 2-3 candidates
8. stop after 3 same-class failures or any safety/template error
9. update round index and progress docs
```

该流程是后续优化默认入口。除非明确需要验证调度器本身，否则不应一次提交大批候选。

