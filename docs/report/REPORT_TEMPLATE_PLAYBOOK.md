# Report Template Playbook

Status: Active
Domain: REPORT
Canonical: `docs/report/REPORT_TEMPLATE_PLAYBOOK.md`
Related: `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`, `docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 滤波器报告的 HTML/PDF 模板、发布 gate、导出检查和冻结规则。报告是工程结论的表达层，不是原始数据源；报告中的结论、图、表、版图和参数必须能追溯到 run manifest、artifact manifest、score、target profile 和 baseline。

## 1. 报告类型

| 类型 | 说明 | 状态 |
|---|---|---|
| analysis note | 理论分析、参数影响、拓扑比较。 | Active 或 Draft。 |
| optimization report | 多轮参数优化、候选对比和推荐结论。 | Active，发布后可 Frozen。 |
| validation report | baseline repeat、EMSETUP 复测、制造容差或人工复核。 | Active，结论发布后可 Frozen。 |
| release report | 准备对外或打样使用的正式设计报告。 | Frozen。 |

## 2. 报告目录

项目报告默认进入：

```text
projects/<project_id>/reports/
projects/<project_id>/reports/assets/
projects/<project_id>/reports/releases/
projects/<project_id>/reports/legacy/
```

旧报告保留在 `legacy/`，新报告不得覆盖 frozen 或 legacy 报告。若需要更新结论，应生成新版本文件或维护当前分支唯一报告，并保留 release hash。

## 3. 必填元数据

HTML 报告头部或可机器读取注释中应包含：

```text
report_id:
report_title:
status:
project_id:
device_type:
material:
order:
topology:
target_profile_id:
score_version:
baseline_id:
baseline_repeat_id:
candidate_run_ids:
source_score_files:
source_manifest_files:
source_artifact_files:
last_updated:
owner:
```

## 4. 内容结构

| 章节 | 必填 | 说明 |
|---|---|---|
| 设计目标 | 是 | 通带、阻带、回损、插损、材料和制造约束。 |
| 层叠和工艺 | 是 | 材料、介质厚度、铜厚、参考地、线宽线距、孔规则。 |
| 拓扑和参数 | 是 | 结构类型、阶数、关键尺寸、参数表。 |
| 自动化流程 | 是 | layout 生成、ADS 导入、端口、emSetup、FEM、导出、评分。 |
| 仿真结果 | 是 | S21/S11/S22 曲线和关键指标表。 |
| baseline 对比 | 有优化结论时必填 | 引用 baseline_id、repeat 状态和改善判据。 |
| 制造鲁棒性 | release 必填 | nominal 和 tolerance/worst-case 说明。 |
| 人工介入 | 有则必填 | 引用 manual intervention log。 |
| 结论和限制 | 是 | 明确候选状态、风险和下一步。 |

## 5. Report Release Gate

发布前必须逐项检查。

| Gate | 检查项 | 通过标准 |
|---|---|---|
| REPORT-GATE-01 | manifest 引用 | 报告引用 run_manifest 和 artifact_manifest。 |
| REPORT-GATE-02 | score 一致 | 报告指标与 score CSV 一致。 |
| REPORT-GATE-03 | 曲线一致 | 图片曲线来自同一 dataset/TXT/CSV。 |
| REPORT-GATE-04 | 版图一致 | 版图图、DXF/SVG/params 和 geometry hash 对应同一 candidate。 |
| REPORT-GATE-05 | target profile | 明确 target_profile_id 和 score_version。 |
| REPORT-GATE-06 | baseline | 优化结论必须引用 baseline_id 和有效 repeat。 |
| REPORT-GATE-07 | 制造 gate | release candidate 必须说明 DRC 和 tolerance sweep 状态。 |
| REPORT-GATE-08 | 人工介入 | 有 GUI 操作时引用 manual intervention log。 |
| REPORT-GATE-09 | 资产存在 | 图片、logo、CSS、字体和脚本均可访问或已内嵌。 |
| REPORT-GATE-10 | PDF 导出 | PDF 页面、页眉页脚、logo、图表、分页和中文字体正常。 |
| REPORT-GATE-11 | 分支隔离 | 不混用不同材料、阶数、拓扑或目标约束的结论。 |
| REPORT-GATE-12 | 冻结规则 | 发布后状态可转 Frozen，后续只补勘误。 |

## 6. HTML 模板要求

| 项 | 要求 |
|---|---|
| 编码 | UTF-8。 |
| 标题 | 工程化标题，避免口语化表达。 |
| logo | 使用当前报告模板要求的 logo，路径进入资产清单。 |
| 样式 | 页面宽度、页边距、表格、图注和分页适合 PDF 打印。 |
| 图片 | 版图、曲线、候选图必须有图号和数据来源。 |
| 表格 | 指标表保留单位，关键 pass/fail 用文字说明。 |
| 第三方视角 | 第一方工程报告不写“他们/其方案”等第三方口吻。 |
| 可追溯注释 | 可在 HTML comment 中嵌入 report metadata。 |

## 7. PDF 导出流程

导出前检查：

```text
1. 打开 HTML 本地文件或本地服务页面
2. 确认 logo 加载正确
3. 确认图片路径和曲线图加载完整
4. 确认中文字体、表格宽度和分页无溢出
5. 使用模板规定的打印 CSS
6. 导出 PDF
7. 打开 PDF 复查首页、目录、图表、页眉页脚和最后一页
8. 记录 PDF 文件路径和 hash
```

若项目需要严格参考固定模板，例如施工日报扩展模板，应先从模板文件提取打印 CSS、页边距、页眉页脚、logo 规则和分页规则，再生成 PDF。

## 8. 数据一致性检查

发布前建议生成 `report_manifest.json`：

```json
{
  "schema_version": "report_manifest_v1",
  "report_id": "",
  "project_id": "",
  "html_path": "",
  "pdf_path": "",
  "status": "Frozen",
  "target_profile_id": "",
  "score_version": "",
  "baseline_id": "",
  "baseline_repeat_id": "",
  "candidate_run_ids": [],
  "source_scores": [],
  "source_manifests": [],
  "source_artifacts": [],
  "assets": [],
  "release_gates": {
    "manifest": "pass",
    "score_consistency": "pass",
    "plot_consistency": "pass",
    "layout_consistency": "pass",
    "mfg_gate": "pass",
    "pdf_export": "pass"
  }
}
```

## 9. 勘误和版本

| 情况 | 处理 |
|---|---|
| 修正错字、路径、图号 | 可在同一报告补 errata。 |
| 指标或结论变化 | 生成新报告版本，不覆盖 frozen 报告。 |
| 更换材料、阶数、拓扑 | 新建独立报告，不在旧报告混写。 |
| 更换 target profile | 升级 score_version 或新建报告。 |
| PDF 导出样式修复 | 可重新导出 PDF，但需更新 hash 和导出记录。 |

## 10. 发布状态

| 状态 | 含义 |
|---|---|
| `Draft` | 结构或内容未完成。 |
| `Review` | 数据已挂接，等待工程复核。 |
| `Active` | 当前维护版本，可继续更新。 |
| `Frozen` | 正式发布版本，只补勘误。 |
| `Deprecated` | 历史版本，不再作为当前结论。 |

报告只有通过 release gate 后才能标记为 `Frozen`。
