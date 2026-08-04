# HFSS 微带线+连接器联合仿真优化方案

Status: Draft
Domain: FLOW
Canonical: `docs/flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`
Related: `docs/flow/FLOW_HFSS_PYAEDT_VERDICT.md`, `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Last updated: 2026-08-04
Owner: ADS Automation

本文档定义 HFSS 独立扩展项：用一段标准 50 ohm CPWG/GCPW 传输线和两端连接器组成联合仿真模型，通过 HFSS 自动化迭代连接器与传输线 launch 处的版图参数，使 CPWG-连接器过渡的 S 参数表现更优。该流程不引入滤波器、谐振器或其他功能结构，目的是降低系统复杂度，把优化对象集中在连接器焊盘、锥形过渡、地过孔、参考地和端口参考面。

当前 Home 电脑落地方式：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt` 是单一 AEDT 工程，工程内包含 `IDEAL_50R_CPW_100MM`、`SINGLE_END_SMA_CPW_100MM`、`DUAL_END_SMA_CPW_100MM` 三个 HFSS 3D Layout design。后续连接器优化项目应沿用“一个 AEDT project space，下方多个 design/simulation”的组织方式，而不是每个仿真单独新建 `.aedt`。

HFSS project contract 已固化为两个维度：

- `project_model=per_design_project`：历史默认模式，每个候选或仿真项使用独立 AEDT 工程。
- `project_model=single_aedt_project_multiple_designs`：一个 AEDT 工程内维护多个 design/simulation。
- `project_action=new`：创建新的工程或项目空间。
- `project_action=add`：打开指定 AEDT 工程，在其中追加或重建当前 design。当前 `hfss_sma_connector` 项目使用该模式。

## 0. AEDT 工程修改安全边界

从 2026-08-04 起，HFSS/AEDT 工程结构修改禁止通过直接编辑 `.aedt` 文本实现。端口重命名、端口/激励新增、net/interface 更新、schematic instance 属性、layout component 位置、层叠、boundary、setup 和 sweep 等修改，必须通过 AEDT/pyAEDT/EDB 的正式 API 或 GUI 操作完成。

允许的文件级访问仅限只读审计和差异分析，例如读取已保存 `.aedt` 生成 design/port/net 报告；这类脚本不得写回 `.aedt`、`.aedb` 或 `.aedtresults`。如果 AEDT API 不能完成某项修改，应停止并记录 API 缺口，不能自动 fallback 到文本替换补丁。

执行真实 AEDT API 写入前必须备份 `.aedt`、`.aedb` 和 `.aedtresults`，并串行连接 AEDT，避免多个 pyAEDT/gRPC 会话同时操作同一个工程。用户已打开 AEDT GUI 时，脚本默认保持附着，不关闭项目和 desktop。

历史排查中出现过的文件级路径：

- `tools/hfss/rename_aedt_design_ports_text.py`：文本解析 `PlanarEMCircuit` 并准备写回端口名的脚本；后续禁止作为工程修改入口，仅保留为历史排查记录。
- `projects/hfss_sma_connector/reports/single_text_rename_ports_dry_run_20260804.json` 和 `dual_text_rename_ports_dry_run_20260804.json`：上述文本补丁脚本的 dry-run 报告，未作为正式修改依据。
- `tools/hfss/inspect_aedt_project.py --backend file`：直接读取已保存 `.aedt` 文本并用正则提取 design/port/net；只读审计允许继续使用，但不得扩展为写入工具。
- `projects/hfss_sma_connector/reports/rename_test_after_property_change_file_20260804.json`：对测试副本做 API 属性尝试后的只读文件检查报告，不代表允许直接修改主工程文本。

## 1. 目标

当前目标是 CPWG+连接器联合仿真，不优化滤波器主体，也不把滤波器接入模型。模型只包含：P1 连接器 launch、一段标准 50 ohm CPWG、P2 连接器 launch。通过这个独立联合仿真模型判断连接器与 CPWG 过渡区域对回波、插损、相位和左右端一致性的影响。

核心目标：

- 固定层叠、50 ohm 线宽、直通线长度和求解频段，减少非连接器变量。
- 参数化 P1/P2 两端连接器过渡区域。
- 自动生成 CPWG+connector layout JSON 或 HFSS 几何输入。
- 用 HFSS 作为主要求解器，输出包含连接器/launch 影响的 S2P、trace CSV、score CSV、SVG 和 manifest。
- 以连接处参数为主变量进行迭代，优化 0.5-10 GHz 范围内的 S11/S22、S21 插损、端口对称性和 6-8 GHz 目标频段表现。
- 将理想 50 ohm CPWG through line 或无连接器 50R CPWG 作为 baseline，用 delta 指标判断连接器结构是否引入额外劣化。

## 2. 初始边界

第一阶段只优化连接器与 50 ohm 微带线之间的过渡，不加入滤波器或其他功能结构。

固定条件：

- 板材层叠、介电常数、铜厚和参考地层。
- 50 ohm CPWG 线宽和共面地间隙。
- 联合仿真模型总长度或中间直通线长度。
- P1/P2 连接器类型或等效 footprint 版本。
- HFSS 求解频段、端口类型、reference plane、deembed 和边界设置。

纳入参数化的区域：

- 连接器中心针焊盘或等效信号 pad。
- 信号 pad 到 50 ohm 主线的锥形过渡。
- pad 周围 ground clearance / anti-pad。
- 地焊盘、地过孔、via fence 与连接器壳体接地路径。
- 连接器边缘到参考面之间的 launch feed 长度。
- P1/P2 是否严格镜像对称，以及少量非对称补偿参数。

暂不作为第一阶段变量：

- 滤波器主体谐振器长度、间距和耦合结构。
- 滤波器输入/输出耦合段。
- 板材层叠、介电常数和铜厚。
- 完整机械连接器细节，例如螺纹、介质珠、外壳全 3D 结构；这些放到 Route C，并优先使用用户提供的连接器 HFSS 模型。

## 3. 建模路线

### 3.1 Route A: 2.5D launch surrogate

用于快速迭代。HFSS 3D Layout 中只建立 PCB 金属、过孔、地平面和端口，不导入连接器 3D 实体。连接器影响用 launch pad、ground pad、via fence、端口截面和去嵌长度近似。

适用场景：

- 快速筛选连接处版图参数。
- 评估 pad、taper、via fence、clearance 对 S11/S22 的影响。
- 固定 50R 微带+连接器联合仿真模型后批量比较不同 launch 参数。

### 3.2 Route B: connector footprint + calibrated port

在 Route A 基础上固定连接器推荐 footprint，并使用更明确的端口参考面、deembedding 和 GND reference。该路线作为正式候选筛选的主路线。

需要冻结：

- 连接器型号或等效 footprint 版本。
- 50R 线宽、共面地间隙、联合仿真模型长度和板边位置。
- 端口类型、reference plane、deembed length 和 renormalization。
- P1/P2 的方向、边界和 GND 参考一致性。

### 3.3 Route C: full 3D connector verification

仅用于少量最终候选。优先使用用户提供的连接器 HFSS 模型，并把该模型作为高保真连接器源；必要时再补充 STEP/SAT 或供应商 3D component。

适用场景：

- 发布前验证连接器推荐 launch。
- Route A/B 与实物测试差异较大时定位误差来源。
- 用户提供连接器 HFSS 模型后，对 Route A/B 推荐 launch 做高保真复核。

## 4. 参数分解

建议第一批参数只覆盖连接器过渡区，保持数量可控。

| 参数组 | 示例参数 | 主要影响 |
|---|---|---|
| 50R 微带线 | `line_w_mm`、`line_l_mm`、`edge_margin_mm` | 参考阻抗、传输相位、去嵌稳定性。 |
| 信号 pad | `pin_pad_w_mm`、`pin_pad_l_mm`、`pad_to_edge_mm` | 输入电容、端口阻抗、低频/高频回波。 |
| 锥形过渡 | `taper_l_mm`、`taper_w_start_mm`、`taper_w_end_mm` | 阻抗连续性、通带回波、插损。 |
| launch 短线 | `launch_feed_l_mm`、`reference_plane_offset_mm` | 相位、端口去嵌、左右一致性。 |
| 地间隙 | `gnd_clearance_mm`、`anti_pad_w_mm` | pad 寄生电容、奇偶模耦合。 |
| 地过孔 | `via_d_mm`、`via_pad_d_mm`、`via_pitch_mm`、`via_count` | 返回电流路径、壳体接地、S11/S22。 |
| via fence | `fence_offset_mm`、`fence_pitch_mm`、`fence_span_mm` | 辐射泄漏、边缘模式和高频回波。 |
| 对称性 | `p1_delta_*`、`p2_delta_*` 或 `mirror=true` | P1/P2 回波一致性，S11/S22 差异。 |

## 5. 自动化流程

```text
stackup + 50R microstrip template
  -> connector launch 参数表
  -> generate microstrip+connector layout JSON
  -> HFSS build project
  -> ports/reference/deembed/extents
  -> HFSS solve
  -> export s2p/trace/score/svg/manifest
  -> compare vs ideal/connector-free 50R baseline
  -> optimizer 生成下一批 connector 参数
```

推荐目录：

```text
projects/<project_id>/microstrip_connector/
  plans/
  layouts/
  results/
  baselines/
  reports/
```

run manifest 必须明确 `fixture_type=microstrip_connector_50r`、`stackup_config`、`line_w_mm`、`line_l_mm`、`connector_params_json`、`connector_route`、`connector_model_version`、`reference_plane_offset_mm` 和 `port_deembed_mm`。

## 6. 评分口径

连接器优化的评分对象是 50R 微带线+连接器联合仿真模型，不是完整滤波器。评分既看最终 S 参数，也看相对理想 50R through line 或无连接器 50R 微带线的劣化量。

建议指标：

- `worst_s11_4_10_db`、`worst_s22_4_10_db`：连接器 launch 宽频回波。
- `worst_s11_6_8_db`、`worst_s22_6_8_db`：目标频段回波。
- `min_s21_6_8_db`：目标频段最差插损。
- `s21_ripple_6_8_db`：目标频段幅度平坦度。
- `delta_min_s21_6_8_db`：相对 50R baseline 的插损劣化。
- `delta_worst_return_6_8_db`：相对 50R baseline 的回波劣化。
- `s11_s22_balance_db`：左右端口对称性。
- `passband_phase_slope` 或 group delay：后续需要相位一致性时再加入。

优化目标优先级：

1. 6-8 GHz 内 S11/S22 尽量低，优先减少连接器处反射。
2. 6-8 GHz 内 S21 插损尽量接近 50R through baseline。
3. 减小 P1/P2 不对称，避免一端 launch 优、一端 launch 差。
4. 0.5-10 GHz 内避免出现明显局部谐振或高频回波尖峰。
5. 满足连接器 footprint、板边距离、地过孔和板厂制造约束。

## 7. 数据契约补充

新增或扩展 layout/manifest 字段：

```text
fixture_type
connector_model_version
connector_route
connector_type
microstrip_connector_layout_json
connector_params_json
line_w_mm
line_l_mm
reference_plane_offset_mm
port_deembed_mm
connector_region_bbox_mm
connector_hfss_model_path
connector_hfss_model_version
connector_hfss_model_hash
connector_port_mapping
```

artifact 建议记录：

```text
microstrip_connector_layout_json
connector_params
hfss_project
aedt_project
connector_hfss_model
s2p
trace_csv
score_csv
compare_csv
svg
run_manifest
artifact_manifest
```

## 8. 实施拆解

### Phase 0: 方案冻结

- [ ] 固定连接器类型或等效 launch footprint 版本。
- [ ] 登记用户提供的连接器 HFSS 模型路径、版本、hash、端口定义和参考面。
- [ ] 固定层叠、50R 线宽、联合仿真模型长度、板边位置和求解频段。
- [ ] 固定 Route A/B/C 的定义和使用场景。
- [ ] 选定理想 50R through line 或无连接器 50R 微带线 baseline。
- [ ] 明确评分 target：回波、插损、delta、对称性和制造约束。

### Phase 1: 参数化连接器过渡

- [x] 新增 connector launch 参数 schema。
- [x] 新增 microstrip+connector generator：输入 stackup/50R template 和 connector 参数，输出微带线+连接器 layout JSON。
- [x] 增加连接器区域 DRC：pad、clearance、via、edge setback、symmetry、manufacturing limit。
- [x] 生成 3-5 个 smoke 候选，只做 layout gate，不启动 HFSS。

### Phase 2: HFSS 自动求解闭环

- [x] 在 HFSS workflow 中支持 `fixture_type=microstrip_connector_50r` 的 dry-run/manifest 记录。
- [x] 固定当前 Route A/B smoke 口径：AEDT edge port、`port-edges` GND、`ETCH_INNER1:hfss_ground_plane` reference、50 ohm renormalization、deembed=`0 mm`。
- [x] 对一个 smoke 候选执行 HFSS solve，输出完整 manifest。
- [x] 与 50R baseline 做 S 参数 delta compare。
- [x] 连接器 3D placement 改为项目配置 profile 管理；历史 `SMA_KE_Unite_solder` 使用 `sma_ke_unite_solder_3dlayout_etch_top` profile，手动校准参考 Z 为 `2.07 mm`。该值与连接器模型、导入方向、placement layer 和当前层叠相关，后续其他连接器必须新建 profile，不得复用。
- [x] 当前 active connector profile 切换为 `sma_ke_unite_small_solder_3dlayout_etch_top`，连接器模型为 `SMA_KE_Unite_Small_Solder`，P1/P2 component name 分别为 `SMA_KE_Unite_Small_Solder1` 和 `SMA_KE_Unite_Small_Solder2`。
- [x] `SINGLE_END_SMA_CPW_100MM` 已替换为 small connector component ID `67`，placement readback 为 `Location=0,0,2.07`、`Rotation Angle=180deg`、`3D Placement=true`。
- [x] `DUAL_END_SMA_CPW_100MM` 已替换为 small connector component ID `68/69`；ID `68` placement 为 `0,0,2.07`、`180deg`，ID `69` placement 为 `113.65,0,2.07`、`0deg`。
- [x] 连接器 pin interface port 添加已独立为 `tools/hfss/add_connector_pin_iports.py`，支持从 `config/projects/hfss_sma_connector.json` 的 connector placement profile 自动读取 P1/P2 组件，也支持 `--component` 和 `--component-id` 手动指定。
- [ ] 在 AEDT GUI 中手动将连接器 pin interface port 改成标准 `PortN` 命名；当前不再使用文本补丁或端口重命名脚本修改工程。
- [ ] 手动改名后，用只读检查确认 `SINGLE_END_SMA_CPW_100MM` 端口为 `Port1/Port2`，`DUAL_END_SMA_CPW_100MM` 端口为 `Port1/Port2`。

2026-08-04 暂停状态：

- 已停止继续写 AEDT 工程，等待明天继续验证。
- DUAL 端口被用户删除后，`add_connector_pin_iports.py --project-config config\projects\hfss_sma_connector.json --placement dual` 可以正确从 profile 选中 ID `68/69`，但一次性多选执行未生成端口。
- 单独对 DUAL component ID `68` 执行 `AddPinIPorts` 可生成 `Pin_T1`；单独对 ID `69` 执行未新增端口，原因初判为两个 small connector 内部 pin 名均为 `Pin_T1`，AEDT 不允许第二个同名 IPort 自动创建。
- `odesign.RenamePort("Pin_T1", "Port1")` 对当前 3D Layout schematic IPort 失败，明天应优先用 `SchematicEditor.ChangeProperty` 直接修改 `PassedParameterTab.PortName`，或在 GUI 中完成端口改名后再由脚本继续添加第二个端口。
- 新增 `tools/hfss/inspect_schematic_iports.py` 用于只读读取 `SchematicEditor.GetAllPorts()` 和 IPort 属性；明天继续前先运行该脚本确认当前 GUI/保存状态。

当前 2026-08-03 Home profile 首次结果：

- 项目目录：`projects/hfss_sma_connector/microstrip_connector/`
- baseline：`100 mm` P1-to-P2 理想 50R through line，`passband_min_s21=-3.10 dB`，`worst_s11_6_8=-23.41 dB`，`worst_s22_6_8=-24.14 dB`。
- connector surrogate：中间 `100 mm` 50R 微带 + 两端各 `3.5 mm` launch，`passband_min_s21=-8.02 dB`，`worst_s11_6_8=-2.72 dB`，`worst_s22_6_8=-2.75 dB`。
- delta compare：6-8 GHz 内 `S21` 平均绝对差约 `3.43 dB`，`S11/S22` 平均绝对差约 `22.35/24.35 dB`。
- 结论：默认 Route A surrogate launch 严重失配，下一步先做连接器 launch 参数 DoE；完整 3D SMA 模型导入放到 Route C。

### Phase 3: 连接处参数优化

- [ ] 建立首批 DoE 参数表。
- [ ] 用 HFSS 批量运行微带线+连接器联合仿真候选。
- [ ] 基于 score 和 delta 指标生成下一批局部候选。
- [ ] 判断对称设计和非对称补偿哪一种更优。

### Phase 4: 连接器高保真复核

- [ ] 接收并归档用户提供的连接器 HFSS 模型，记录模型路径、版本、hash、端口定义和坐标基准。
- [ ] 建立 connector model import/placement adapter，保证模型端口、PCB launch、GND reference 和参考面一致。
- [ ] 对前 2-3 个 launch 候选执行 Route C 复核。
- [ ] 形成连接器版图推荐参数和可制造性说明。
- [ ] 冻结微带线+连接器联合仿真的推荐 launch 参数，不在本阶段混入滤波器主体。

### Phase 5: 最终合并验证

- [ ] 将冻结后的连接器 launch 作为独立模块移植到滤波器 PCB。
- [ ] 对带滤波器主体的完整版图执行少量 HFSS/ADS 复核，确认连接器与输入/输出耦合段的相互影响。
- [ ] 若整板复核出现明显劣化，只允许小范围调整首末端馈线和连接器过渡，不重启微带线+连接器联合仿真主优化。
- [ ] 该阶段复杂度最高，作为最后事项处理，不作为微带线+连接器联合仿真优化闭环的前置条件。

## 9. 风险

| 风险 | 说明 | 处理 |
|---|---|---|
| 端口参考面不一致 | 连接器 launch 仿真很容易把端口参考面和实际测量面混淆。 | manifest 必须记录 reference plane 和 deembed。 |
| 50R 微带线过短或去嵌过度 | 直通线太短会让端口、pad 和过渡互相耦合，太强去嵌会掩盖 launch 问题。 | 固定最小 50R 线长，并对 deembed 设置做 baseline check。 |
| 2.5D surrogate 精度有限 | Route A/B 不包含完整连接器内部结构。 | 只用于迭代，最终候选用用户提供的连接器 HFSS 模型执行 Route C 或实物复测。 |
| 参数过多 | pad、taper、via、clearance 同时扫描会快速膨胀。 | 先 DoE 小样本，再局部优化。 |
| 连接器模型版本漂移 | 用户提供的 HFSS 模型若后续更新，端口定义、坐标基准或内部结构可能变化。 | manifest 记录模型路径、版本、hash 和 port mapping，模型更新后重新冻结 baseline。 |
| 连接器机械约束 | 边缘连接器有板边距离、地焊盘和禁布区。 | connector schema 加 mechanical envelope。 |
| 最终合并验证复杂度高 | 微带线+连接器联合仿真得到的最优 launch 移植到滤波器输入/输出耦合段后，仍可能与滤波器主体互相影响，并引入整板边界、耦合和求解时间问题。 | 作为最后事项处理；先冻结 launch，再做少量整板复核。 |

## 10. 当前结论

该扩展项应作为 HFSS 微带线+连接器联合仿真方案推进。当前阶段采用标准 50 ohm 微带线 + 两端连接器 launch 的结构，优先通过 Route A/B 快速迭代连接器过渡版图，以理想或无连接器 50R through line 作为 baseline，通过 delta 指标判断连接器结构是否改善或恶化 S 参数。最终合并验证作为后续最后事项：连接器 launch 冻结并使用用户提供的 HFSS 模型完成高保真复核后，再移植到滤波器 PCB 做少量整板验证。
