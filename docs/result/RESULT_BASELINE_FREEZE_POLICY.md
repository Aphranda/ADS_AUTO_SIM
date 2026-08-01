# Baseline Freeze Policy

Status: Active
Domain: RESULT
Canonical: `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`
Related: `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`, `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真项目中的 baseline freeze、复测、漂移判定和勘误规则。baseline 是后续优化、报告和环境漂移判断的参考点；冻结后不得被普通 sweep、候选优化或报告改写覆盖。

## 1. 定义

| 对象 | 定义 |
|---|---|
| Baseline | 当前项目中用于比较的参考候选，可以是初始模板、历史最好点或正式发布点。 |
| Frozen baseline | 已冻结的 baseline，具备参数、layout、score、目标 profile、环境和漂移容差记录。 |
| Baseline repeat | 在当前环境中复跑 frozen baseline，用于判断 ADS/profile/substrate/emSetup 是否漂移。 |
| Drift | 复跑结果相对 frozen 指标超过容差，且无法用已记录变更解释。 |
| Errata | 冻结记录中的文字、路径、hash 或单位勘误；不得改变原始冻结结论。 |

## 2. 状态

| 状态 | 含义 | 允许操作 |
|---|---|---|
| `Draft` | 候选可能作为 baseline，但尚未冻结。 | 可修改参数、补跑、重评估。 |
| `Proposed` | 已通过目标 profile 初筛，准备冻结。 | 只允许补齐追溯文件和人工复核。 |
| `Frozen` | 已作为正式 baseline。 | 只允许引用、复测和补勘误。 |
| `Superseded` | 已被新的 frozen baseline 替代。 | 保留历史，不删除。 |
| `Deprecated` | 因材料、阶数、拓扑或目标变更不再适用。 | 保留历史，不参与新比较。 |

## 3. 冻结前置条件

一个候选进入 `Frozen` 前，至少满足：

| 条件 | 要求 |
|---|---|
| identity | 有唯一 `baseline_id`、`project_id`、`candidate_id`、`device_type`。 |
| source | 有参数表、layout 文件、仿真结果、score CSV 或 legacy 来源说明。 |
| target | 明确 `target_profile_id` 和 `score_version`。 |
| material | 明确 substrate、材料、层叠、参考地、铜厚和 profile。 |
| layout trace | 记录 params、DXF/SVG/GDS、layout image 或 geometry hash。 |
| result trace | 记录 dataset/TXT/CSV、score 文件和关键指标。 |
| repeatability | 若存在重复点，记录重复点一致性；若是 legacy 数据，说明缺失的 run manifest。 |
| drift tolerance | 定义关键指标容差，不允许只写“基本一致”。 |
| protection | 确认普通候选流程不会覆盖 baseline cell、template cell 或 frozen result。 |

当前 FR4 7 阶交指分支的 frozen baseline：

```text
baseline_id: i7_fr4_baseline_freeze_20260801
representative_candidate_id: i7_fr4_r3_base
target_profile_id: fr4_25db_rl6
score_version: fr4_i7_score_v1
baseline_record:
  projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md
```

## 4. 冻结记录字段

建议 Markdown 和 JSON 同时维护。Markdown 用于人工审查，JSON 用于脚本读取。

| 字段 | 要求 |
|---|---|
| `schema_version` | baseline 记录 schema 版本。 |
| `baseline_id` | 全局唯一，建议含项目、候选和日期。 |
| `status` | `Frozen` / `Superseded` / `Deprecated`。 |
| `project_id` | 项目边界，例如 `bfp_6_8g_i7_fr4`。 |
| `device_type` | 例如 `filter.interdigital`、`filter.folded_sir`。 |
| `representative_candidate_id` | 代表候选。 |
| `baseline_candidates` | 重复候选或等价候选列表。 |
| `profile_id` | 生成该结果的 profile；legacy 数据需写明 `legacy_migrated`。 |
| `ads_workspace` | ADS workspace 路径。 |
| `ads_library` | ADS library 名称。 |
| `template_cell` | 生成或复跑时使用的模板 cell。 |
| `substrate` | ADS substrate 名称或材料配置。 |
| `target_profile_id` | 目标约束。 |
| `score_version` | 评分版本。 |
| `parameters` | 关键几何参数和单位。 |
| `metrics` | 关键 S 参数、约束 margin 和状态。 |
| `layout` | params/DXF/SVG/image/hash。 |
| `drift_tolerance` | 复测容差。 |
| `freeze_rules` | 冻结后的使用规则。 |

## 5. 复测触发条件

出现以下任一情况，新候选与历史结果比较前必须先执行 baseline repeat：

| 触发 | 说明 |
|---|---|
| ADS 版本变化 | ADS Update、RFPro、FEM solver 或 Python API 变化。 |
| profile 变化 | home/company 路径、host Python、ADS Python 或 workspace 变化。 |
| substrate 变化 | Er、tanD、介质厚度、铜厚、参考地、via stack 变化。 |
| emSetup 变化 | 频段、网格、边界、端口、via、airbox、solver 设置变化。 |
| template cell 变化 | 复制来源、层映射、端口放置或布局模板变化。 |
| dataset/export 变化 | DDS/TXT/CSV 导出接口或插值逻辑变化。 |
| score_version 变化 | 目标函数、硬约束、采样点或 margin 公式变化。 |
| 发布报告前 | 报告声称候选优于 baseline 时，需要最近一次有效 repeat。 |

## 6. Baseline Repeat 流程

```text
1. 读取 frozen baseline JSON/Markdown
2. 检查 profile、workspace、library、template、substrate
3. 确认 target candidate cell 不等于 template cell
4. 使用新的 run_id 复跑代表 baseline
5. 导出 dataset/TXT/CSV 并重新评分
6. 与 frozen metrics 按 drift_tolerance 比较
7. 写入 repeat summary、run manifest、artifact manifest 和 round index
8. 判定 drift status
```

复跑不得覆盖 frozen baseline 原始文件。建议输出到：

```text
projects/<project_id>/results/baselines/<repeat_id>/
```

## 7. 漂移判定

每个关键指标计算：

```text
delta = repeat_metric - frozen_metric
abs_delta = abs(delta)
drifted = abs_delta > tolerance
```

判定状态：

| 状态 | 条件 | 后续动作 |
|---|---|---|
| `repeat_pass` | 所有关键指标在容差内。 | 允许继续比较新候选。 |
| `repeat_warn` | 只有非关键指标轻微超差，且不影响目标判断。 | 记录原因，必要时再复跑一次。 |
| `repeat_drifted` | 任一关键指标超过容差。 | 暂停新候选比较，排查环境或设置。 |
| `repeat_invalid` | 复跑流程、端口、导出或评分失败。 | 不得用于漂移判断。 |

当前 FR4 7 阶交指 baseline 容差沿用 frozen 记录：

| 指标 | 容差 |
|---|---:|
| `S21@5GHz` | ±1.0 dB |
| `S21@6GHz` | ±0.5 dB |
| `S21@8GHz` | ±0.5 dB |
| `passband_min_s21` | ±0.5 dB |
| `passband_ripple` | ±0.5 dB |
| `worst_s11_6_8` | ±0.5 dB |
| `worst_s22_6_8` | ±0.5 dB |

## 8. 新候选比较规则

新候选宣称优于 baseline 前，必须满足：

| 检查项 | 要求 |
|---|---|
| repeat valid | 当前环境最近一次 baseline repeat 为 `repeat_pass`，或能证明环境未变。 |
| same target | 使用同一 `target_profile_id` 和 `score_version`；否则不能直接比较综合分。 |
| same branch | 材料、阶数、拓扑不同的分支不得混用 baseline 结论。 |
| hard constraints | 新候选必须保持 target profile 的硬约束。 |
| objective improvement | 改善方向与目标 profile 一致，例如保持阻带和通带时改善回损。 |
| manufacturing gate | 满足当前制造规则和 DRC，不允许不可制造最优。 |
| artifact trace | layout、dataset、score、manifest 和报告图表可追溯。 |

不同材料、阶数或拓扑应建立独立 baseline。例如 FR4 7 阶交指和 RO4350B 9 阶滤波器应分开维护。

## 9. 勘误规则

Frozen baseline 只允许补勘误，不允许改写结论。

| 允许 | 不允许 |
|---|---|
| 修正拼写、路径显示、单位说明。 | 修改 frozen 指标数值。 |
| 补充缺失 hash、文件链接或 legacy 说明。 | 用新复跑结果覆盖旧 frozen 结果。 |
| 追加 errata 章节说明错误来源。 | 删除不利指标或失败说明。 |
| 标记 Superseded 并引用新 baseline。 | 在原 baseline_id 下改变材料、阶数或目标 profile。 |

若确实需要替换 baseline，应创建新的 `baseline_id`，并把旧记录标记为 `Superseded`，保留旧文件。

## 10. 报告引用规则

报告包含优化结论时，必须引用：

```text
baseline_id:
baseline_record:
baseline_repeat_id:
target_profile_id:
score_version:
repeat_status:
candidate_run_id:
candidate_score:
```

若没有有效 baseline repeat，报告只能描述候选自身指标，不能声称相对 frozen baseline 改善。

