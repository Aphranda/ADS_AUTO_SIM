# FR4 L3 折叠 SIR 带通滤波器分支

Status: Active
Domain: DEVICE
Canonical: `docs/devices/FR4折叠SIR带通滤波器分支.md`
Related: `docs/README.md`, `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
Last updated: 2026-08-01
Owner: ADS Automation

更新时间：2026-07-31

## 1. 分支目的

基于 `SIM/projects/bfp_6_8g_i7_fr4/references/6g_bpf_report/6G宽带带通滤波器文章分析报告.html` 中的折叠阶跃阻抗谐振器方案，建立一个新的 6-8 GHz 低成本 FR4 L3 参考分支。

本分支不是直接复刻文章 Rogers 4003C 尺寸，而是抽象文章结构中的关键自由度，形成可被现有 ADS 自动化闭环消费的参数化候选：

- 紫色部分为左右镜像的 via 加载 U 形谐振器，包含底部横臂、竖臂、顶部横臂，中间按图示保留 `S2` 开缝耦合；其中分支/竖臂采用较窄 `W1`，耦合横段采用较宽 `W2`，打孔位置使用独立方形铜皮。
- 橙色部分为左右对称的折叠线 / 折叠 SIR 加载线，并在下横段中心保留接地点，橙色 via 同样使用独立方形铜皮。
- 左右 50 Ω 馈线外移，通过窄尖锥与紫色 U 形谐振器形成小面积直接重叠接入，避免宽线过渡覆盖大面积谐振器区域。
- 50 Ω 馈线宽度采用 ADS LineCalc 结果 `2.35421 mm`（FR4 L3，h = 1.2906 mm）。
- 保留 `t1 / S1 / S2 / d1 / d2` 作为首轮优化变量。
- 基板固定为 FR4 L3 参考：L1 signal、L2 keepout、L3 ground，h = 1.2906 mm。

## 2. 环境区分

OneDrive 目录在公司和家里电脑共享，但 ADS 工作目录、Library、普通 Python 环境可能不同。自动化脚本必须通过 profile 区分环境。

配置入口：

```text
SIM/tools/ads_profiles.py
```

已维护 profile：

```text
company -> D:\Work\ADS\6-8G_Fillter\6-8G_Fillter, Library = 6-8G_Fillter_lib
home    -> D:\Work\ADS\BFP\BFP, Library = BFP_lib
```

家里普通主控 Python：

```text
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
```

ADS OA/RFPro API 仍由 ADS 自带 Python 执行：

```text
D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

运行 ADS 自动化时不要手动硬编码这些路径，优先使用：

```powershell
--profile company
--profile home
```

## 3. 新增文件

版图生成器：

```text
SIM/tools/generate_folded_sir_bpf_layout.py
```

首轮参数表：

```text
SIM/projects/bfp_6_8g_i7_fr4/plans/folded_sir_bpf_l3_round0.csv
```

首轮版图输出：

```text
SIM/projects/bfp_6_8g_i7_fr4/layouts/folded_sir_bpf_l3_round0/
```

输出文件包含：

```text
<candidate>.dxf
<candidate>_mm_coords.dxf
<candidate>_ads_mil_coords.dxf
<candidate>.svg
<candidate>_params.json
<candidate>_drc.txt
```

## 4. Round0 候选

| 候选 | 调整项 | 意图 |
|---|---|---|
| `folded_sir_l3_r0_base` | 基准 | 按文章/实物图量级建立的 FR4 L3 紫色 U 形谐振器 + 对称橙色折叠线首版 |
| `folded_sir_l3_r0_t1_080` | `t1` 由 1.00 mm 降到 0.80 mm | 比较较短馈入尖锥对端口匹配和外部耦合的影响 |
| `folded_sir_l3_r0_s1_020` | `S1` 由 0.24 mm 降到 0.20 mm | 增强紫色 U 形谐振器与橙色折叠线之间的主耦合，观察带宽和零点变化 |
| `folded_sir_l3_r0_d1_010` | `d1` 由 0.00 mm 增到 0.10 mm | 将紫色 U 形谐振器底部 via pad 从末端补偿位置向内回退，观察模式分裂和高边零点 |

首版 DRC 结果：

```text
Minimum metal width: 0.18 mm -> PASS
Minimum coupling/feed gap: 0.24 mm -> PASS
Via drawing diameter: 0.30 mm -> PASS
Via square pad size: 0.42 mm -> PASS
Core resonator bounding box: about 7.45 mm x 5.74 mm
Total metal bounding box with feeds: about 15.69 mm x 6.80 mm
Purple U W1 branch width: 0.24 mm
Purple U W2 coupling width: 0.76 mm
Feed taper length t1: 1.00 mm
Feed taper tip width: 0.18 mm
Feed taper overlap into Purple U: 0.08 mm
```

尺寸说明：

- `Core resonator bounding box` 对应紫色 U 形谐振器 + 橙色折叠线主体，更接近文章和实物照片中标注的滤波器有效尺寸。
- `Total metal bounding box with feeds` 包含左右 50 Ω 馈线，用于 ADS 端口导入和 EM 边界检查，不应直接与论文中的滤波器主体尺寸混用。

## 5. 生成命令

```powershell
python SIM\tools\generate_folded_sir_bpf_layout.py `
  --plan SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round0.csv `
  --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0
```

## 6. ADS 单候选测试命令

公司电脑示例：

```powershell
python SIM\tools\run_ads_filter_candidate.py folded_sir_l3_r0_base `
  --profile company `
  --template-cell DA_SSBFilter1_Step_R `
  --target-profile fr4_25db `
  --dxf SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0\folded_sir_l3_r0_base_mm_coords.dxf `
  --params SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0\folded_sir_l3_r0_base_params.json `
  --cell folded_sir_l3_r0_base_mm_coords `
  --overwrite-setup
```

家里电脑示例：

```powershell
python SIM\tools\run_ads_filter_candidate.py folded_sir_l3_r0_base `
  --profile home `
  --template-cell BFP `
  --target-profile fr4_25db `
  --dxf SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0\folded_sir_l3_r0_base_mm_coords.dxf `
  --params SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0\folded_sir_l3_r0_base_params.json `
  --cell folded_sir_l3_r0_base_mm_coords `
  --overwrite-setup
```

建议首跑先加：

```powershell
--skip-fem
```

确认 ADS 版图、via、端口、EM Setup 均正确后，再启动 FEM。

## 7. Round0 FEM 结果

仿真时间：2026-07-31 10:11-10:14

运行入口：

```powershell
python SIM\tools\run_ads_filter_sweep.py `
  --profile company `
  --plan SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round0.csv `
  --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round0 `
  --results-dir SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round0 `
  --summary SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round0\sweep_summary.csv `
  --skip-generate `
  --template-cell DA_SSBFilter1_Step_R `
  --target-profile fr4_25db `
  --candidates folded_sir_l3_r0_base folded_sir_l3_r0_t1_080 folded_sir_l3_r0_s1_020 folded_sir_l3_r0_d1_010 `
  --continue-on-error
```

输出文件：

```text
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round0\sweep_summary.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round0\<candidate>_mm_coords_rfpro.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round0\<candidate>_mm_coords_score.csv
```

| 候选 | 峰值频点 / S21 | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---:|---:|---:|---:|---:|---|
| `folded_sir_l3_r0_base` | 6.300 GHz / -1.24 dB | -2.03 dB | -21.92 dB | -25.87 dB | -26.07 dB | 只有 6.3 GHz 附近窄峰，未形成 6-8 GHz 宽通带 |
| `folded_sir_l3_r0_t1_080` | 6.300 GHz / -1.54 dB | -2.27 dB | -21.94 dB | -25.39 dB | -26.07 dB | 缩短馈入尖锥未明显改善高端通带 |
| `folded_sir_l3_r0_s1_020` | 6.342 GHz / -1.35 dB | -2.38 dB | -16.52 dB | -30.00 dB | -28.68 dB | 减小 S1 可抬高 7 GHz，但 8 GHz 更差，仍不是宽通带 |
| `folded_sir_l3_r0_d1_010` | 6.330 GHz / -1.25 dB | -2.18 dB | -18.33 dB | -26.67 dB | -26.73 dB | via 位置内移有轻微改善，但方向不足 |

阶段结论：

- 当前折叠 SIR round0 已跑通自动化闭环，ADS 导入、端口、EM Setup、RFPro FEM、评分均正常。
- 当前结构主要表现为 6.3 GHz 附近窄通带/谐振峰，高端 7-8 GHz 未打开。
- `S1` 减小是四个方向里对 7 GHz 改善最明显的变量，但会牺牲 8 GHz，说明单纯加强橙紫耦合不足以形成目标宽通带。
- 下一轮不建议只做小步微调，应优先增加电长度/耦合自由度，或重新确认折叠线接地点与 U 形谐振器的物理拓扑。

## 8. 参数、零点与耦合分析

### 8.1 当前响应的物理判断

目标 6-8 GHz 带通对应中心频率约 7 GHz，分数带宽约 28.6%。这种宽带响应需要两个条件同时满足：

- 端口外部耦合足够强，输入/输出能量能有效进入谐振器，等效外部 Q 不能太高。
- 相邻谐振模式之间的耦合足够强，多个传输极点需要展开并覆盖 6-8 GHz，而不是只形成一个窄峰。

Round0 的 EM 结果显示，所有候选都只有 6.30-6.34 GHz 附近一个主要传输峰，同时在 7.17-7.39 GHz 出现很深的传输零点：

| 候选 | 主传输峰 | 主要传输零点 | 说明 |
|---|---:|---:|---|
| `folded_sir_l3_r0_base` | 6.300 GHz / -1.24 dB | 7.177 GHz / -67.28 dB | 深零点落在目标通带中部 |
| `folded_sir_l3_r0_t1_080` | 6.300 GHz / -1.54 dB | 7.171 GHz / -60.69 dB | 改馈入长度不能移走零点 |
| `folded_sir_l3_r0_s1_020` | 6.342 GHz / -1.35 dB | 7.387 GHz / -48.03 dB | 加强橙紫耦合后零点上移、变浅 |
| `folded_sir_l3_r0_d1_010` | 6.330 GHz / -1.25 dB | 7.249 GHz / -54.69 dB | via 位置内移使零点轻微上移 |

因此当前结构不是标准 6-8 GHz 宽带 BPF，而更像“6.3 GHz 窄带通 + 7.2 GHz 附近陷波 + 高端阻带”。下一轮优化的首要目标不是继续微调插损，而是把 7.2 GHz 附近的传输零点移出目标通带，或者改变耦合符号/耦合路径，使该模式成为通带内的传输极点。

### 8.2 传输极点与零点来源

传输极点主要来自紫色 via 加载 U 形谐振器的偶/奇模谐振，以及橙色折叠 SIR 与紫色 U 之间的耦合模。极点落在目标通带内时表现为 S21 上升，多个极点展开后才能形成宽带通。

传输零点主要来自两类机制：

- **谐振器支路短路型零点**：橙色折叠线带中心接地 via，本质上引入一个对主通路耦合的接地谐振支路；当该支路在某个频率呈现低阻抗时，会把能量旁路到地，形成陷波零点。
- **多路径相消型零点**：紫色 U 形谐振器、橙色折叠线、左右直接馈入之间存在多条电磁耦合路径；当两条路径幅度接近、相位相反时，输出端电压相消，形成有限频率传输零点。

Round0 中 `S1` 从 0.24 mm 降到 0.20 mm 后，零点从 7.177 GHz 上移到 7.387 GHz，并且深度由 -67.28 dB 变浅到 -48.03 dB。这说明 7.2 GHz 附近零点高度受橙色折叠线与紫色 U 之间的耦合控制，橙色结构不是被动旁观者，而是当前通带中部陷波的主要来源之一。

### 8.3 关键参数影响

| 参数 | 主要控制对象 | 增大时的典型影响 | 减小时的典型影响 | 对当前问题的判断 |
|---|---|---|---|---|
| `feed_gap_t1_mm` | 50 Ω 线到紫色 U 的尖锥变换长度 | 过渡更平缓，外部耦合略减，端口不连续性减小 | 外部耦合略增，但不连续性增加 | `t1=1.00 -> 0.80` 基本不移动 7.2 GHz 零点，说明当前瓶颈不是馈入长度 |
| `feed_tip_w_mm` | 馈入尖端局部接触宽度 | 外部耦合增强，通带峰可能变宽，但过大易形成寄生直通 | 外部耦合减弱，峰值变窄、插损变差 | 可作为匹配细调，不应作为 round1 主变量 |
| `feed_overlap_mm` | 馈入与紫色 U 的直接重叠面积 | 外部耦合增强，可能引入直接路径零点 | 外部耦合减弱，通带更窄 | 当前只重叠 0.08 mm，已偏保守；除非 S11 明显改善需求，不优先大扫 |
| `lower_arm_l1_mm` | 紫色 U 的主电长度 | 主极点整体下移，模式间距可能变小 | 主极点上移，模式间距可能变大 | 若目标是把 6.3 GHz 峰推向 7 GHz，可缩短；但单独缩短会把零点也可能带入/带出通带 |
| `lower_span_l2_mm` | 紫色 U 顶部跨度和等效电长度 | 主极点下移，左右谐振器耦合几何同时变化 | 主极点上移，结构更紧凑 | 影响较大，适合 round1 做粗扫 |
| `lower_top_bridge_w_mm` | 紫色顶部宽耦合段阻抗和缝隙电容 | 阻抗降低、电容增强，耦合增强，零点可能更靠近通带 | 阻抗升高、耦合减弱，通带更窄 | 当前 W2=0.76 mm 明显宽于分支，可扫 0.60-0.90 mm 看零点位置 |
| `lower_bottom_l2_mm` | 紫色底部接地臂长度和 via 加载位置 | 接地支路电长度增加，主极点/零点倾向下移 | 电长度减小，主极点/零点倾向上移 | 与 `d1` 一起控制接地边界，适合联动扫 |
| `via_offset_d1_mm` | 紫色 via 相对底部臂末端的位置 | via 远离末端，接地边界改变，零点上移且变浅 | via 更靠近末端，零点下移且更强 | 实测 `d1=0.10` 只轻微改善，说明需要更大拓扑/电长度调整 |
| `main_gap_s1_mm` | 紫色 U 与橙色折叠线之间的主耦合 | 耦合减弱，橙色支路对主通道影响变弱 | 耦合增强，极点/零点分裂增强 | 当前最敏感；减小 S1 抬高 7 GHz，但让 8 GHz 更差，不能单独继续压小 |
| `side_gap_s2_mm` | 左右紫色 U 顶部开缝耦合 | 耦合减弱，带宽收窄，峰更孤立 | 耦合增强，两个主模更可能展开成宽通带 | 当前未扫；应作为 round1 重点变量，受 6 mil 下限约束 |
| `upper_fold_h_mm` | 橙色折叠 SIR 的垂直电长度 | 橙色支路谐振/零点下移 | 橙色支路谐振/零点上移 | 当前零点在 7.2 GHz，若确认它来自橙色支路，减小该值可尝试把零点推向高边阻带 |
| `upper_left_l3_mm` | 橙色顶部折叠臂有效长度 | 橙色支路零点下移，支路加载增强 | 零点上移，支路加载减弱 | 当前应优先尝试缩短，观察 7.2 GHz 零点是否上移到 8.5-9 GHz |
| `upper_right_l4_mm` | 橙色半跨度上限 | 小于几何上限时增大会增加折叠线长度 | 减小时缩短橙色跨度、零点上移 | 当前 `upper_right_l4=4.35` 被 `lower_span_l2/2 - upper_margin_x=3.525` 限制，继续增大无效 |
| `upper_margin_x_mm` | 橙色结构离紫色外侧的边距 | 橙色跨度缩短，零点上移、耦合减弱 | 橙色跨度加长，零点下移、耦合增强 | 可作为推动橙色零点离开通带的有效变量 |
| `fold_offset_d2_mm` | 橙色顶部中心开口/折叠余量 | 顶部臂缩短，零点上移、中心耦合减弱 | 顶部臂变长，零点下移、耦合增强 | 若要把 7.2 GHz 零点推到高边，应增大 d2 或缩短 L3 |

### 8.4 带通与带阻调参方向

若目标是形成 6-8 GHz 宽带通：

- 先把 7.2 GHz 附近传输零点移出通带；优先缩短橙色折叠 SIR 的有效长度，即减小 `upper_left_l3_mm / upper_fold_h_mm`，或增大 `fold_offset_d2_mm / upper_margin_x_mm`。
- 再增强紫色 U 之间的主通带耦合；优先减小 `side_gap_s2_mm`，让左右谐振模式展开，而不是继续只减小 `main_gap_s1_mm`。
- 如果主峰仍在 6.3 GHz 偏低，可适度缩短 `lower_arm_l1_mm / lower_span_l2_mm / lower_bottom_l2_mm`，把主极点向 7 GHz 提。
- `feed_tip_w_mm / feed_overlap_mm / feed_gap_t1_mm` 放在后期做匹配和插损优化，不建议作为移动零点的主手段。

若目标是增强带阻/陷波：

- 将橙色折叠 SIR 的零点放在需要抑制的频点，例如 5 GHz 或 9 GHz；增大橙色有效长度会使零点下移，缩短橙色有效长度会使零点上移。
- 减小 `main_gap_s1_mm` 可增强陷波深度和支路耦合，但可能把陷波拉进通带，必须配合橙色电长度一起调整。
- 增大 via pad 或改变 via 位置会改变支路对地电感/电容，适合微调零点深度，但不适合单独决定零点频率。

### 8.5 Round1 建议 sweep 组合

Round1 建议先做少量正交候选，而不是一次扫太多变量：

| 方向 | 参数组合 | 目的 |
|---|---|---|
| 移走通带内零点 | `upper_left_l3_mm` 减小、`upper_fold_h_mm` 减小、`fold_offset_d2_mm` 增大 | 将 7.2 GHz 陷波推向 8.5-9 GHz 以上 |
| 打开主通带 | `side_gap_s2_mm` 减小到 0.18-0.20 mm | 增强左右紫色 U 的主耦合，增加极点分裂 |
| 抬高主峰 | `lower_arm_l1_mm / lower_span_l2_mm` 小幅缩短 | 将 6.3 GHz 主峰推近 7 GHz |
| 保持阻带 | `main_gap_s1_mm` 不再单独减小，优先与橙色长度联动 | 避免 7-8 GHz 中部再次形成深陷波 |

### 8.6 Round1 参数修改

已按上述原理导向新增 Round1 参数表：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round1.csv
```

并生成版图/参数/DRC 文件：

```text
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round1\
```

Round1 不覆盖 Round0，便于结果对比。所有 Round1 候选的 DRC 均通过，最小金属宽度为 0.18 mm，最小耦合/间隙不低于 0.18 mm，满足 6 mil 加工能力。

| 候选 | 修改方向 | 关键参数 | 预期作用 |
|---|---|---|---|
| `folded_sir_l3_r1_zup_l3210` | 单独缩短橙色顶部臂 | `upper_left_l3_mm=2.10` | 判断 7.2 GHz 零点是否由橙色顶部臂主控，并尝试上移零点 |
| `folded_sir_l3_r1_zup_h160` | 单独缩短橙色垂直折叠高度 | `upper_fold_h_mm=1.60` | 判断橙色垂直电长度对零点位置的敏感性 |
| `folded_sir_l3_r1_zup_combo` | 强零点上移组合 | `upper_left_l3_mm=2.10`、`upper_fold_h_mm=1.60`、`fold_offset_d2_mm=0.90`、`upper_margin_x_mm=0.35`、`main_gap_s1_mm=0.28` | 缩短橙色有效长度并减弱橙紫陷波耦合，目标是把通带内零点推到高边 |
| `folded_sir_l3_r1_s2_018` | 打开紫色 U 主耦合 | `side_gap_s2_mm=0.18` | 增强左右紫色 U 模式分裂，观察 6-8 GHz 是否出现更宽通带 |
| `folded_sir_l3_r1_short_main` | 抬高主传输峰 | `lower_arm_l1_mm=3.42`、`lower_span_l2_mm=7.15`、`lower_bottom_l2_mm=1.95` | 缩短紫色 U 有效电长度，将 6.3 GHz 主峰推近 7 GHz |
| `folded_sir_l3_r1_wide_combo` | 宽通带组合尝试 | `upper_left_l3_mm=2.10`、`upper_fold_h_mm=1.60`、`fold_offset_d2_mm=0.90`、`side_gap_s2_mm=0.18`、`lower_arm_l1_mm=3.42`、`lower_span_l2_mm=7.15`、`main_gap_s1_mm=0.26` | 同时上移橙色零点、增强紫色主耦合、抬高主峰，作为最积极的宽带候选 |

建议仿真顺序：

1. 先跑 `zup_l3210 / zup_h160 / zup_combo`，确认 7.2 GHz 零点是否能按预期上移。
2. 再跑 `s2_018`，判断只增强紫色主耦合是否能打开通带。
3. 最后跑 `short_main / wide_combo`，看主峰上移和组合调参是否能形成 6-8 GHz 宽通带。

Round1 sweep 命令：

```powershell
python SIM\tools\run_ads_filter_sweep.py `
  --profile company `
  --plan SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round1.csv `
  --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round1 `
  --results-dir SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round1 `
  --summary SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round1\sweep_summary.csv `
  --skip-generate `
  --template-cell DA_SSBFilter1_Step_R `
  --target-profile fr4_25db `
  --continue-on-error
```

### 8.7 Round1 FEM 结果

仿真时间：2026-07-31 10:29-10:34

输出文件：

```text
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round1\sweep_summary.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round1\<candidate>_mm_coords_rfpro.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round1\<candidate>_mm_coords_score.csv
```

| 候选 | 主传输峰 | 主要通带内谷值 / 零点趋势 | S21@6 GHz | S21@7 GHz | S21@8 GHz | 判断 |
|---|---:|---:|---:|---:|---:|---|
| `folded_sir_l3_r1_zup_l3210` | 6.511 GHz / -1.19 dB | 7.778 GHz / -46.61 dB | -3.65 dB | -2.80 dB | -33.90 dB | 缩短橙色顶部臂有效，零点从 7.18 GHz 推到 7.78 GHz，但仍压住高边 |
| `folded_sir_l3_r1_zup_h160` | 6.486 GHz / -1.19 dB | 7.670 GHz / -49.62 dB | -3.42 dB | -3.91 dB | -31.20 dB | 缩短橙色垂直高度也有效，但零点上移幅度略小于缩短顶部臂 |
| `folded_sir_l3_r1_zup_combo` | 6.656 GHz / -1.23 dB | 8.125 GHz / -45.74 dB | -5.50 dB | -2.04 dB | -33.42 dB | 强零点上移组合有效，7 GHz 已打开，但 8 GHz 被高边零点压住 |
| `folded_sir_l3_r1_s2_018` | 6.330 GHz / -1.34 dB | 7.171 GHz / -61.43 dB | -2.31 dB | -21.46 dB | -25.41 dB | 单独减小 S2 无法移走陷波，说明高边问题仍由橙色支路主控 |
| `folded_sir_l3_r1_short_main` | 6.474 GHz / -1.58 dB | 7.237 GHz / -56.29 dB | -3.62 dB | -14.53 dB | -24.74 dB | 缩短紫色 U 可抬高主峰，但不解决橙色零点 |
| `folded_sir_l3_r1_wide_combo` | 6.895 GHz / -1.25 dB、7.387 GHz / -1.76 dB | 8.162 GHz / -51.16 dB | -6.76 dB | -1.36 dB | -25.63 dB | 最接近宽带方向，已形成 6.9/7.4 GHz 双峰，但高边零点仍太低 |

Round1 结论：

- 原理判断成立：缩短橙色折叠 SIR 有效长度会显著上移原来 7.2 GHz 附近的深零点。
- `upper_left_l3_mm` 和 `upper_fold_h_mm` 都有效，其中缩短顶部臂 `upper_left_l3_mm` 对零点上移略更直接。
- `s2_018` 单独增强紫色 U 主耦合基本无效，说明在橙色陷波零点没有移出通带前，单独增加主耦合无法形成宽通带。
- `wide_combo` 是当前最优方向：6.9 GHz 和 7.4 GHz 已形成双传输峰，7 GHz 插损约 -1.36 dB；主要问题变成 8.16 GHz 零点过低，导致 8 GHz 附近 S21 仍只有约 -25.63 dB。
- 下一轮应以 `wide_combo` 为基准，继续把橙色零点从 8.16 GHz 推到 9 GHz 附近，同时略增强低边耦合，改善 6 GHz 的 -6.76 dB。

Round2 建议：

- 继续缩短橙色有效长度：`upper_left_l3_mm` 可从 2.10 mm 继续降到 1.80 / 1.60 mm；`upper_fold_h_mm` 可从 1.60 mm 降到 1.45 / 1.30 mm。
- 继续增大顶部中心开口：`fold_offset_d2_mm` 可从 0.90 mm 增到 1.05 / 1.20 mm，目标是把高边零点推到 8.8-9.2 GHz。
- 保持或略放大 `main_gap_s1_mm` 到 0.28-0.32 mm，避免橙色支路耦合过强导致陷波压回通带。
- 保持 `side_gap_s2_mm=0.18 mm`，必要时只做 0.16 mm 的加工极限验证，不建议立即压到 6 mil 下限。
- 低边 6 GHz 偏弱可通过轻微增加馈入耦合补偿，例如 `feed_tip_w_mm=0.20` 或 `feed_overlap_mm=0.10`，但应放在高边零点推走之后再细调。

### 8.8 Round2 参数与 FEM 结果

已新增 Round2 参数表：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round2.csv
```

已生成版图/参数/DRC 文件：

```text
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round2\
```

Round2 输出文件：

```text
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round2\sweep_summary.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round2\<candidate>_mm_coords_rfpro.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round2\<candidate>_mm_coords_score.csv
```

Round2 全部候选 DRC 通过，其中 `S2=0.16 mm` 的候选仍高于 6 mil 最小能力 `0.1524 mm`，但已接近加工边界。

| 候选 | 主要改动 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---|
| `folded_sir_l3_r2_base_wide` | 复跑 `r1_wide_combo` | -12.23 dB | -6.76 dB | -1.36 dB | -25.63 dB | -25.28 dB | 基准：中段好，高边零点太低 |
| `folded_sir_l3_r2_zhi_l180` | `upper_left_l3=1.80`、`d2=1.05`、`S1=0.28` | -12.67 dB | -7.47 dB | -1.39 dB | -11.87 dB | -27.67 dB | 高边明显改善，但 6 GHz 仍弱 |
| `folded_sir_l3_r2_zhi_h145` | `upper_fold_h=1.45`、`S1=0.28` | -17.34 dB | -8.63 dB | -1.32 dB | -8.59 dB | -27.08 dB | 高边继续改善，低边更弱 |
| `folded_sir_l3_r2_zhi_strong` | `upper_fold_h=1.35`、`upper_left_l3=1.60`、`d2=1.20`、`S1=0.32` | -20.69 dB | -11.34 dB | -2.79 dB | -4.02 dB | -31.69 dB | 高边目标基本达成，8 GHz 可用，但 6 GHz 明显不足 |
| `folded_sir_l3_r2_s2_016` | `S2=0.16` | -10.91 dB | -6.73 dB | -1.38 dB | -20.30 dB | -27.22 dB | 单独压 S2 对高边帮助有限 |
| `folded_sir_l3_r2_feed_boost` | `feed_tip=0.20`、`feed_overlap=0.10` | -11.98 dB | -6.43 dB | -1.54 dB | -39.40 dB | -23.84 dB | 低边只轻微改善；该结果只有 20 点，需视为趋势参考 |
| `folded_sir_l3_r2_balanced` | 高边上移 + `S2=0.16` + 馈入增强 + 紫色 U 略加长 | -16.12 dB | -7.80 dB | -1.54 dB | -9.58 dB | -29.04 dB | 折中方向较稳，但 6/8 GHz 仍未达 -5 dB |

Round2 局部极值判断：

- `r2_zhi_strong` 已将主要高边零点推到约 9.135 GHz，9 GHz 抑制约 -31 dB，证明“继续缩短橙色折叠 SIR + 放大 S1”可以把高边陷波移出通带。
- `r2_zhi_strong` 在 7.273 GHz 和 8.306 GHz 附近形成两个传输峰，说明高边带通形态已经建立；但低边 6 GHz 只有 -11.34 dB，低端极点/外部耦合不足。
- `r2_zhi_l180 / r2_zhi_h145 / r2_balanced` 把 8 GHz 改善到 -8 至 -12 dB，说明高边改善是连续可控的，不是偶然跳变。
- 单独压 `S2` 或单独增强馈入不足以解决问题；下一轮应在 `r2_zhi_strong` 的橙色高边零点基础上，恢复低边极点。

Round3 建议：

- 以 `r2_zhi_strong` 为高边基准，适度加长紫色 U：`lower_arm_l1_mm` 从 3.42 回到 3.50-3.60 mm，`lower_span_l2_mm` 从 7.15 回到 7.25-7.35 mm，目标是把低边极点拉回 6.0-6.3 GHz。
- 保留橙色强上移结构：`upper_fold_h_mm=1.35-1.45`、`upper_left_l3_mm=1.60-1.80`、`fold_offset_d2_mm=1.20`、`main_gap_s1_mm=0.30-0.32`。
- 馈入增强只做辅助变量：`feed_tip_w_mm=0.20`、`feed_overlap_mm=0.10` 可保留，但不应指望单独修复低边。
- `S2=0.16` 虽可加工但裕量小，若电性能没有明显收益，优先回到 `S2=0.18`。

### 8.9 Round3 FEM 结果

已完成 Round3 参数表、版图生成、DRC 与自动 FEM 仿真：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round3.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l3_round3\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round3\sweep_summary.csv
```

Round3 共 8 组候选，全部 DRC 通过，全部 RFPro 输出为 1000 点数据。

| 候选 | 主要方向 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---|
| `r3_zhi_ref` | 复跑 `r2_zhi_strong` | -20.69 dB | -11.34 dB | -2.79 dB | -4.02 dB | -31.69 dB | 高边可用，低边不足 |
| `r3_l350_s725` | 紫色 U 中等加长 | -17.02 dB | -9.15 dB | -1.72 dB | -3.71 dB | -42.94 dB | 低边改善约 2.2 dB，是强橙色组里较优 |
| `r3_l360_s735` | 紫色 U 继续加长 | -31.11 dB | -11.50 dB | -1.92 dB | -4.15 dB | -36.17 dB | 加长过多后低侧零点靠近 5 GHz，6 GHz 反而变差 |
| `r3_l370_s745` | 紫色 U 接近早期长度 | -31.02 dB | -10.73 dB | -1.62 dB | -3.33 dB | -41.70 dB | 高边好，6 GHz 仍不足 |
| `r3_l360_feed` | 加长紫色 U + 增强馈入 | -15.67 dB | -14.01 dB | -2.07 dB | -4.88 dB | -40.43 dB | 馈入增强引入低频杂散峰，低边恶化 |
| `r3_l360_s1_030` | S1 从 0.32 降到 0.30 | -28.32 dB | -12.37 dB | -2.51 dB | -4.29 dB | -30.46 dB | 主耦合增强未修复低边 |
| `r3_l360_s2_016` | S2 压到 0.16 mm | -24.16 dB | -11.94 dB | -2.09 dB | -4.23 dB | -37.68 dB | 接近 6 mil 下限但收益不明显 |
| `r3_mild_orange` | 减弱橙色高边控制 | -12.99 dB | -8.30 dB | -1.34 dB | -3.90 dB | -43.44 dB | 6 GHz 最好，但 5 GHz 抑制不足 |

Round3 结论：

- 紫色 U 适度恢复长度可以改善 6 GHz，但不是单调关系；`l350_s725` 以后低侧零点逐步靠近 5 GHz，6 GHz 重新变差。
- `r3_mild_orange` 说明降低橙色折叠线约束可改善低边插损，但代价是 5 GHz 抑制降到约 13 dB，不满足 20 dB 阻带目标。
- `S2=0.16 mm` 与馈入增强均未形成决定性收益，因此不建议继续优先压加工极限或扩大馈入重叠。

### 8.10 Round4 FEM 结果

Round4 以 `r3_mild_orange` 和 `r3_l350_s725` 为基础，扫描紫色线宽、顶端耦合臂宽度和中等橙色加载：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round4.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round4\sweep_summary.csv
```

Round4 共 9 组候选，全部 DRC 通过，全部 RFPro 输出为 1000 点数据。

| 候选 | 主要方向 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---|
| `r4_mild_ref` | 复跑 `r3_mild_orange` | -12.99 dB | -8.30 dB | -1.34 dB | -3.90 dB | -43.44 dB | 低边较好，5 GHz 不足 |
| `r4_mild_l350` | mild 橙色 + l350 紫色 | -17.96 dB | -8.92 dB | -1.45 dB | -2.26 dB | -42.25 dB | 8 GHz 明显改善，6 GHz 未突破 |
| `r4_mild_l340` | 紫色 U 缩短 | -18.01 dB | -10.97 dB | -1.90 dB | -3.17 dB | -30.95 dB | 低边恶化 |
| `r4_mild_l370` | 紫色 U 加长 | -22.19 dB | -8.54 dB | -1.96 dB | -8.69 dB | -28.88 dB | 5 GHz 达标但高边被拉低 |
| `r4_mild_w028` | 紫色分支加宽到 0.28 mm | -17.44 dB | -8.70 dB | -1.34 dB | -4.21 dB | -32.37 dB | 低边略改善但 5 GHz 不足 |
| `r4_mild_topw085` | 紫色顶臂加宽到 0.85 mm | -21.60 dB | -8.70 dB | -1.77 dB | -8.51 dB | -29.55 dB | 5 GHz 达标，高边恶化 |
| `r4_mild_wide_combo` | 分支与顶臂同时加宽 | -15.10 dB | -7.92 dB | -1.37 dB | -6.55 dB | -31.97 dB | 6 GHz 当前最好，但 8 GHz 不足 |
| `r4_moderate_orange` | 中等橙色加载 | -15.81 dB | -9.41 dB | -1.37 dB | -2.38 dB | -45.57 dB | 高边好，低边不足 |
| `r4_l350_moderate_orange` | l350 + 中等橙色加载 | -40.79 dB | -10.05 dB | -1.58 dB | -2.61 dB | -37.74 dB | 阻带好但 6 GHz 不足 |

Round4 结论：

- 加宽紫色分支和顶端耦合臂可以降低 6 GHz 插损，最佳为 `r4_mild_wide_combo`，S21@6 GHz 约 -7.92 dB。
- 顶端耦合臂加宽会把高边零点拉低，导致 8 GHz 插损变差；这是 Round4 的主要矛盾。
- 中等橙色加载可恢复 8 GHz，但通常会牺牲 6 GHz，说明当前结构在低边和高边之间存在明显折中。

### 8.11 Round5 FEM 结果与阶段判断

Round5 在 `r4_mild_wide_combo` 基础上增强橙色高边零点控制，验证能否同时保住 6 GHz 与 8 GHz：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l3_round5.csv
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l3_round5\sweep_summary.csv
```

Round5 共 8 组候选，全部 DRC 通过，全部 RFPro 输出为 1000 点数据。

| 候选 | 主要方向 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---|
| `r5_wide_ref` | 复跑 `r4_mild_wide_combo` | -15.10 dB | -7.92 dB | -1.37 dB | -6.55 dB | -31.97 dB | 低边最好但高边不足 |
| `r5_wide_moderate_orange` | 加宽紫色 + 中等橙色 | -17.25 dB | -8.87 dB | -1.36 dB | -2.85 dB | -35.61 dB | 8 GHz 恢复，6 GHz 变差 |
| `r5_wide_zhi_orange` | 加宽紫色 + 强橙色 | -18.88 dB | -11.24 dB | -1.65 dB | -3.82 dB | -40.87 dB | 高边好，低边明显不足 |
| `r5_wide_zhi_s1_030` | 强橙色 + S1=0.30 | -35.30 dB | -10.25 dB | -1.53 dB | -2.97 dB | -44.43 dB | 阻带好，低边不足 |
| `r5_w028_moderate_orange` | 仅分支加宽 + 中等橙色 | -15.92 dB | -9.15 dB | -1.51 dB | -2.30 dB | -37.83 dB | 低边不足 |
| `r5_topw085_moderate_orange` | 仅顶臂加宽 + 中等橙色 | -22.14 dB | -9.37 dB | -1.35 dB | -2.54 dB | -38.78 dB | 5 GHz 达标，低边不足 |
| `r5_l370_wide_zhi` | 长紫色 + 加宽 + 强橙色 | -25.95 dB | -11.18 dB | -1.53 dB | -3.56 dB | -44.55 dB | 低边不足 |
| `r5_l350_wide_zhi` | 短紫色 + 加宽 + 强橙色 | -42.17 dB | -11.00 dB | -3.04 dB | -4.17 dB | -24.96 dB | 阻带好，通带边缘不足 |

阶段判断：

- Round3-5 已覆盖橙色折叠线长度、S1、S2、紫色 U 长度、紫色分支宽度、紫色顶端耦合臂宽度和馈入重叠等主变量。
- 当前最优低边结果为 `r5_wide_ref / r4_mild_wide_combo`，S21@6 GHz 约 -7.92 dB，但 8 GHz 约 -6.55 dB，且 5 GHz 抑制约 15 dB。
- 当前最优高边/阻带结果可满足 8 GHz 与 9 GHz，但 6 GHz 通常退化到 -9 到 -11 dB。
- 因此，在现有 4 阶 via-loaded folded SIR 拓扑上，6-8 GHz 宽带、FR4 L3、5/9 GHz 约 20 dB 抑制三者同时满足较困难。继续微调仍可能获得 1-2 dB 局部改善，但预计难以稳定达到 6-8 GHz 全带 S21 优于 -5 dB。
- 若继续保留该分支，下一步应考虑拓扑级调整：增加一对低边辅助耦合路径、改为更高阶交指/梳状结构，或回到高低阻抗多节结构并增加可控传输零点。

### 8.12 L1 参考 Round1 复跑

L3 参考结果确认后，改用 L1 参考重新复跑 Round1。ADS 层叠为 `substrate3`：

| 项目 | 参数 |
|---|---:|
| 信号层 | `cond` |
| 参考地 | L1 下方 ground |
| 介质 | FR4, `Er=4.6` |
| 介质厚度 | `0.210 mm` |
| 铜厚 | `0.035 mm` |
| Via 层 | `pcvia1` |
| 50 Ω 线宽 | 约 `0.391 mm`，按 Hammerstad 近似估算 |

为避免仍继承旧 L3 的 EM Setup，已修改自动化脚本：

```text
SIM\tools\ads_clone_emsetup_template.py
```

修改内容：克隆 EM Setup 时优先读取参数 JSON 中的 `parameters.substrate`，因此 L1 复跑会使用 `6-8G_Fillter_lib:substrate3.subst`。本轮 RFPro 日志已确认每个候选的 substrate info 均为：

```text
6-8G_Fillter_lib:substrate3.subst
```

新增 L1-R1 参数与结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l1_round1.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l1_round1\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l1_round1\sweep_summary.csv
```

L1-R1 共 6 组候选，全部 DRC 通过，全部 RFPro 输出为 1000 点数据。DRC 中最小金属宽度不低于 `0.18 mm`，最小耦合/馈入间隙不低于 `0.18 mm`，满足 6 mil 加工能力。

| 候选 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 主要峰值 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---|
| `l1_r1_zup_l3210` | -33.43 dB | -42.89 dB | -41.42 dB | -42.93 dB | -43.59 dB | 5.682 GHz / -12.46 dB | 无有效 6-8 GHz 通带 |
| `l1_r1_zup_h160` | -36.77 dB | -29.43 dB | -42.93 dB | -44.23 dB | -45.00 dB | 5.670 GHz / -11.53 dB | 无有效 6-8 GHz 通带 |
| `l1_r1_zup_combo` | -32.56 dB | -15.94 dB | -42.26 dB | -43.07 dB | -43.83 dB | 6.036 GHz / -12.74 dB | 仅低边出现弱峰，通带断裂 |
| `l1_r1_s2_018` | -32.66 dB | -36.05 dB | -36.91 dB | -38.61 dB | -39.51 dB | 5.399 GHz / -9.45 dB | 峰值低于目标频段且插损较大 |
| `l1_r1_short_main` | -31.47 dB | -39.14 dB | -42.07 dB | -44.41 dB | -45.52 dB | 5.465 GHz / -12.87 dB | 无有效 6-8 GHz 通带 |
| `l1_r1_wide_combo` | -27.64 dB | -47.34 dB | -41.16 dB | -41.91 dB | -43.10 dB | 4.156 GHz / -12.29 dB、6.240 GHz / -12.40 dB | 弱峰分散，6-8 GHz 不可用 |

L1-R1 结论：

- L1 参考下，原 L3 的 R1 几何不能直接沿用。6-8 GHz 内 S21 基本处于 -30 到 -50 dB，S11 接近 0 dB，表现为强反射/弱耦合结构，而非正常带通。
- 主要弱传输峰集中在约 5.4-6.0 GHz，且峰值也只有约 -9 到 -13 dB，说明频率位置和耦合强度都不满足要求。
- L1 的 `0.210 mm` 薄介质显著改变微带等效电长度、接地 via 电感、谐振器阻抗和耦合强度。当前尺寸由 L3 `1.2906 mm` 厚介质演化而来，直接切到 L1 后不再等效。
- 若继续使用 L1 参考，应从 L1 的电长度和阻抗比重新综合，而不是沿用 L3 尺寸。建议下一步新开 `folded_sir_bpf_l1_round0` 或转向更适合薄介质的高低阻抗/交指/梳状结构。

### 8.13 L1 参考 JLC04161H 厚度 Round1 复跑

根据 JLC04161H-7628G 层叠重新修改 L1 参考介质厚度。L1 到 L2 的介质由三层 PP 构成：

```text
0.2180 mm + 0.2180 mm + 0.0764 mm = 0.5124 mm
```

本轮参数：

| 项目 | 参数 |
|---|---:|
| 信号层 | `cond` |
| 参考地 | L2 |
| 介质 | FR4, `Er=4.6` |
| 介质厚度 | `0.5124 mm` |
| 铜厚 | `0.035 mm` |
| Via 层 | `pcvia1` |
| 50 Ω 线宽 | 约 `0.9545 mm`，按 Hammerstad 近似估算 |

新增参数与结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l1_h512_round1.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l1_h512_round1\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l1_h512_round1\sweep_summary.csv
```

本轮共 6 组候选，全部 DRC 通过，RFPro 日志确认使用 `6-8G_Fillter_lib:substrate3.subst`。其中 `l1h512_r1_short_main` 只输出 20 点，应仅作为趋势参考；其余候选为 1000 点数据。

| 候选 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 主峰/零点 | 判断 |
|---|---:|---:|---:|---:|---:|---|---|
| `l1h512_r1_zup_l3210` | -27.37 dB | -2.64 dB | -36.05 dB | -32.85 dB | -33.86 dB | 峰 5.934/-2.18 dB、6.258/-2.94 dB；零点 6.811/-48.72 dB | 6 GHz 较好，但 7 GHz 被零点压制 |
| `l1h512_r1_zup_h160` | -32.24 dB | -3.89 dB | -31.01 dB | -32.20 dB | -33.51 dB | 峰 5.772/-2.57 dB、6.084/-3.48 dB；零点 6.547/-45.42 dB | 低频窄带，零点太低 |
| `l1h512_r1_zup_combo` | -21.46 dB | -8.23 dB | -33.45 dB | -32.34 dB | -32.77 dB | 峰 6.168/-3.07 dB、6.577/-3.64 dB；零点 7.117/-49.07 dB | 峰向上移动，但 6 GHz 变弱 |
| `l1h512_r1_s2_018` | -23.73 dB | -26.88 dB | -27.03 dB | -29.82 dB | -31.15 dB | 峰 5.465/-2.19 dB；零点 6.072/-39.27 dB | 峰低于目标频段 |
| `l1h512_r1_short_main` | -20.80 dB | -8.01 dB | -25.61 dB | -28.89 dB | -31.09 dB | 20 点趋势：峰约 5.688/-1.60 dB，零点约 6.250/-38.07 dB | 数据点少，仅看趋势 |
| `l1h512_r1_wide_combo` | -12.78 dB | -13.24 dB | -23.11 dB | -28.26 dB | -29.68 dB | 峰 6.330/-2.19 dB、6.703/-3.16 dB；零点 7.153/-42.75 dB | 峰最接近 6-7 GHz，但 5 GHz 抑制不足且高边断裂 |

阶段结论：

- 相比 `h=0.210 mm` 的 L1 复跑，`h=0.5124 mm` 明显改善。部分候选已在 5.9-6.7 GHz 形成 -2 到 -4 dB 的传输峰。
- 但当前仍不是 6-8 GHz 宽带带通，而是 6 GHz 附近窄带通加 6.5-7.2 GHz 深传输零点。
- `zup_l3210` 的 6 GHz 表现最好，S21@6 GHz 约 -2.64 dB，5/9 GHz 抑制也足够；主要问题是零点在 6.811 GHz，导致 7-8 GHz 无法通过。
- `wide_combo` 已将双峰推到 6.330/6.703 GHz，但零点仍在 7.153 GHz，说明橙色折叠线有效长度仍偏长，零点需要继续上移。
- 下一轮 L1 h512 优先方向：以 `zup_l3210` 或 `wide_combo` 为基准，继续缩短橙色折叠 SIR 有效长度，重点调 `upper_left_l3_mm`、`upper_fold_h_mm`、`fold_offset_d2_mm` 和 `main_gap_s1_mm`，目标是把 6.8-7.2 GHz 零点推到 8.8-9.2 GHz 附近。

### 8.14 L1 参考 JLC04161H 厚度 Round2 结果

Round2 在 L1 h=0.5124 mm Round1 的基础上，继续缩短橙色折叠 SIR 有效长度，并调整 `fold_offset_d2_mm / main_gap_s1_mm / side_gap_s2_mm`，验证通带内深零点能否上移到高边阻带。

新增参数与结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l1_h512_round2.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l1_h512_round2\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l1_h512_round2\sweep_summary.csv
```

| 候选 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `r2_zup_ref` | 5.934 GHz / -2.18 dB | 6.811 GHz / -48.72 dB | -27.20 dB | -2.64 dB | -36.13 dB | -32.85 dB | -33.86 dB | 复跑 Round1 低边较优项，确认零点仍压在通带内 |
| `r2_zup_l180` | 6.300 GHz / -2.52 dB | 7.285 GHz / -49.77 dB | -18.17 dB | -13.75 dB | -20.97 dB | -32.61 dB | -32.79 dB | 零点上移，但 6 GHz 明显变弱 |
| `r2_zup_l160` | 6.535 GHz / -2.91 dB | 7.586 GHz / -51.78 dB | -17.38 dB | -25.54 dB | -4.01 dB | -34.92 dB | -33.13 dB | 7 GHz 打开，高边零点仍低，低边塌陷 |
| `r2_zup_strong` | 6.865 GHz / -3.79 dB | 8.060 GHz / -54.58 dB | -15.73 dB | -37.01 dB | -6.18 dB | -45.19 dB | -34.13 dB | 零点可继续上移，但只剩中高段窄峰 |
| `r2_wide_ref` | 6.330 GHz / -2.19 dB | 7.153 GHz / -42.75 dB | -12.72 dB | -13.24 dB | -22.82 dB | -28.26 dB | -29.68 dB | 双峰低于目标中心，5 GHz 抑制不足 |
| `r2_wide_l180` | 6.750 GHz / -6.15 dB | 7.750 GHz / -43.06 dB | -10.85 dB | -40.87 dB | -8.79 dB | -33.35 dB | -31.31 dB | 高边零点上移，低边完全断裂 |
| `r2_wide_l160` | 6.955 GHz / -3.42 dB | 8.030 GHz / -46.51 dB | -8.93 dB | -24.55 dB | -3.74 dB | -43.50 dB | -29.70 dB | 7/7.5 GHz 可用，但 6 GHz 与 8 GHz 不足 |
| `r2_wide_strong` | 7.279 GHz / -4.83 dB | 8.420 GHz / -51.87 dB | -8.03 dB | -20.64 dB | -19.64 dB | -9.34 dB | -32.68 dB | 高边向上，但中间仍被零点/弱耦合割裂 |

Round2 结论：

- 缩短橙色折叠线有效长度的方向正确，零点可以从 6.8-7.2 GHz 推到 7.6-8.4 GHz。
- 零点上移会同步削弱 6 GHz 低边极点，表现为 6 GHz 从约 -2.6 dB 快速退化到 -20 dB 以下。
- 说明当前结构的橙色折叠线同时承担高边零点控制和通带模式耦合；单独上移零点会破坏低边通带。
- Round3 应尝试在保持橙色零点上移的基础上，通过加长紫色 U、减小 `S2` 和小幅增强馈入来恢复低边极点。

### 8.15 L1 参考 JLC04161H 厚度 Round3 结果

Round3 以 `r2_zup_l160 / r2_wide_l160 / r2_wide_strong` 为基础，尝试恢复紫色 U 电长度、增强紫色主耦合和馈入耦合。

新增参数与结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_l1_h512_round3.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_l1_h512_round3\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_l1_h512_round3\sweep_summary.csv
```

| 候选 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `r3_zup_l160_ref` | 6.535 GHz / -2.91 dB | 7.586 GHz / -51.78 dB | -17.42 dB | -25.54 dB | -4.06 dB | -34.92 dB | -33.13 dB | 复跑基准，7 GHz 可用但两端断裂 |
| `r3_zup_l160_s2_018` | 6.553 GHz / -2.89 dB | 7.538 GHz / -48.28 dB | -15.55 dB | -29.10 dB | -4.00 dB | -32.07 dB | -30.97 dB | 减小 S2 未恢复低边 |
| `r3_zup_l160_long` | 6.498 GHz / -3.18 dB | 7.610 GHz / -54.10 dB | -19.79 dB | -25.27 dB | -4.77 dB | -36.39 dB | -33.82 dB | 紫色 U 加长后低边仍不足 |
| `r3_zup_l160_long_s2` | 6.505 GHz / -2.91 dB | 7.538 GHz / -50.33 dB | -17.56 dB | -26.35 dB | -4.61 dB | -33.08 dB | -31.46 dB | 加长 + S2=0.18 无决定性收益 |
| `r3_zup_mid_s2` | 6.474 GHz / -2.79 dB | 7.520 GHz / -52.55 dB | -17.72 dB | -22.90 dB | -6.02 dB | -33.48 dB | -32.01 dB | 低边略改善，但 7 GHz 已退化 |
| `r3_wide_l160_long` | 6.853 GHz / -4.01 dB | 7.874 GHz / -47.65 dB | -12.62 dB | -27.13 dB | -7.20 dB | -37.52 dB | -30.48 dB | 传输峰上移，低边仍断裂 |
| `r3_wide_strong_long` | 7.063 GHz / -4.37 dB | 6.474 GHz / -47.36 dB、8.138 GHz / -49.97 dB | -14.41 dB | -25.45 dB | -6.25 dB | -33.08 dB | -31.35 dB | 形成中段窄峰，低/高边均不足 |
| `r3_wide_strong_feed` | 7.027 GHz / -3.79 dB | 6.342 GHz / -49.01 dB、8.204 GHz / -52.38 dB | -15.68 dB | -28.00 dB | -4.07 dB | -29.89 dB | -32.23 dB | 馈入增强未恢复低边，且仍有强零点 |

Round3 结论：

- 当前 L1 h=0.5124 mm 折叠 SIR 结构可以稳定形成 6.5-7.6 GHz 附近的窄带传输峰，但 6 GHz 和 8 GHz 两端无法同时打开。
- 加长紫色 U、减小 `S2`、增强馈入只改变局部峰值和零点深度，未把响应转化为连续 6-8 GHz 带通。
- 该结构的主要矛盾已经比较明确：橙色折叠接地支路用于生成高边零点时，会在通带内部引入强陷波；削弱橙色支路可改善低边，但阻带抑制会下降。
- 基于当前三轮 L1 h512 结果，继续做小步尺寸微调预计收益有限。若目标仍要求 6-8 GHz 连续带通、FR4、阻带约 20 dB，建议进入拓扑级修改：增加谐振阶数、增加低边辅助耦合路径，或切换到高低阻抗多节/梳状/交指带通结构。

### 8.16 RO4350 folded SIR 单板对照

根据 ADS 当前层叠，新增 RO4350 材料对照板。该板不做电长度缩放，只将 L1 h512 中低边较优的 `l1h512_r1_zup_l3210` 几何迁移到 RO4350 材料，用于判断问题主要来自材料损耗/介电常数，还是来自 folded SIR 拓扑本身。

层叠参数：

| 项目 | 参数 |
|---|---:|
| ADS substrate | `substrate1` |
| 介质 | Rogers_RO4350 |
| Er | `3.66` |
| 介质厚度 | `0.51 mm` |
| 铜厚 | `0.035 mm` |
| 信号层 | `cond` |
| Via 层 | `pcvia1` |
| 50 Ω 线宽 | `1.1252 mm`，按 Hammerstad 近似估算 |

新增参数、版图和结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_ro4350_round0.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_ro4350_round0\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_ro4350_round0\sweep_summary.csv
```

自动化流程已确认 EM Setup 使用：

```text
6-8G_Fillter_lib:substrate1.subst
```

| 候选 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@6.5 GHz | S21@7 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `folded_sir_ro4350_r0_zup_ref` | 6.523 GHz / -1.06 dB、6.895 GHz / -1.38 dB | 7.411 GHz / -56.33 dB、5.736 GHz / -54.85 dB | -11.48 dB | -19.87 dB | -1.17 dB | -5.92 dB | -30.79 dB | -31.80 dB | 峰值插损明显改善，但仍是窄带双峰 + 通带内深零点 |

RO4350 单板结论：

- RO4350 材料降低损耗后，6.5-6.9 GHz 的峰值插损可到约 -1 dB，说明材料对峰值插损有明显帮助。
- 响应仍然没有形成连续 6-8 GHz 宽带带通，7.411 GHz 处仍有约 -56 dB 的深零点，8 GHz 仍处于阻带。
- 同一几何从 FR4 h512 切到 RO4350 后，主峰和零点整体上移，符合较低介电常数导致电长度变短的趋势。
- 因此 folded SIR 当前瓶颈不是单纯 FR4 损耗，而是拓扑/耦合路径：橙色接地折叠支路仍把高边零点压在目标通带内。
- 若继续 RO4350 folded SIR，可基于该单板做一轮尺寸调整：适度加长紫色 U 以恢复 6 GHz，继续缩短或减弱橙色接地折叠支路以把 7.4 GHz 零点推到 8.5-9 GHz 以上。但预计仍需要增加阶数或辅助耦合路径，才能稳定覆盖 6-8 GHz。

### 8.17 RO4350 folded SIR Round1 零点偏移

Round1 目标是偏移 RO4350 单板中 7.411 GHz 的通带内深零点。调参方向为缩短橙色折叠 SIR 有效长度，并适度放大 `S1`，降低橙色接地支路对通带中部的陷波加载。

新增参数、版图和结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_ro4350_round1.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_ro4350_round1\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_ro4350_round1\
```

| 候选 | 主要调整 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@6.5 GHz | S21@7 GHz | S21@7.5 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `r0_zup_ref` | RO4350 基准 | 6.523 GHz / -1.06 dB、6.895 GHz / -1.38 dB | 7.411 GHz / -56.33 dB | -11.44 dB | -19.87 dB | -1.17 dB | -5.68 dB | -38.52 dB | -30.79 dB | -31.80 dB | 基准：低中段有双峰，高边零点压入通带 |
| `r1_zero_up_l180` | `upper_fold_h=1.70`、`upper_left_l3=1.80`、`S1=0.26`、`d2=0.85` | 6.907 GHz / -1.27 dB、7.363 GHz / -1.71 dB | 7.934 GHz / -61.37 dB、6.078 GHz / -57.76 dB | -10.02 dB | -35.21 dB | -16.49 dB | -2.41 dB | -9.85 dB | -43.35 dB | -32.13 dB | 中等偏移有效，但低边零点进入 6 GHz 附近 |
| `r1_zero_up_l160` | `upper_fold_h=1.60`、`upper_left_l3=1.60`、`S1=0.28`、`d2=1.00` | 7.153 GHz / -1.73 dB、7.718 GHz / -2.81 dB | 8.360 GHz / -68.97 dB、6.282 GHz / -61.53 dB | -10.25 dB | -26.33 dB | -26.42 dB | -6.48 dB | -5.59 dB | -19.51 dB | -33.26 dB | 强偏移把高边零点推出 8 GHz，但低边断裂更明显 |

Round1 结论：

- 零点偏移方向成立：缩短橙色折叠 SIR 后，高边零点从 7.411 GHz 分别上移到 7.934 GHz 和 8.360 GHz。
- 代价也很明确：高边零点上移后，低边会出现新的深零点，`l180` 在约 6.078 GHz，`l160` 在约 6.282 GHz，导致 6 GHz 侧严重断裂。
- `l180` 更适合作为下一轮基准，因为 6.9/7.36 GHz 双峰较强，且零点刚好接近 8 GHz；`l160` 高边偏移更充分，但 6.5 GHz 已被压到约 -26 dB。
- 下一轮不建议继续单纯缩短橙色折叠线，而应在 `l180` 基础上恢复低边：适度加长紫色 U 主电长度，或增加低边辅助耦合路径，同时保持橙色零点不回落到 7.4 GHz。

### 8.18 RO4350 folded SIR Round2 低边极点恢复

Round2 以 `r1_zero_up_l180` 为基准，尝试通过加长紫色 U、减小 `S2`、加宽紫色顶部耦合段和增强馈入来恢复低边极点。

新增参数、版图和结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_ro4350_round2.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_ro4350_round2\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_ro4350_round2\sweep_summary.csv
```

| 候选 | 主要调整 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@6.5 GHz | S21@7 GHz | S21@7.5 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `r2_l180_long` | 紫色 U 加长 | 6.625 GHz / -3.04 dB、7.250 GHz / -4.13 dB | 5.875 GHz / -60.32 dB、7.875 GHz / -49.61 dB | -13.38 dB | -30.52 dB | -7.83 dB | -6.79 dB | -18.84 dB | -38.55 dB | -32.58 dB | 仅 20 点趋势，低边仍断裂 |
| `r2_l180_s2_020` | `S2=0.20` | 6.919 GHz / -1.39 dB、7.405 GHz / -1.97 dB | 6.180 GHz / -55.55 dB、7.934 GHz / -59.45 dB | -8.74 dB | -27.91 dB | -18.77 dB | -2.42 dB | -7.27 dB | -42.11 dB | -31.44 dB | 双极点增强，但低边零点进入 6.2 GHz |
| `r2_l180_long_s2` | 紫色 U 加长 + `S2=0.20` | 6.835 GHz / -1.26 dB、7.285 GHz / -1.70 dB | 5.952 GHz / -60.58 dB、7.928 GHz / -64.39 dB | -13.26 dB | -40.79 dB | -13.29 dB | -3.30 dB | -14.05 dB | -44.11 dB | -32.45 dB | 峰值很好，但 6 GHz 和 8 GHz 两端被零点切断 |
| `r2_l180_long_s2_topw082` | 加宽紫色顶部 W2 | 6.835 GHz / -1.37 dB、7.303 GHz / -1.74 dB | 6.090 GHz / -56.25 dB、7.826 GHz / -57.29 dB | -11.46 dB | -34.29 dB | -15.08 dB | -3.67 dB | -14.84 dB | -34.63 dB | -29.91 dB | 顶部加宽未补回低边 |
| `r2_l180_long_s2_feed` | 增强馈入 | 6.715 GHz / -1.33 dB、7.159 GHz / -1.78 dB | 5.970 GHz / -57.26 dB、7.700 GHz / -59.14 dB | -11.84 dB | -42.48 dB | -9.49 dB | -4.04 dB | -25.49 dB | -33.28 dB | -31.20 dB | 馈入增强不能解决通带内零点 |

Round2 结论：

- 加长紫色 U 与减小 `S2` 能形成较强的两个传输极点，峰值插损约 -1.3 到 -2.0 dB。
- 低边和高边仍存在强传输零点，典型位置约 6.0-6.2 GHz 与 7.7-7.9 GHz，目标 6-8 GHz 被切成两段。
- 因此问题不是“极点数量完全不够”，而是已有极点被两个有限频率零点夹住；继续加强馈入或单纯压 `S2` 只会改变峰值，不会形成连续宽通带。

### 8.19 RO4350 folded SIR Round3 补极点验证

Round3 继续沿“补极点/拓宽通带”方向验证：保留较长紫色 U 以尝试恢复低边传输极点，同时进一步缩短或减弱橙色接地折叠 SIR，将高边零点推出 8 GHz。

新增参数、版图和结果：

```text
SIM\projects\bfp_6_8g_i7_fr4\plans\folded_sir_bpf_ro4350_round3.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\folded_sir_bpf_ro4350_round3\
SIM\projects\bfp_6_8g_i7_fr4\results\folded_sir_bpf_ro4350_round3\sweep_summary.csv
```

其中 `r3_pole_mid_l160_s2` 在上次中断后遗留 RFPro view 锁，未纳入本轮有效比较；其余候选为 1000 点 RFPro FEM 数据。

| 候选 | 主要调整 | 主传输峰 | 主要零点 | S21@5 GHz | S21@6 GHz | S21@6.5 GHz | S21@7 GHz | S21@7.5 GHz | S21@8 GHz | S21@9 GHz | 判断 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `r3_pole_long_l160_s2` | 长紫色 U + 短橙色 SIR + `S2=0.20` | 7.171 GHz / -1.40 dB、7.682 GHz / -1.83 dB | 6.336 GHz / -59.31 dB、8.318 GHz / -68.92 dB | -10.96 dB | -25.80 dB | -29.64 dB | -7.62 dB | -4.76 dB | -21.72 dB | -32.69 dB | 高边零点已外推，但低边零点进入 6.3 GHz |
| `r3_pole_long_l160_s1_030` | 放大 `S1=0.30` | 7.021 GHz / -1.35 dB、7.508 GHz / -1.97 dB | 6.240 GHz / -57.54 dB、8.072 GHz / -60.76 dB | -11.14 dB | -27.37 dB | -23.01 dB | -1.52 dB | -1.98 dB | -39.03 dB | -30.78 dB | 7-7.5 GHz 最好，但 6 GHz 与 8 GHz 两端断裂 |
| `r3_pole_long_l150_s2` | 进一步缩短橙色 SIR | 7.357 GHz / -1.60 dB、7.916 GHz / -2.07 dB | 6.486 GHz / -60.31 dB、8.607 GHz / -88.46 dB | -11.10 dB | -24.37 dB | -52.56 dB | -16.39 dB | -4.35 dB | -5.96 dB | -35.99 dB | 高端极点接近 8 GHz，但 6.5 GHz 被深零点压制 |
| `r3_pole_long_l160_topw068` | 紫色顶部 W2 降到 0.68 mm | 7.153 GHz / -1.45 dB、7.646 GHz / -1.78 dB | 6.294 GHz / -58.69 dB、8.288 GHz / -69.08 dB | -10.85 dB | -26.45 dB | -27.23 dB | -6.33 dB | -4.18 dB | -23.45 dB | -32.55 dB | 顶部减载对低边零点无决定性改善 |

Round3 结论：

- 进一步缩短橙色折叠 SIR 可以有效把高边零点推到 8.1-8.6 GHz，并在 7.5-7.9 GHz 产生高端传输极点。
- 同时低边零点会从约 6.0 GHz 上移到 6.24-6.49 GHz，直接压入目标通带低端。
- 当前拓扑存在明显的零点/极点耦合跷跷板：橙色支路越短，高边越容易打开，但低边深零点越靠近 6.5 GHz；橙色支路越长，低边较好，高边零点又落回 7.4-7.9 GHz。
- 因此仅靠现有 `L1/L2/W2/S1/S2/d2/feed` 参数，预计难以得到连续 6-8 GHz、最差 S21 优于 -5 dB 的宽带通。

补充极点的建议路径：

- 增加低边辅助谐振单元：在输入/输出馈入附近或紫色 U 底部外侧增加一对短路加载支路，目标在 6.0-6.4 GHz 形成额外传输极点，用来填平当前 6.2-6.5 GHz 深陷波。
- 增加交叉耦合路径：在左右紫色 U 的上部或中部增加可控弱耦合桥/缝隙耦合，使相消零点从通带内移动到阻带，而不是只依赖橙色接地支路控制零点。
- 将 4 阶结构扩展到 5-6 阶：当前两个主极点覆盖 7-7.9 GHz 不足以覆盖 28.6% 分数带宽，新增谐振器应优先补低边极点，再用橙色支路保留 8.5-9 GHz 抑制。
- 下一轮若继续 folded SIR，不建议再扫 `feed_tip_w/feed_overlap` 作为主变量；应优先修改生成器，加入低边辅助支路的参数化选项，再做 `aux_len / aux_gap / aux_via_offset / S1 / orange_len` 联合扫描。

### 8.20 原文拓扑复现版 Round0

基于重新核对原文图 3.1(a) 和谐振传输线模型，新增一个独立的“原文拓扑复现版”分支。该分支不沿用前面 simplified folded SIR 的假设，而是按原文视觉关系和物理模型重建：

- 橙色折叠 SIR 位于上方，紫色双模 SIR 位于下方，左右 50 Ω 馈线位于紫色下端附近；SVG/DXF 均按原文方向输出，避免人工核图时上下颠倒。
- 左右 50 Ω 馈线采用间隙耦合，`t1` 表示馈线与紫色谐振器之间的外部耦合间距；不再使用 taper 直接搭接紫色区域。
- 紫色双模 SIR 顶部为连续 `Z2, θ2` 线段，两侧竖臂/下方加载段对应 `Z1, θ1`，不再把紫色顶部按 `S2` 切开。
- 橙色折叠 SIR 默认不加中心接地 via，避免把原文的耦合谐振单元误建成强短路陷波支路。
- `Z1/Z2/Z3` 线宽先按 RO4350 `Er=3.66, h=0.51 mm` 的一阶微带近似建立：约 `0.206 / 0.510 / 0.267 mm`，后续需用 ADS LineCalc/FEM 校准。

新增文件：

```text
SIM\tools\generate_paper_mixed_sir_bpf_layout.py
SIM\projects\bfp_6_8g_i7_fr4\plans\paper_mixed_sir_bpf_ro4350_round0.csv
SIM\projects\bfp_6_8g_i7_fr4\layouts\paper_mixed_sir_bpf_ro4350_round0\
```

首版候选：

| 候选 | 层叠 | 核心尺寸 | 关键建模差异 | DRC |
|---|---|---:|---|---|
| `paper_sir_ro4350_r0_base` | `substrate1`，RO4350，`h=0.51 mm` | `7.45 mm x 5.604 mm` | 原文方向；间隙馈电；紫色顶部连续；橙色无中心接地 via | PASS |

生成命令：

```powershell
python SIM\tools\generate_paper_mixed_sir_bpf_layout.py `
  --plan SIM\projects\bfp_6_8g_i7_fr4\plans\paper_mixed_sir_bpf_ro4350_round0.csv `
  --out-dir SIM\projects\bfp_6_8g_i7_fr4\layouts\paper_mixed_sir_bpf_ro4350_round0
```

后续仿真入口：

```powershell
python SIM\tools\run_ads_filter_candidate.py paper_sir_ro4350_r0_base `
  --profile company `
  --template-cell DA_SSBFilter1_Step_R `
  --target-profile fr4_25db `
  --dxf SIM\projects\bfp_6_8g_i7_fr4\layouts\paper_mixed_sir_bpf_ro4350_round0\paper_sir_ro4350_r0_base_mm_coords.dxf `
  --params SIM\projects\bfp_6_8g_i7_fr4\layouts\paper_mixed_sir_bpf_ro4350_round0\paper_sir_ro4350_r0_base_params.json `
  --cell paper_sir_ro4350_r0_base_mm_coords `
  --out SIM\projects\bfp_6_8g_i7_fr4\results\paper_mixed_sir_bpf_ro4350_round0\paper_sir_ro4350_r0_base_mm_coords_rfpro.csv `
  --score-out SIM\projects\bfp_6_8g_i7_fr4\results\paper_mixed_sir_bpf_ro4350_round0\paper_sir_ro4350_r0_base_mm_coords_score.csv `
  --log-file SIM\projects\bfp_6_8g_i7_fr4\results\paper_mixed_sir_bpf_ro4350_round0\paper_sir_ro4350_r0_base_mm_coords_flow.log `
  --overwrite-setup
```

## 9. 后续优化 TODO

1. 已完成 `folded_sir_l3_r0_base / t1_080 / s1_020 / d1_010` 自动 FEM 仿真。
2. 已完成 Round1 自动 FEM 仿真，确认橙色折叠 SIR 有效长度是传输零点主控变量。
3. 已完成 Round2 自动 FEM 仿真，确认 `r2_zhi_strong` 可将高边零点推到约 9.1 GHz，但低边 6 GHz 明显不足。
4. 已完成 Round3 自动 FEM 仿真，确认恢复紫色 U 长度只能有限改善 6 GHz，且存在低侧零点靠近 5 GHz 的副作用。
5. 已完成 Round4 自动 FEM 仿真，确认紫色分支/顶臂加宽可改善 6 GHz，但会压低高边零点。
6. 已完成 Round5 自动 FEM 仿真，确认增强橙色高边控制可恢复 8 GHz，但会再次牺牲 6 GHz。
7. 已完成 L1 参考 Round1 复跑，确认原 L3 几何直接迁移到 L1 后不形成有效 6-8 GHz 带通。
8. 已完成 L1 JLC04161H 厚度 `h=0.5124 mm` Round1 复跑，确认 6 GHz 可形成较好传输峰，但高边零点仍落在 6.8-7.2 GHz。
9. 已完成 L1 JLC04161H 厚度 `h=0.5124 mm` Round2/Round3 复跑，确认橙色零点可上移，但 6 GHz 低边极点无法同时保持。
10. 已完成 RO4350 `substrate1` folded SIR 单板对照，确认材料可改善峰值插损，但不能消除通带内深零点。
11. 已完成 RO4350 folded SIR Round1 零点偏移，确认高边零点可从 7.411 GHz 推到 7.934/8.360 GHz，但低边新零点会进入 6.1-6.3 GHz。
12. 已完成 RO4350 folded SIR Round2/Round3 补极点验证，确认现有 4 阶拓扑可形成较强双极点，但低边和高边零点无法同时移出 6-8 GHz。
13. 已建立原文拓扑复现版 Round0，修正旧版的上下方向、直接搭接馈电、紫色顶部切缝和橙色中心接地 via 假设。
14. 评分继续按 FR4 低成本目标：
   - 5 GHz 抑制 >= 20 dB。
   - 9 GHz 抑制 >= 20 dB。
   - 6-8 GHz 内最差 S21 优先提升到 -5 dB 以内。
15. 若继续旧 simplified folded SIR 分支，优先做拓扑级调整，而不是继续单点尺寸微调：
   - 增加低边辅助耦合路径或额外谐振单元。
   - 将当前 4 阶结构扩展到 5-6 阶。
   - 改用更适合宽带的梳状/交指结构。
   - 与高低阻抗多节结构对比，保留尺寸、损耗和加工容差较优的方案。


