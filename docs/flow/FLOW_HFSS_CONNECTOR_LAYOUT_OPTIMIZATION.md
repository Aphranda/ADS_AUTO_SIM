# HFSS 微带线+连接器联合仿真优化方案

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`
Related: `docs/flow/FLOW_HFSS_PYAEDT_VERDICT.md`, `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Last updated: 2026-08-05
Owner: ADS Automation

本文档定义 HFSS 独立扩展项：用一段标准 50 ohm CPWG/GCPW 传输线和两端连接器组成联合仿真模型，通过 HFSS 自动化迭代连接器与传输线 launch 处的版图参数，使 CPWG-连接器过渡的 S 参数表现更优。该流程不引入滤波器、谐振器或其他功能结构，目的是降低系统复杂度，把优化对象集中在连接器焊盘、锥形过渡、地过孔、参考地和端口参考面。

当前落地方式是双环境同一工程组织：家里电脑使用 HFSS profile `home` 和 `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt` 作为当前验证工程；公司电脑镜像使用 HFSS profile `company_connector` 和 `D:\Work\ADS\HFSS_VERDICT\hfss_sma_connector_cpw.aedt`。连接器优化项目沿用“一个 AEDT project space，下方多个 design/simulation”的组织方式，而不是每个仿真单独新建 `.aedt`。

路径边界必须严格区分：家里当前连接器工程只走 `home` profile 和 `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT`；公司连接器镜像只走 `company_connector` profile 和 `D:\Work\ADS\HFSS_VERDICT`；公司电脑滤波器/常规 HFSS backend 继续使用原有工程根 `D:\Work\ADS\SIMADS_STANDARD\HFSS`，不得把滤波器候选迁入连接器专用目录。

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
- 以连接处参数为主变量进行迭代，优化 0.5-10 GHz 全频带范围内的 S11/S22、S21 插损、幅度平坦度和端口对称性。
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
| 锥形过渡 | `taper_l_mm`、`taper_w_start_mm`、`taper_w_end_mm` | 阻抗连续性、全频带回波、插损。 |
| launch 短线 | `launch_feed_l_mm`、`reference_plane_offset_mm` | 相位、端口去嵌、左右一致性。 |
| 地间隙 | `gnd_clearance_mm`、`anti_pad_w_mm` | pad 寄生电容、奇偶模耦合。 |
| 地过孔 | `via_d_mm`、`via_pad_d_mm`、`via_pitch_mm`、`via_count` | 返回电流路径、壳体接地、S11/S22。 |
| via fence | `fence_offset_mm`、`fence_pitch_mm`、`fence_span_mm` | 辐射泄漏、边缘模式和高频回波。 |
| 对称性 | `p1_delta_*`、`p2_delta_*` 或 `mirror=true` | P1/P2 回波一致性，S11/S22 差异。 |

## 5. 自动化流程

### 5.1 SMA launch 补偿策略（2026-08-05）

当前 30 mm 连接器夹具的首要失配风险来自 SMA 中心针焊盘偏大。该结构等效为 launch 处局部电容偏大、阻抗偏低，表现为 S11/S22 恶化，并通过反射间接拉低 S21。后续优化不得只追求插损，应先压低 launch 回波，再看相对无连接器 50R baseline 的 S21 delta。

公开资料给出的处理方向一致：连接器中心针 landing pad 和 PCB 传输线交界处需要做阻抗补偿；常用手段包括缩小焊盘、加长/调窄 taper、调整共面地间隙、保证地回流 via 连续，以及在参考地层做局部 cut-out / anti-pad 来降低焊盘寄生电容。参考资料包括 Southwest Microwave end-launch connector test board 文章、MDPI Electronics 2024 SMA connector sub-10 GHz performance 对 reference plane cut-out 的测试，以及 reference-plane cut-out 方法论文。资料入口：

- https://www.microwavejournal.com/articles/6009-50-ghz-end-launch-connector-test-boards
- https://www.mdpi.com/2079-9292/13/14/2686
- https://www.mdpi.com/1424-8220/22/3/964
- https://doi.org/10.3390/electronics11131990

本项目第一轮采用以下工程策略：

- 优先缩小中心焊盘：`pin_pad_w_mm` 和 `pin_pad_l_mm` 是第一优先级变量；焊盘只保留制造和焊接可靠所需尺寸。
- 优化 taper：增大 `taper_l_mm`，并允许 `taper_w_start_mm` 小于焊盘宽度，避免焊盘到 50R CPWG 主线突变。
- L2 参考地局部挖空：先只对 `ETCH_INNER1` 在中心焊盘和 taper 起始区域下方做 cut-out，不先挖 `ETCH_INNER2/ETCH_BOTTOM`。cut-out 目标是降低焊盘到参考地的电容，而不是破坏 SMA 外壳和 via fence 的回流路径。
- cut-out 必须参数化：记录 `l2_cutout_enabled`、`l2_cutout_shape`、`l2_cutout_w_mm`、`l2_cutout_l_mm`、`l2_cutout_offset_x_mm`、`l2_cutout_taper_l_mm`、`l2_cutout_corner_r_mm` 和 `l2_cutout_keep_gnd_via_clearance_mm`。若当前 layout schema 暂不能表达内层挖空，先在候选计划中登记这些字段，并在 generator/HFSS build 中补齐实现。
- 不使用普通 lumped 补偿器件：10 GHz 上普通贴片电容/电感的封装寄生、自谐振、焊盘寄生和装配误差会主导结果；本项目补偿只使用可制造的分布式微带/CPW 几何，包括线宽、长度、taper、参考地 cut-out、短高阻抗段和受控 stub。
- 串联电感性补偿：若 S11/TDR 显示焊盘处为低阻抗凹陷，可尝试在焊盘与 50R 主线之间加入短高阻抗段或更窄 taper tip，等效增加分布式串联电感来补偿焊盘 shunt capacitance。该方法优先于随意增加开路 stub。
- 短截线补偿仅作为二轮定位候选：开路或短路 stub 是谐振/频率选择结构，可能改善某一局部失配点，但容易在 0.5-10 GHz 全频带内引入新尖峰。只有当 full-band 复数 S 参数显示稳定单一失配中心、且不会破坏相邻频段时，才加入 `stub_type=open|short`、`stub_l_mm`、`stub_w_mm`、`stub_offset_x_mm` 的 DOE。
- Smith 圆图调谐：每次仿真必须保留复数 S 参数，并用 `z=(1+Gamma)/(1-Gamma)` 转为 50 ohm 归一化输入阻抗。若目标频段内 `r<1` 且 `x<0`，优先减小焊盘电容或加入短高阻抗串联段；若 `r<1` 且 `x>0`，优先减小串联电感或增加局部电容；若轨迹绕圈或跨越实轴，说明结构已进入谐振补偿，优先回退到更宽带的 pad/taper/cut-out 方案。
- 保持回流连续：连接器地脚、顶层共面地和 via fence 不得被 cut-out 切断；via 与中心焊盘距离作为独立变量扫参。
- 第二层以下挖空作为第二轮变量：只有当 L2 cut-out 仍无法改善 S11，或 TDR/场分布显示 launch 仍明显电容性时，才增加 `l3_cutout_enabled` 或更深层 cut-out。

首轮真实 HFSS solve 控制在 6-8 个候选；计划表允许登记带 gate 的备用候选，只有前序 Smith/score 条件满足时才进入求解队列：

| 候选组 | 变化 | 目的 |
|---|---|---|
| baseline | 当前 30 mm single/ideal | 建立无连接器和当前连接器 delta。 |
| small_pad | 减小 `pin_pad_w_mm/pin_pad_l_mm` | 降低焊盘电容。 |
| long_taper | 增大 `taper_l_mm`，调小 `taper_w_start_mm` | 平滑阻抗过渡。 |
| l2_cutout_s/m | 在 `ETCH_INNER1` 小/中等面积挖空 | 验证参考地 cut-out 是否改善 S11。 |
| pad_taper_cutout | 小焊盘 + 长 taper + L2 cut-out | 测试组合补偿。 |
| high_z_series | 焊盘后短高阻抗段 / 更窄 taper tip | 用串联电感补偿焊盘电容。 |
| via_relief | 调整 via fence 到中心焊盘距离 | 避免回流过近导致额外电容，同时保持地连续。 |

L2 cut-out 形状选择：

| 形状 | 参数 | 适用场景 | 风险 |
|---|---|---|---|
| `rect` | `w/l/offset_x` | 首轮基准，最容易实现和解释。 | 直角处可能引入局部场集中，尺寸过大时回流路径变差。 |
| `rounded_rect` | `w/l/corner_r/offset_x` | 比矩形更平滑，适合最终候选复核。 | generator/HFSS build 需要支持圆角或多段近似。 |
| `tapered` | `w_start/w_end/l/taper_l/offset_x` | cut-out 随焊盘到窄线过渡逐渐收敛，更像宽带补偿。 | 参数多，容易和金属 taper 强耦合，首轮只做 1 个样本。 |
| `dogbone` | `pad_w/pad_l/neck_w/neck_l` | 只释放焊盘正下方和 taper 起点，保留两侧回流。 | 形状复杂，需确认 via fence clearance。 |
| `slot` | `slot_w/slot_l/offset_x` | 只沿中心线挖窄槽，微调电容。 | 补偿力度有限，可能不足以修正大焊盘。 |

首轮实现优先级：`rect` 小/中尺寸 + `tapered` 一个随形样本。`rounded_rect/dogbone/slot` 先进入计划，不作为第一批真实 HFSS 候选，除非矩形 cut-out 显示明确改善但出现局部尖峰。

### 5.2 定稿前独立检索与评审（2026-08-05）

连接器 launch 优化方案必须至少经过三组独立资料检索和评审后才能定稿。三组证据不能来自同一篇文章的重复解读，且每组评审都要落回本项目可执行变量。

**评审 A：edge-launch SMA/GCPW 实测和厂商测试板**

- 资料入口：Southwest Microwave 50 GHz end-launch connector test board 文章，MDPI Electronics 2024 sub-10 GHz SMA connector performance 论文。
- 结论：SMA 过渡处的中心 pad、taper、地回流 via 和参考面几何共同决定 S11。连接器本体不是唯一变量；PCB launch 的阻抗补偿必须作为独立优化对象。
- 对本项目的约束：当前 `pin_pad_w_mm=1.2`、`pin_pad_l_mm=4.8`、`taper_l_mm=1.6` 导致宽线段过长，首轮必须把“有效宽焊盘长度”作为主变量压缩，而不是只改 via 或端口。

**评审 B：参考平面 cut-out / anti-pad**

- 资料入口：reference plane cut-out 方法论文、MDPI SMA sub-10 GHz connector 论文。
- 结论：大焊盘下方的参考地会形成显著 shunt capacitance；L2 cut-out 可以降低该电容并把 Smith 轨迹从低阻抗电容区拉回。但 cut-out 过大时会破坏回流路径，转成过度电感或产生局部谐振。
- 对本项目的约束：第一轮只挖 `ETCH_INNER1`，只覆盖中心焊盘和 taper 起点，不切断顶层共面地、连接器地脚和 via fence。矩形小/中尺寸优先；`tapered` 只做一个样本；更复杂形状放二轮。

**评审 C：分布式补偿、短高阻抗段和 stub 风险**

- 资料入口：微带不连续补偿、Smith 圆图匹配和 connector launch 调谐资料。
- 结论：10 GHz 内普通 lumped 电容/电感不适合作为首选补偿。焊盘电容过大时，短高阻抗传输线段可以提供分布式串联电感，通常比开路/短路 stub 更宽带。stub 本质更接近局部谐振补偿，可能改善某一点，但也可能在 0.5-10 GHz 引入尖峰。
- 对本项目的约束：首轮允许 `series_hi_z_*`，禁止默认启用 stub。只有复数 S2P 显示全频带内存在稳定单峰失配，且相邻频段没有宽带低阻抗趋势时，二轮才加入 stub。

基于三组评审，当前定稿前 gate 为：

- 必须先完成 `IDEAL_50R_CPW_30MM` 和 `SINGLE_END_SMA_CPW_30MM` 复数 S2P 对比。
- 必须计算 0.5-10 GHz 全频带的 `z=(1+Gamma)/(1-Gamma)` 归一化阻抗范围。
- 若 `r<1, x<0` 占主导，第一动作是减小 pad 电容：缩小/缩短 pad，或增加 L2 cut-out；第二动作才是短高阻抗段。
- 若 `r>1, x>0` 占主导，说明 cut-out 或高阻抗段过强，应回退 cut-out 或缩短/加宽高阻抗段。
- 若轨迹绕圈、尖峰或局部单点改善伴随其它频段回波峰，当前候选不得定稿。

### 5.3 首轮参数范围冻结

首轮 DOE 的参数范围按“宽带根因修正”冻结，不做全因子暴力扫描：

| 参数 | 当前值 | 首轮范围 | 定稿约束 |
|---|---:|---:|---|
| `pin_pad_w_mm` | `1.2` | `0.90-1.20` | 真实制造候选不得小于连接器中心针/焊接可靠下限；若 source connector `Pin` bbox 仍未修复，低于 `0.95` 的样本只作为电趋势样本。 |
| `pin_pad_l_mm` | `4.8` | `2.0-4.8` | 优先缩短宽焊盘有效长度；机械接触必需区域不能删除。 |
| `taper_l_mm` | `1.6` | `2.4-4.0` | 小焊盘样本必须配长 taper，避免 1.2 mm 直接跳到 0.3175 mm。 |
| `taper_w_start_mm` | `1.2` | `0.85-1.10` | 允许 taper 起点小于焊盘宽度，用短 neck 降低电容突变。 |
| `gnd_clearance_mm` | `0.30` | `0.30-0.45` | 只小范围释放顶层共面地，不能切断连接器地回流。 |
| `fence_offset_mm` | `0.55` | `0.55-0.95` | 当前 via 距中心焊盘较近，扫远一点判断是否减小额外电容；不能超过导致回流绕行的距离。 |
| `l2_cutout_w_mm` | `off` | `1.4/1.8/2.2` | 只对 `ETCH_INNER1`；cut-out 边缘需避开 via pad 和 GND net。 |
| `l2_cutout_l_mm` | `off` | `3.0/4.2/5.4` | 覆盖 pad 和 taper 起点；不延伸到整段 50R 主线。 |
| `series_hi_z_w_mm` | `off` | `0.18-0.24` | 必须大于板厂最小线宽，长度短于 1 mm，避免成为明显谐振结构。 |
| `series_hi_z_l_mm` | `off` | `0.4-1.0` | 只在 Smith 显示电容性低阻抗时启用。 |
| `stub_*` | `off` | 二轮待定 | 首轮禁用；只在窄带单峰失配时引入。 |

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

连接器评分系统独立于滤波器评分系统，当前版本为 `connector_fullband_v1`，默认 profile 为 `sma_launch_fullband_0p5_10g_v1`。后处理入口为 `tools/analyze_connector_s2p.py`，核心库为 `src/simads/scoring/connector.py`。后续参数优化器应直接读取该 score CSV，不再消费 `passband_*`、`worst_s11_6_8_db` 或滤波器 `target_profile` 字段。

评分系统输出两类排序字段：

- `optimization_cost`：优化器主目标，越小越好。该值由全频带最差回波、最差/平均插损、S21 ripple 和 S11/S22 balance 的超限惩罚加权得到。
- `connector_score`：报告展示分数，`100 - optimization_cost` 后截断到 `0-100`，越高越好。

默认 tuning gate：

- `target_worst_return_db=-10 dB`
- `target_s21_min_db=-1.5 dB`
- `target_s21_avg_db=-0.75 dB`
- `target_s21_ripple_db=1.0 dB`
- `target_balance_db=1.5 dB`

默认 release/pass gate：

- `pass_worst_return_db=-15 dB`
- `pass_s21_min_db=-1.0 dB`
- `pass_s21_avg_db=-0.5 dB`
- `pass_s21_ripple_db=0.75 dB`
- `pass_balance_db=1.0 dB`

状态定义：

- `TUNE`：至少一项 tuning gate 未达标，继续迭代。
- `CANDIDATE`：达到 tuning gate，但未达到 release/pass gate，可进入高保真复核或局部细调。
- `PASS_CANDIDATE`：达到 release/pass gate，可作为当前连接器 launch 推荐候选。

建议指标：

- `worst_s11_0p5_10g_db`、`worst_s22_0p5_10g_db`：连接器 launch 全频带回波。
- `worst_return_0p5_10g_db`、`worst_return_param`、`worst_return_freq_ghz`：全频带最差回波及其位置。
- `s21_min_0p5_10g_db`：全频带最差插损。
- `s21_avg_0p5_10g_db`：全频带平均插损。
- `s21_ripple_0p5_10g_db`：全频带幅度平坦度。
- `delta_s21_avg_vs_ideal_0p5_10g_db`：相对 50R baseline 的平均插损劣化。
- `delta_worst_return_vs_ideal_0p5_10g_db`：相对 50R baseline 的回波劣化。
- `s11_s22_balance_max_0p5_10g_db`：左右端口回波差异。
- `phase_slope_0p5_10g` 或 group delay：后续需要相位一致性时再加入。
- `smith_z_r_min/max_0p5_10g`、`smith_z_x_min/max_0p5_10g`：由复数 S11/S22 计算的 50 ohm 归一化阻抗范围。
- `smith_tuning_hint`：基于 `r/x` 和轨迹形态给出的下一轮补偿方向，例如 `reduce_pad_capacitance`、`add_series_inductance`、`reduce_series_inductance`、`avoid_local_resonance`。

优化目标优先级：

1. 0.5-10 GHz 内 S11/S22 尽量低，优先减少连接器处反射。
2. 0.5-10 GHz 内 S21 插损尽量接近 50R through baseline。
3. 减小 P1/P2 不对称，避免一端 launch 优、一端 launch 差。
4. 0.5-10 GHz 内避免出现明显局部谐振或高频回波尖峰。
5. 满足连接器 footprint、板边距离、地过孔和板厂制造约束。

Smith-guided 下一轮决策：

| Smith / 阻抗现象 | 物理判断 | 优先动作 |
|---|---|---|
| `r<1, x<0` | 焊盘/参考地电容偏大，局部阻抗偏低 | 缩小 pad、增大 L2 cut-out、加短高阻抗串联段。 |
| `r<1, x>0` | 串联电感偏大但电阻仍偏低 | 缩短/加宽高阻抗段，减小过长 taper 或过远回流路径。 |
| `r>1, x>0` | 过度电感性或 cut-out 过大 | 减小 cut-out，增加局部电容或缩短 series 段。 |
| `r>1, x<0` | 过度电容补偿但电阻偏高 | 调整 taper 起点、局部加宽，检查 via/地回流不连续。 |
| 轨迹绕圈/尖峰 | 窄带谐振或 stub 过强 | 回退 stub，优先使用宽带 pad/taper/cut-out。 |

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
- [x] 新增 `tools/hfss/audit_connector_parameters.py`，用于只读审计源 HFSS connector design、工程 `$sma_` 变量、3D Layout instance `PassedParameterTab` 和源几何 bbox；脚本支持 `--sync-project-variables --execute --save` 将源 design 变量同步为工程级 `$sma_` 变量。
- [x] 2026-08-04 公司电脑已执行连接器参数同步：工程 `D:\Work\ADS\HFSS_VERDICT\hfss_sma_connector_cpw.aedt`，源 design `SMA_KE_Unite_Small_Solder`，layout design `SINGLE_END_SMA_CPW_100MM`。同步报告为 `projects/hfss_sma_connector/reports/connector_parameter_sync_project_vars_20260804.json` 和 `projects/hfss_sma_connector/reports/connector_parameter_sync_project_vars_resync_20260804.json`。
- [x] 同步后工程变量和实例传参一致：`$sma_Pin_D=0.95mm`、`$sma_Hole_D=1.25mm`、`$sma_PTFE_D=4.2mm`、`$sma_Pin_P=1.7mm` 等参数均已写入工程变量表并与 source design/instance 参数一致。
- [x] 当前有效连接器实例为 schematic component ID `73`，component name `SMA_KE_Unite_Small_Solder6`；layout placement 为 `Location=0,0,2.0862`、`Local Origin=0,0,0`、`Rotation Angle=180deg`、`PlacementLayer=ETCH_TOP`。后续脚本应以 readback 的 effective component ID 为准，不能只依赖请求传入的旧 ID `70`。
- [ ] 修复源连接器模型几何：同步后审计仍显示 `Pin` bbox 直径为 `1.25mm`，匹配 `Hole_D` 而不是 `Pin_D=0.95mm`；`Solder_S` bbox 宽度约 `0.945mm`，已匹配 `Pin_D`。该问题属于 source connector 几何历史/Unite 后实体尺寸不一致，不能通过再次同步变量解决，应通过 AEDT GUI 或正式 API 重建/修正源 connector model，确保中心导体全程使用 `Pin_D/2`，`Hole_D` 仅用于孔/避让。
- [x] 2026-08-04 端口命名规则勘误：connector pin interface port 不能强制改名；改名后会触发 AEDT/HFSS 报错。后续端口名称以 AEDT 自动生成结果为准，例如 `Pin_T1` 或同类生成名。
- [ ] 端口改名作为后续探索项单独处理：目标是确认是否存在 AEDT 官方 API 路径可同时更新 excitation、schematic IPort、3D component passed parameter、report/Dataset 引用和 solver 内部映射；在该探索完成前，正式流程不得改名。
- [ ] 脚本和 manifest 增加 logical port mapping：保留 AEDT 原始 port name，同时记录 `logical_port=P1/P2`、component ID、component name、pin name、reference conductor 和 placement 信息；评分和报告使用逻辑端口映射，不再依赖 `Port1/Port2` 字面名称。
- [ ] 用只读检查脚本记录 `SINGLE_END_SMA_CPW_100MM` 和 `DUAL_END_SMA_CPW_100MM` 的实际 generated port name，并验证每个逻辑端口均能映射到有效 excitation。
- [x] 2026-08-04 已在现有工程追加 30 mm 快速仿真 design：`IDEAL_50R_CPW_30MM`、`SINGLE_END_SMA_CPW_30MM`、`DUAL_END_SMA_CPW_30MM`；频段为 `0.5-10 GHz`，setup/sweep 为 `Setup_0p5to10G` / `Sweep_0p5to10G_96pt`，当前仅 build-only，未启动求解。
- [x] 30 mm design 已放置连接器和端口：single 使用 component ID `78`，connector port 为 `Pin_T1`；dual 使用 component ID `79/80`，connector ports 为 `Pin_T1/Pin_T2`；端口不改名，后续通过 logical port mapping 使用。
- [x] 2026-08-04 网格报错口径更新：connector fixture design 必须取消勾选 Design Settings > HFSS Meshing Method > `Enable Design-level intersection checks`。自动 workflow 使用 `--no-enable-design-intersection-check` 写入 `EnableDesignIntersectionCheck=false`，避免 3D connector 与 PCB launch 接触处触发设计级交叉检查导致端口/网格报错。
- [x] 当前家里环境连接器工程：HFSS profile `home`，workspace `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT`，project `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt`；公司镜像仍使用 `company_connector` 和 `D:\Work\ADS\HFSS_VERDICT`。
- [x] 2026-08-04 已对家里当前工程执行 DesignOptions 写入并保存：`IDEAL_50R_CPW_100MM`、`SINGLE_END_SMA_CPW_100MM`、`DUAL_END_SMA_CPW_100MM`、`IDEAL_50R_CPW_30MM`、`SINGLE_END_SMA_CPW_30MM`、`DUAL_END_SMA_CPW_30MM` 均设置 `EnableDesignIntersectionCheck=false`；报告为 `projects/hfss_sma_connector/reports/home_set_design_intersection_check_false_20260804.json`。

2026-08-04 暂停状态：

- 端口命名原则：生成是什么样，就是什么样；自动流程不得把 pin interface port 重命名为人为统一名称。
- 网格设置原则：连接器夹具默认关闭 design-level intersection checks；后续 validate/solve 前需用只读检查或保存后的 AEDT 字段确认该选项已关闭。
- 当前环境原则：家里电脑使用 `home` profile 和 `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT`；不要把公司 `company_connector` 路径当作当前验证路径。

- 已停止继续写 AEDT 工程，等待明天继续验证。
- DUAL 端口被用户删除后，`add_connector_pin_iports.py --project-config config\projects\hfss_sma_connector.json --placement dual` 可以正确从 profile 选中 ID `68/69`，但一次性多选执行未生成端口。
- 单独对 DUAL component ID `68` 执行 `AddPinIPorts` 可生成 `Pin_T1`；单独对 ID `69` 执行未新增端口，原因初判为两个 small connector 内部 pin 名均为 `Pin_T1`，AEDT 不允许第二个同名 IPort 自动创建。
- `odesign.RenamePort("Pin_T1", "Port1")` 对当前 3D Layout schematic IPort 失败；已确认端口不应改名，后续取消 `PortN` 标准命名要求，改为保留 AEDT generated port name 并建立 logical port mapping。
- 新增 `tools/hfss/inspect_schematic_iports.py` 用于只读读取 `SchematicEditor.GetAllPorts()` 和 IPort 属性；明天继续前先运行该脚本确认当前 GUI/保存状态。

当前 2026-08-03 Home profile 首次结果：

- 项目目录：`projects/hfss_sma_connector/microstrip_connector/`
- baseline：`100 mm` P1-to-P2 理想 50R through line，历史 score 字段来自旧滤波器后处理脚本，后续按 connector full-band score 重新生成。
- connector surrogate：中间 `100 mm` 50R 微带 + 两端各 `3.5 mm` launch，历史 score 字段来自旧滤波器后处理脚本，后续按 connector full-band score 重新生成。
- delta compare：后续统一按 0.5-10 GHz 的 S21 平均/最差劣化、最差回波劣化和 S21 ripple 输出。
- 结论：默认 Route A surrogate launch 严重失配，下一步先做连接器 launch 参数 DoE；完整 3D SMA 模型导入放到 Route C。

### Phase 3: 连接处参数优化

- [x] 建立首批 DoE 参数表：先覆盖 small pad、long taper、L2 cut-out、via relief，不超过 8 个候选。
- [x] 在 layout schema/generator 中增加 L2 reference-plane cut-out 字段和几何输出；实现前先在 plan 中登记参数，避免手工修改 AEDT。
- [x] 在 layout schema/generator 中增加高阻抗串联补偿段字段：`series_hi_z_enabled`、`series_hi_z_l_mm`、`series_hi_z_w_mm`、`series_hi_z_offset_x_mm`。
- [ ] 仅当 0.5-10 GHz 全频带内呈现稳定局部单峰失配时，再增加 stub 补偿字段：`stub_type`、`stub_l_mm`、`stub_w_mm`、`stub_offset_x_mm`；宽带首轮不默认启用 stub。
- [ ] 先跑 `IDEAL_50R_CPW_30MM` 无连接器 baseline，再跑 `SINGLE_END_SMA_CPW_30MM` 当前连接器对比，生成 delta 指标。
- [x] 用 HFSS 批量运行微带线+连接器联合仿真候选。
- [ ] 基于 score 和 delta 指标生成下一批局部候选。
- [ ] 判断对称设计和非对称补偿哪一种更优。

2026-08-05 公司电脑优化迭代归档：

- 当前公司工程为 `D:\Work\ADS\HFSS_VERDICT\hfss_sma_connector_cpw.aedt`，design 为 `SINGLE_END_SMA_CPW_30MM`，AEDT version 为 `2026.1`，host Python 为 `D:\Microsoft\Python\ads-automation\Scripts\python.exe`。
- 本轮真实替换遵守“只替换 P1 PCB launch 版图，不动连接器和既有端口”的边界。保留连接器端口 `S1_1_Pin_T1` 与 PCB 远端端口 `Port1`；版图替换脚本默认不创建 P1 PCB 端口，只有显式 `--recreate-pcb-output-port` 时才重建 `output_feed/P2` 侧 PCB 端口。
- `small_pad_l2_rect_same_anchor_a` 已完成非图形版图替换、求解和导出。结果路径为 `projects\hfss_sma_connector\simulations\single_end_connector_50r_30mm\results\small_pad_l2_rect_same_anchor_a\single_30mm_small_pad_l2_rect_same_anchor_a_score.csv`。
- 当前最佳已求解候选为 `small_pad_l2_rect_same_anchor_a`：`optimization_cost=62.636`，`connector_score=37.364`，状态 `TUNE`；全频带最差回波为 `s22=-8.76 dB @ 7.3 GHz`，`s21_min=-3.07 dB`，`s21_avg=-1.09 dB`，`s21_ripple=2.96 dB`。
- 对比历史候选，`small_pad_l2_rect_same_anchor_a` 明显优于 `small_pad_same_anchor_a` 和 `series_hi_z_same_anchor_a`，后两者 `optimization_cost` 约为 `150+`，不作为下一轮优先方向。
- Smith 指标显示 `smith_z_r_min/max=0.50/1.76`、`smith_z_x_min/max=-0.80/0.71`，当前 tuning hint 为 `reduce_pad_capacitance_or_add_short_series_inductance`。下一轮仍按减小焊盘电容或极短串联高阻抗补偿推进，不引入 stub。
- 因 L2 被挖空，已在 generator/schema/HFSS layout builder 中加入 `reference_ground_plane`，用于生成完整 L3 参考层。`small_pad_l2_rect_l3_same_anchor_a` 已生成 layout JSON、params JSON 和 SVG；SVG 展示 `L1 ETCH_TOP` 与 `L2 ETCH_INNER1`，并包含 `L3 ETCH_INNER2` 的 `l3_ground_plane`。
- `small_pad_l2_rect_l3_same_anchor_a` 目前只完成 dry-run，尚未写入 AEDT 工程、尚未 solve。dry-run 报告为 `projects\hfss_sma_connector\reports\single_30mm_small_pad_l2_rect_l3_same_anchor_a_layout_only_local_dry_run_20260805.json`，选中对象包含 `p1_l2_cutout_rect` 与 `l3_ground_plane`，且未触碰 schematic connector instance 和 IPort。
- 下次执行真实 L3 替换前必须先备份 `.aedt` 和 `.aedb`；`.aedtresults` 如存在锁定的 `.semaphore` 文件，可跳过该类临时锁文件。执行后跳过 Validate，直接按 `Setup_0p5to10G` / `Sweep_0p5to10G_96pt` 求解导出。
- 后处理必须继续使用连接器独立评分 `connector_fullband_v1`，频段为 `0.5-10 GHz` 全频带，不再使用任何滤波器或 `6-8 GHz` passband 口径。

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
