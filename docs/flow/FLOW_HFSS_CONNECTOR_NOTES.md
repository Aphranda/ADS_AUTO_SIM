# HFSS 连接器注意事项

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_HFSS_CONNECTOR_NOTES.md`
Related: `docs/flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`, `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`
Last updated: 2026-08-07
Owner: ADS Automation

本文档汇总 HFSS 连接器仿真中最容易遗漏的操作注意点，作为独立检查清单使用。它不替代主流程文档，只把高频门禁和设置集中到一个入口。

## 1. 设计设置

- `Enable material override` 应勾选。
- `Enable Design-level intersection checks` 在当前 connector fixture 中通常应取消勾选。
- 二者不是同一个开关，不能互相替代。

## 2. 版图生命周期

- 裁切/裁剪板子后，裁切框属于临时源版图对象，必须进入删除生命周期。
- 删除并重绘时，默认清理常见 `clip/cut/crop frame` 名称。
- 如果临时对象名不在默认表内，必须用 `--delete-extra-name` 或 `--delete-extra-prefix` 补进清理列表。
- 版图替换遵循 `delete source layout -> draw new layout -> recreate PCB output port`。
- 连接器实例和连接器 pin 端口不进入删除列表。

## 3. 端口和几何

- connector pin interface port 不要强制改名。
- 连接器芯线与焊锡可以跨越端面参考面到 PCB pad 的物理间隔，不能因为可见空隙就直接判定为开路。
- 源连接器模型几何若有历史尺寸偏差，应回到正式 API 或 GUI 修正源模型，而不是重复同步变量。

## 4. 评分和对比

- 评分口径使用 `connector_fullband_v1`。
- 频段固定为 `0.5-10 GHz` 全频带。
- 对比必须保留无连接器或理想 50R baseline。
- 报告里的曲线、score 和 layout 图必须能追溯到同一 run。

## 5. 常见异常优先级

- 端口/连通性异常，先查裁切框残留。
- 网格或交叉检查报错，先查 `Enable Design-level intersection checks`。
- 金属/介质交叠导致的 mesh 问题，先查 `Enable material override`。
- 3.5 GHz 一类局部谐振，先查 L2/L3 残留对象、重复版图和 launch 几何，而不是先改 GUI 参数。

