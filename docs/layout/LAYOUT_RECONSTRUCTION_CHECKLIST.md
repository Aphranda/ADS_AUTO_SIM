# Layout Reconstruction Checklist

Status: Active
Domain: LAYOUT
Canonical: `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`
Related: `docs/ADS版图自动仿真项目框架设计.md`, `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义从论文、公式、截图、示意版图或 ADS 原理图模型重构参数化版图时的审查清单。目标是在导入 ADS 和 FEM 仿真前，先确认拓扑、层叠、端口、接地、单位、制造约束和数据追溯一致，减少因版图复刻偏差导致的无效仿真。

## 1. 适用范围

本清单适用于以下场景：

| 场景 | 说明 |
|---|---|
| 论文版图复刻 | 根据论文图片、尺寸标注和传输线模型重建 layout。 |
| 原理图到版图 | 根据 ADS 原理图参数或滤波器综合结果生成物理结构。 |
| 图片到参数表 | 根据截图比例、关键尺寸和板厂约束反推参数化变量。 |
| 拓扑分支验证 | 交指、折叠 SIR、高低阻抗 SIR、stub、hairpin、combline 等分支进入自动化前的版图审查。 |
| release candidate 复查 | 候选结果进入报告前，对 layout/source/result 一致性做最终确认。 |

不适用于直接替代 EM/FEM 仿真。该清单只负责降低输入错误和结构误判风险，电性能仍以仿真和实测为准。

## 2. 输入冻结

重构前必须冻结输入来源，禁止在同一轮中混用多个未标注版本。

| 检查项 | 要求 |
|---|---|
| source_id | 为论文、截图、公式、原理图或人工草图指定唯一来源编号。 |
| source_file | 记录原始文件路径、页码、图片编号、截图时间或 ADS cell 名称。 |
| material_reference | 记录原文材料、介质厚度、铜厚、Er、tanD、参考地层。 |
| frequency_target | 记录中心频率、通带、阻带点、回损目标和插损目标。 |
| manufacturing_rule | 记录最小线宽、最小间距、孔径、焊盘、铜到边距离和板厂工艺等级。 |
| scaling_assumption | 若从图片量尺寸，必须记录基准尺寸、像素比例和是否存在透视变形。 |

## 3. 拓扑等价检查

先确认结构类型，再确认尺寸。拓扑不等价时，局部参数优化通常不能修复整体频响。

| 检查项 | 通过标准 |
|---|---|
| resonator_count | 谐振器数量、阶数和源结构一致。 |
| resonator_orientation | U 形、L 形、折叠线、开路端和短路端方向一致。 |
| symmetry | 源结构为对称结构时，左右或上下参数应默认对称；非对称必须有明确设计原因。 |
| feed_topology | 输入/输出馈线、抽头、耦合馈电或端耦合方式与源结构一致。 |
| coupling_path | 主耦合、交叉耦合、源负载耦合路径不能缺失或误连。 |
| grounded_nodes | 所有短路端、接地 stub、via ground 数量和位置与源结构一致。 |
| open_nodes | 开路端必须保持开路，不得被过渡铜皮、端口或边界误短接。 |
| zero_source | 若论文说明传输零点来源，应能在版图中找到对应耦合路径或短路/开路支节。 |

## 4. 层叠和参考地

层叠变化会直接改变线宽、电长度、耦合强度和辐射损耗，必须作为 layout 输入的一部分。

| 检查项 | 通过标准 |
|---|---|
| substrate_id | layout params 中记录 substrate/profile id。 |
| signal_layer | 明确金属走线层，例如 L1 或 L3。 |
| reference_ground | 明确参考地层，禁止只写“FR4”而不写参考层。 |
| dielectric_height | 记录信号层到参考地的介质厚度，不只记录总板厚。 |
| copper_thickness | 记录铜厚及是否按成品铜厚建模。 |
| Er_tanD | 记录 Er、tanD 来源，FR4 必须注明供应商或工艺档位。 |
| via_stack | via 起止层、孔径、成品孔径和是否接参考地必须明确。 |

## 5. 单位、坐标和缩放

DXF/GDS/ADS 导入错误常见于单位和坐标基准。导入前必须完成以下检查。

| 检查项 | 通过标准 |
|---|---|
| units | `params.json/layout.json/DXF` 单位一致，优先使用 `mm`。 |
| import_units | ADS 导入时选择的单位与导出单位一致。 |
| origin | 记录坐标原点，例如版图中心、输入端口中心或左下角。 |
| bounding_box | 输出总尺寸与设计预期一致，误差应小于 0.1%。 |
| mirror_flip | 确认没有因坐标轴方向导致上下颠倒或左右镜像。 |
| image_scale | 若由图片复刻，至少用两个独立标注尺寸交叉验证缩放比例。 |

## 6. 参数映射

所有可调几何必须有明确参数名、单位、物理含义和约束范围。

| 参数类别 | 必须记录 |
|---|---|
| 线宽 | 50 Ω 线宽、耦合段线宽、谐振支节线宽、高低阻抗段线宽。 |
| 间距 | 输入/输出耦合间距、相邻谐振器间距、折叠线内部间距、最小工艺间距。 |
| 长度 | 谐振器总电长度、折叠臂长度、耦合段长度、馈线长度、过渡段长度。 |
| 孔 | 孔径、焊盘直径、via 到线端补偿距离、via 与边线对齐规则。 |
| 过渡 | 锥形过渡长度、重叠长度、宽度变化起止点。 |
| 边界 | EM airbox、端口延伸、金属到仿真边界距离。 |

## 7. 端口和接地

端口和接地错误会导致原理图带通、版图仿真低通或阻带异常。

| 检查项 | 通过标准 |
|---|---|
| port_count | 端口数量与器件端口数一致。 |
| port_location | P1/P2 放在 50 Ω 馈线端部或明确的端口参考面。 |
| port_width | 端口宽度等于馈线宽度，不覆盖耦合缝隙。 |
| port_reference | 端口参考地为正确地层或 via fence，不悬空。 |
| feed_taper | 需要锥形过渡时，端口参考面不得落在过渡内部。 |
| ground_via | 短路支节使用 via 接参考地时，via 位置必须与短路端补偿规则一致。 |
| direct_ground | 只有原模型为理想短路或 ADS 原理图 ground 时，才能在 layout 中直接等效为短路边界。 |

## 8. Via 和焊盘

via 是电感性结构，不能只按几何连接处理。

| 检查项 | 通过标准 |
|---|---|
| via_shape | 按工艺使用圆孔和圆形焊盘；特殊方形铜皮必须有制造或补偿原因。 |
| drill_pad | 孔径和焊盘满足板厂规则，例如 `10/14 mil` 或当前项目指定规则。 |
| via_offset | via 不要求必然与支节中心线对齐；若采用边线对齐，必须记录对齐边。 |
| compensation | 短路端需记录 via 电感补偿，避免等效电长度偏长。 |
| antipad | 多层结构中若存在内层避让，必须记录 antipad 或 clearance。 |
| stitching | via fence 或接地过孔阵列必须记录间距和边界距离。 |

## 9. 耦合和零点

滤波器版图重构不能只看线长，还必须检查耦合路径。

| 检查项 | 通过标准 |
|---|---|
| input_coupling | 输入耦合强度与目标外部 Q 一致，过强会加宽通带但恶化回损。 |
| output_coupling | 输出耦合与输入耦合对称或有明确非对称目标。 |
| resonator_coupling | 相邻谐振器耦合段长度、间距和重叠方向正确。 |
| source_load_coupling | 若需要传输零点，应保留源负载或非相邻交叉耦合路径。 |
| short_stub_zero | 短路支节零点位置受支节长度、via 电感和参考地影响。 |
| open_stub_zero | 开路支节零点位置受开路端 fringing 和邻近金属影响。 |
| bandwidth_control | 通带变宽通常来自更强外部耦合和谐振器间耦合，但会牺牲选择性或回损。 |

## 10. DRC 和可制造性

每个候选进入 ADS 前，必须先满足制造下限。自动优化不得生成板厂不可加工结构。

| 检查项 | 通过标准 |
|---|---|
| min_width | 所有线宽大于等于当前工艺最小线宽，并保留必要余量。 |
| min_gap | 所有间距大于等于当前工艺最小间距，并保留必要余量。 |
| drill_rule | 孔径、焊盘、孔到边、孔到线满足工艺。 |
| acute_angle | 避免不必要的尖角和极短锥形。 |
| copper_sliver | 避免窄铜皮、孤岛铜和不可控重叠。 |
| port_clearance | 端口附近不应有无意短路或极小缝隙。 |
| edge_clearance | 金属到板边和 EM 边界距离满足制造及仿真要求。 |

## 11. ADS 导入和 EM 设置

导入 ADS 后，应先做结构检查，再启动 FEM。

| 检查项 | 通过标准 |
|---|---|
| layer_map | DXF/GDS layer 映射到正确 ADS conductor/via 层。 |
| shape_conversion | 导入后线框已经转换为 shape，且无丢失、破碎或重复边界。 |
| layout_unit | ADS layout unit 与导出单位一致。 |
| emsetup_clone | emSetup 只从 template clone 到 candidate cell，不覆盖 template。 |
| frequency_sweep | 仿真频段覆盖目标通带和关键阻带，例如 `4-10 GHz`。 |
| boundary | airbox、辐射边界、ground reference 与目标 EM 模型一致。 |
| mesh | 最小间距、via、窄线和耦合缝隙有足够网格分辨率。 |
| dataset_export | 仿真后 dataset、DDS/TXT/CSV 导出路径进入 run manifest。 |

## 12. 结果发布前一致性

进入报告或 release candidate 前，执行以下最终一致性检查。

| 检查项 | 通过标准 |
|---|---|
| source_to_params | source_id、参数表、layout 图和 DXF hash 可追溯。 |
| params_to_result | result/score 能追溯到同一 candidate_id 和 geometry_hash。 |
| material_consistency | 报告中的材料、阶数、层叠和约束与 candidate 完全一致。 |
| plot_consistency | 曲线图、score CSV 和报告表格数值一致。 |
| layout_image | 报告版图图像无镜像、无缩放错误、端口和接地点可识别。 |
| manufacturing_note | 报告明确当前工艺能力和最小尺寸余量。 |

## 13. 常见失败特征

| 现象 | 优先排查 |
|---|---|
| 原理图带通、版图低通 | 接地/via 缺失、开路端误短接、端口参考错误、layer map 错误。 |
| 频率整体偏低 | 电长度偏长、Er 偏高、via 电感未补偿、图片缩放偏大。 |
| 频率整体偏高 | 电长度偏短、参考地距离偏大、Er 偏低、开路端 fringing 未计入。 |
| 通带变窄 | 谐振器间耦合不足、输入/输出耦合不足、间距过大。 |
| 回损恶化 | 外部 Q 不匹配、输入输出耦合不对称、端口落点错误、过渡过短。 |
| 低边或高边阻带不足 | 传输零点路径缺失、stub 长度错误、交叉耦合方向错误。 |
| 仿真不稳定或耗时异常 | 极小缝隙、碎片铜、重复 shape、mesh 过密、边界过近。 |

## 14. 最小执行记录

每次基于新论文、截图或拓扑生成首版 layout 时，应在 candidate 目录或 round 记录中至少写入：

```text
source_id:
source_file:
topology:
substrate_id:
signal_layer:
reference_ground:
units:
manufacturing_rule:
layout_params_file:
layout_image_file:
drc_file:
known_assumptions:
review_status:
```

`review_status` 建议使用：

| 状态 | 含义 |
|---|---|
| `draft` | 首版参数化完成，尚未完整检查。 |
| `layout_checked` | 已完成本清单第 2-11 章检查，可进入 ADS 导入或 dry-run。 |
| `sim_ready` | ADS 导入、端口、emSetup 和频段检查完成，可启动 FEM。 |
| `rework_required` | 拓扑、单位、接地、制造或端口存在明确问题，需要重做。 |
