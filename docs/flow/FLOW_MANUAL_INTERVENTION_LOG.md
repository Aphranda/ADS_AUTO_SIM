# Manual GUI Intervention Log

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_MANUAL_INTERVENTION_LOG.md`
Related: `docs/flow/FLOW_RUN_STATE_MACHINE.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真流程中的人工 GUI 介入记录格式。人工 ADS GUI 操作允许用于复核、临时修补、最终确认或 API fallback，但必须留下可追溯记录；任何改变 ADS cell、emSetup、substrate、layout、端口或导出数据的人工操作，都不能成为隐性输入。

## 1. 适用场景

| 场景 | 是否必须记录 | 说明 |
|---|---|---|
| 手动导入 DXF/GDS | 是 | 包括导入单位、layer map、shape 转换设置。 |
| 手动放置或修正端口 | 是 | 包括端口位置、宽度、参考地和端口编号。 |
| 手动创建或修改 via/ground | 是 | 包括孔、焊盘、via stack 和接地层。 |
| 手动修改 emSetup/RFPro | 是 | 包括频段、mesh、边界、substrate、端口设置。 |
| 手动点击 simulate | 是 | 包括 cell、setup、启动时间和导出结果路径。 |
| 手动导出 DDS/TXT/CSV | 是 | 包括选中表格、变量名、导出单位和文件路径。 |
| GUI 只读查看 | 建议 | 若影响后续判断或报告结论，应记录。 |
| 清理残留进程、stale lock 或半成品 cell | 是 | 属于高风险介入。 |

## 2. 介入等级

| 等级 | 定义 | 对数据使用的影响 |
|---|---|---|
| `L0_readonly_review` | 只读查看 GUI、截图、核对结果。 | 可作为复核证据，不改变 run。 |
| `L1_manual_export` | 手动导出数据，但不修改 ADS 设计。 | 可用于评分，必须记录导出方法。 |
| `L2_manual_patch` | 手动修补 candidate cell、端口、via、emSetup 或 substrate。 | run 必须标记 manual intervention，训练集需说明。 |
| `L3_destructive_cleanup` | 删除/覆盖 cell、清理残留、修复 workspace。 | 必须有原因、范围和风险记录；不能影响 template/baseline。 |

## 3. 记录位置

每次介入建议同时保留项目级索引和 run 级记录。

```text
projects/<project_id>/runs/<run_id>/manual_intervention.md
projects/<project_id>/runs/<run_id>/manual_intervention.json
projects/<project_id>/docs/manual_intervention_index.md
```

如果 run 目录尚未创建，可先记录在：

```text
projects/<project_id>/results/manual_interventions/<date>_<short_id>/
```

后续 run_id 确定后再反向引用。

## 4. Markdown 模板

```markdown
# Manual GUI Intervention

Status: Active
Domain: FLOW
Canonical: `projects/<project_id>/runs/<run_id>/manual_intervention.md`
Related: `run_manifest.json`, `artifact_manifest.json`, `state.json`
Last updated: YYYY-MM-DD
Owner: <name or role>

## Summary

| Field | Value |
|---|---|
| intervention_id | `<project_id>_<run_id>_manual_<YYYYMMDD_HHMMSS>` |
| project_id | `<project_id>` |
| run_id | `<run_id or pending>` |
| candidate_id | `<candidate_id>` |
| profile_id | `<home/company/...>` |
| ADS workspace | `<path>` |
| library | `<library>` |
| cell | `<cell>` |
| setup view | `<emSetup/RFPro view>` |
| intervention_level | `L0_readonly_review/L1_manual_export/L2_manual_patch/L3_destructive_cleanup` |
| operator | `<name>` |
| start_time | `<YYYY-MM-DD HH:MM:SS>` |
| end_time | `<YYYY-MM-DD HH:MM:SS>` |

## Reason

- Trigger:
- Expected automated behavior:
- Why manual action was needed:

## Actions

| Step | Object | Action | Before | After | Evidence |
|---:|---|---|---|---|---|
| 1 |  |  |  |  |  |

## Files

| Type | Path | SHA256 | Note |
|---|---|---|---|
| screenshot |  |  |  |
| exported_txt |  |  |  |
| exported_csv |  |  |  |
| log |  |  |  |

## Impact

| Item | Value |
|---|---|
| changed_layout | yes/no |
| changed_ports | yes/no |
| changed_emsetup | yes/no |
| changed_substrate | yes/no |
| changed_dataset | yes/no |
| affects_training_dataset | yes/no |
| requires_baseline_repeat | yes/no |
| reusable_as_template_update | yes/no |

## Follow-up

- Required automation fix:
- Required documentation update:
- Required rerun:
- Reviewer:
```

## 5. JSON Schema 草案

```json
{
  "schema_version": "manual_intervention_v1",
  "intervention_id": "",
  "project_id": "",
  "run_id": null,
  "candidate_id": "",
  "profile_id": "",
  "workspace": "",
  "library": "",
  "cell": "",
  "setup_view": "",
  "intervention_level": "L1_manual_export",
  "operator": "",
  "start_time": "",
  "end_time": "",
  "reason": {
    "trigger": "",
    "expected_automated_behavior": "",
    "manual_need": ""
  },
  "actions": [
    {
      "step": 1,
      "object": "",
      "action": "",
      "before": "",
      "after": "",
      "evidence": ""
    }
  ],
  "files": [
    {
      "type": "screenshot",
      "path": "",
      "sha256": "",
      "note": ""
    }
  ],
  "impact": {
    "changed_layout": false,
    "changed_ports": false,
    "changed_emsetup": false,
    "changed_substrate": false,
    "changed_dataset": false,
    "affects_training_dataset": false,
    "requires_baseline_repeat": false,
    "reusable_as_template_update": false
  },
  "follow_up": {
    "automation_fix": "",
    "documentation_update": "",
    "required_rerun": "",
    "reviewer": ""
  }
}
```

## 6. Manifest 标记

只要存在人工介入，`run_manifest.json` 建议增加兼容字段：

```json
{
  "manual_intervention": {
    "has_manual_intervention": true,
    "intervention_level": "L1_manual_export",
    "intervention_log": "manual_intervention.md",
    "affects_training_dataset": false,
    "requires_baseline_repeat": false
  }
}
```

如果人工操作改变了 layout、端口、emSetup 或 substrate，则该 run 不得默认进入训练集，除非训练集记录 `candidate_source=manual_patch` 或 `excluded_reason` 已说明。

## 7. 高风险操作规则

| 操作 | 规则 |
|---|---|
| 覆盖 template cell | 禁止普通流程执行；若确需模板升级，必须新建模板版本。 |
| 删除 candidate cell | 只能删除 target candidate，不能扩大到 library/template/baseline。 |
| 修改 substrate | 必须记录原始文件、备份、diff、profile 和 baseline repeat 需求。 |
| 手动改 emSetup | 必须记录变更项；若用于后续自动化，应提升为新 template cell。 |
| 手动导出数据 | 必须记录 DDS/table/变量名和导出路径。 |
| 清理 stale lock | 必须记录 PID、进程检查、日志时间戳和清理原因。 |

## 8. 训练集和报告影响

| 情况 | 训练集处理 | 报告处理 |
|---|---|---|
| 只读 GUI 复核 | 可正常使用。 | 可作为复核证据引用。 |
| 手动导出 TXT/CSV | 可使用，但必须记录导出路径和变量名。 | 报告注明导出来源。 |
| 手动修端口或 emSetup | 默认排除，除非作为正式模板变更重新跑。 | 不直接作为自动化闭环结果。 |
| 手动清理后重跑 | 使用重跑后的 manifest。 | 报告引用最终有效 run。 |

