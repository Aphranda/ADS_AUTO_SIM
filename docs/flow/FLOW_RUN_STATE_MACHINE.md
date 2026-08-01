# ADS 自动仿真运行状态机

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_RUN_STATE_MACHINE.md`
Related: `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/test/TEST_STRATEGY.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真闭环的 run state machine。目标是让每个候选从版图、导入、emSetup、FEM、导出、评分到报告的状态可追溯、可恢复、可判定是否允许复用。

## 1. 策略版本

```text
state_machine_version = ads_run_state_machine_v1
```

当前代码入口：

```text
src/simads/runtime/state_machine.py
```

## 2. 状态字段

`state.json` 和 `run_manifest.json` 使用两个概念：

| 字段 | 含义 | 示例 |
|---|---|---|
| `stage` | 当前或最终流程阶段。 | `ads_imported`、`sim_running`、`scored` |
| `status` | 当前 run 的生命周期状态。 | `running`、`completed`、`failed` |

`stage` 描述“走到哪一步”，`status` 描述“这次 run 处于什么状态”。两者不得混用，例如 `scored` 是 stage，不是 status。

## 3. 允许 Stage

| Stage | 说明 | 主要输出 | 可恢复入口 |
|---|---|---|---|
| `planned` | run 已创建，尚未执行实质步骤。 | `state.json`、`run_manifest.json` | 从头开始。 |
| `layout_ready` | 候选版图文件已生成或已确认存在。 | DXF、params、SVG/DRC 可选 | 从 ADS import 开始。 |
| `ads_imported` | DXF 或既有 layout 已进入 ADS cell，端口已放置。 | ADS layout cell | 从 emSetup clone 开始。 |
| `emsetup_ready` | emSetup 已克隆并 patch 到目标 cell。 | target `em%Setup` | 从 RFPro FEM 开始。 |
| `rfpro_ready` | RFPro view 已准备好。 | ADS RFPro view | 从 FEM analysis 开始。 |
| `sim_running` | RFPro/FEM 正在运行或刚进入运行阶段。 | FEM job / RFPro project | 若失败，通常从 FEM 重跑。 |
| `dataset_exported` | S 参数数据已导出到 CSV 或 dataset 可读。 | RFPro CSV / FEM dataset / TXT | 从评分开始。 |
| `scored` | score CSV 已生成。 | score CSV | 可写 summary/report。 |
| `reported` | 正式报告已引用本 run。 | HTML/PDF/report manifest | 通常只读。 |
| `completed` | run 作为流程整体完成。 | 全部必要 artifact | 不默认重跑。 |
| `failed` | run 失败。 | failed state、error_class、failed_step、log | 按 failed_step 判断。 |

## 4. 允许 Status

| Status | 含义 | 是否终态 |
|---|---|---|
| `planned` | run 已登记但未执行。 | 否 |
| `running` | run 正在执行某个 stage。 | 否 |
| `completed` | run 已完成当前目标，例如 `--skip-fem` 到 emSetup、完整 scored 或 reported。 | 是 |
| `failed` | run 失败，需要人工或自动恢复。 | 是 |
| `skipped` | run 被策略跳过，例如已存在等价结果。 | 是 |

## 5. 失败分类

允许 `error_class`：

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

分类原则：

- 环境、路径、Python、ADS 安装问题归入 `ENV_ERROR` 或 `PROFILE_ERROR`。
- DXF、端口、layout 几何问题归入 `LAYOUT_ERROR`。
- emSetup 克隆、XML patch、substrate 引用问题归入 `EMSETUP_ERROR`。
- RFPro/FEM API、仿真运行、dataset 生成问题归入 `RFPRO_ERROR`。
- 写入安全 gate 拦截归入 `SAFETY_ERROR`。

## 6. Resume 规则

| failed_step | 建议恢复入口 | 默认动作 |
|---|---|---|
| `1. DXF import and P1/P2 pins` | `ads_imported` | 重新导入 DXF 或检查既有 layout。 |
| `2. Clone/patch FEM setup` | `emsetup_ready` | 重新 clone/patch emSetup。 |
| `3. RFPro FEM` | `sim_running` | 保留 layout/emSetup，重跑 FEM。 |
| `4a. Export FEM fitted dataset TXT` | `dataset_exported` | 重新导出 TXT 或切换 score source。 |
| `4. Score S-parameters` | `scored` | 复用已有结果，仅重新评分。 |
| `run_ads_filter_candidate.py` | `planned` | 按异常分类判断从头或人工处理。 |

自动 resume 前必须检查：

- `run_manifest.json` 存在且 `run_id` 一致。
- 输入文件 hash、profile、target profile、template cell、target cell 未变化。
- 若涉及 ADS workspace 写入，必须重新通过 `flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`。
- 若上次失败为 `SAFETY_ERROR`，不得自动加 `--force`。

## 7. 幂等规则

- 相同 `run_id` 的 `status=completed` 结果不得静默覆盖。
- 参数、profile、substrate、emSetup、target profile 或 score version 变化时必须生成新 run。
- `score_only` 只允许从 `dataset_exported` 或既有结果进入 `scored`，不得修改 ADS layout。
- `reuse_layout` 必须在 manifest 中记录 layout 来源。
- `--skip-fem` 可在 `emsetup_ready` 以 `status=completed` 收尾，但不得宣称完成 FEM 或评分。

## 8. 代码落地

当前已落地：

```text
src/simads/runtime/state_machine.py
src/simads/runtime/manifest.py
tools/run_ads_filter_candidate.py
tools/run_ads_filter_sweep.py
```

`write_state()` 和 `write_run_manifest()` 会校验 `stage/status/error_class`。如果新增 stage、status 或 error class，必须先更新 `state_machine.py` 和本文档。
