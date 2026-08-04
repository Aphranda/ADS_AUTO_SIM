# HFSS/pyAEDT Backend 流程

Last updated: 2026-08-04

## 目标

用 HFSS 3D Layout 作为 ADS/RFPro 之外的标准仿真 backend。当前仍保留“裁决/复核”用途：对 ADS/RFPro 的关键候选做独立复核，判断当前七阶 FR4 交指带通滤波器在 `S11/S22` 上的漂移是否来自 ADS 模板、端口、拟合数据源或版图本身。后续标准 pipeline 入口通过 `simulation_backends=ads_rfpro|hfss3dlayout|both` 选择 ADS、HFSS 或双后端运行。

## 当前基线

- HFSS 安装根目录：`D:\Hardware\ANAYS`
- AEDT 可执行文件：`D:\Hardware\ANAYS\ANSYS Inc\v261\AnsysEM\ansysedt.exe`
- pyAEDT 环境：`D:\Microsoft\Python\ads-automation`
- AEDT 版本参数：`2026.1`
- 公司电脑滤波器/常规 HFSS 工作区：`D:\Work\ADS\SIMADS_STANDARD\HFSS`
- Home/历史 round13 滤波器 HFSS 工作区：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT`
- 连接器专用 HFSS 工作区：`D:\Work\ADS\HFSS_VERDICT`，仅用于 `hfss_sma_connector` 微带线+连接器联合仿真，不作为滤波器候选工作区。
- 当前裁决输入：`projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round13_retest_4to10_40\i7_fr4_r13_retest_base_l555_taper_layout.json`
- 当前自动化主 route：`hfss3dlayout_aedt_edge_gap_gnd_port_edges`，CLI 可用 `--route reliable` 展开。
- 当前主层叠配置：`config\stackups\JLC04161H_7628_1P6MM.json`

## AEDT 工程文件访问边界

- 禁止把 `.aedt` 当文本文件做结构性修改；端口、net、component instance、layout、layer、setup、boundary 和 sweep 的变更必须走 AEDT/pyAEDT/EDB API 或 GUI。
- `.aedt` 文本读取只允许用于已保存工程的只读审计、差异分析和报告生成；只读脚本不得写回 `.aedt`、`.aedb` 或 `.aedtresults`。
- 如果 API 修改失败，应记录失败命令、设计名、对象名和 AEDT 错误，再决定补 API adapter 或人工 GUI 操作；不得自动退回到字符串替换。
- 真实 API 写入前必须备份 `.aedt`、`.aedb`、`.aedtresults`，同一 AEDT 工程必须串行操作，避免并行 gRPC/pyAEDT 会话。

## 建模策略

优先使用 `Hfss3dLayout`，因为它和 ADS/RFPro 一样是平面版图 EM 模型，适合比较微带、via、层叠和端口影响。普通 `Hfss` 3D 实体模型作为第二阶段方案，只有在 3D Layout 端口或层叠难以对齐时再启用。

脚本直接读取 `_layout.json`：

- 使用配置化层叠时，`cond` 矩形和多边形映射到 `stackup.geometry.signal_layer`，当前为 `ETCH_TOP`。
- 底层 `GND` 创建实际地平面几何，避免只建层、不建参考导体。当前两端口交指滤波器使用 `--gnd-boundary-mode port-edges`，让 GND 左右边界对齐 Port1/Port2 截面；Y 方向仍沿用原始 `EM_BOUNDARY`。
- GND 铜皮映射到 `stackup.geometry.reference_ground_layer`，当前为 `ETCH_INNER1`。
- `pcvia1` via 映射为 `stackup.geometry.via_top_layer` 到 `stackup.geometry.via_bottom_layer` 的接地 via，当前为 `ETCH_TOP` 到 `ETCH_BOTTOM`，并在信号层增加接地 pad。
- net 分配：输入馈线 `IN`，输出馈线 `OUT`，交指短截线和 via 为 `GND`。
- 当前主层叠使用 `JLC04161H_7628_1P6MM` 配置：`ETCH_TOP` 到 `ETCH_INNER1` 参考地间距 `0.2104 mm`，7628 prepreg `Dk=4.4`、loss tangent 暂取 `0.02`。未传 `--stackup-config` 时才回退到旧的 `GND / FR4_CORE / TOP` 简化模型。
- 默认端口：使用 `aedt-edge`，即由 `Hfss3dLayout.create_edge_port()` 让 AEDT 原生创建 GUI 可见端口，但不再传 `reference_primitive/reference_edge_number`，避免生成 `AddRefPort` 到 GND 外边缘的 circuit port。
- 当前端口锚点按 layout JSON 端口坐标匹配馈线外侧边：Port1 为 `input_feed` 左边，Port2 为 `output_feed` 右边。AEDT 矩形 edge 编号实测为 `top=0,left=1,bottom=2,right=3`。
- 当前 GND 范围：原始 EM boundary 为 `x=-5.04..8.5502mm`，修正后的 HFSS GND 为 `x=-3.54..7.0502mm`、`y=-1.5..7.5323mm`，使端口参考落在 GND 边界且位于端口截面正下方。
- 当前 `aedt-edge` 读回位置：Port1 signal=`(-3.54, 1.95) mm`，Port2 signal=`(7.0502, 1.95) mm`。两者均为 `EdgeTerminal`、`is_circuit=False`、`terminal_type=edge`，且 `reference_terminal=None`。
- 自动端口属性对齐人工端口基准：`HFSS Type=Gap`、`Orientation=Vertical`、`Reference=GND:GND:hfss_ground_plane`、`Renormalize=true`、`Renormalize Impedance=50ohm`、`DeembedParasiticPortInductance=false`、`PEC Launch Width=0.04mm`。
- 旧的 `aedt-edge + AddRefPort` 路线会保存为 `HFSS Type=Circuit`、`CircuitPort=true`，并把参考落到 GND 平面外边缘中点；这与人工 `Port -> Create` 的 gap port 不一致，相关仿真结果只保留作排查记录，不作为裁决数据。
- 旧 pyEDB `edge-gap` 路线的注意事项：端口后处理属性必须通过 `port.core.port_post_processing_prop` 取出、修改、再回写；pyEDB 创建 edge port 后不要再用 AEDT 非图形方式重新打开并保存同一个项目，否则可能抹掉 pyEDB 新建端口。
- 空气盒子/开放区域按当前截图模板默认开启：dielectric bounding box padding `0.005`，airbox bounding box horizontal padding `0.15`，Z 正负 padding `2`，`SyncZExt=true`，`OpenRegionType=Radiation`，`OperFreq=5GHz`，`RadLvl=0`。
- 旧的 edge/circuit/wave 端口方式只作为排查选项保留，默认不再使用。

## 推荐命令

标准 pipeline 串行 sweep 入口，默认仍是 ADS/RFPro；显式选择 HFSS 时会通过 `tools\run_sim_filter_candidate.py` 调用 HFSS workflow：

```powershell
python tools\run_ads_filter_sweep.py `
  --backend hfss `
  --project-id bfp_6_8g_i7_fr4 `
  --pipeline-id bfp_6_8g_i7_fr4_home_parallel_round13_retest_4to10_40 `
  --profile home_simads_em_parallel `
  --hfss-profile home `
  --skip-generate `
  --hfss-build-only `
  --candidates i7_fr4_r13_retest_base_l555_taper
```

当前 round13 既有 layout JSON 是历史产物，若 layout gate 报 `layer_map.version`，应优先重新生成 layout；临时验证编排命令时可加 `--skip-layout-check`。

先只建工程，不跑仿真：

```powershell
& 'D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe' tools\hfss\run_hfss3dlayout_filter_verdict.py `
  --layout projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round13_retest_4to10_40\i7_fr4_r13_retest_base_l555_taper_layout.json `
  --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT `
  --out-dir projects\bfp_6_8g_i7_fr4\results\hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd `
  --project-name i7_fr4_r13_retest_base_l555_taper_hfss_aedt_edge_port_gnd_airbox `
  --stackup-config config\stackups\JLC04161H_7628_1P6MM.json `
  --route reliable `
  --build-only `
  --non-graphical
```

如果手动选择 HFSS 端口，建议生成无端口工程，避免自动端口把负端拉到地平面边界：

```powershell
& 'D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe' tools\hfss\run_hfss3dlayout_filter_verdict.py `
  --layout projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round13_retest_4to10_40\i7_fr4_r13_retest_base_l555_taper_layout.json `
  --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT `
  --out-dir projects\bfp_6_8g_i7_fr4\results\hfss_verdict_i7_fr4_r13_manual_ports `
  --project-name i7_fr4_r13_retest_base_l555_taper_hfss_manual_ports `
  --build-only `
  --skip-ports
```

确认层、via、端口边号后再跑 4-10 GHz、40 点裁决：

```powershell
& 'D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe' tools\hfss\run_hfss3dlayout_filter_verdict.py `
  --layout projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round13_retest_4to10_40\i7_fr4_r13_retest_base_l555_taper_layout.json `
  --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT `
  --out-dir projects\bfp_6_8g_i7_fr4\results\hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd `
  --project-name i7_fr4_r13_retest_base_l555_taper_hfss_aedt_edge_port_gnd_airbox `
  --stackup-config config\stackups\JLC04161H_7628_1P6MM.json `
  --route reliable `
  --non-graphical
```

## 裁决标准

把 HFSS 导出的 `.s2p` 与 ADS `FEM_a`、旧 RFPro 记录放到同一频点指标下比较：

- 若 HFSS 接近当前 `FEM_a`，说明差异更可能来自版图/过渡结构/端口物理，而不是 ADS 导出 bug。
- 若 HFSS 接近旧 RFPro，而远离当前 `FEM_a`，优先排查 ADS EM setup、端口校准、参考面、mesh/fitting。
- 若 HFSS、当前 `FEM_a`、旧 RFPro 三者都不一致，先固定端口形式、扫频点数和材料损耗，再做逐项 A/B。

## 最新试跑

2026-08-03 已把 HFSS 接入标准 pipeline contract 的第一阶段：

- `config/pipelines/bfp_6_8g_i7_fr4_home_parallel_round13_retest_4to10_40.json` 已登记 `simulation_backends=["ads_rfpro","hfss3dlayout"]` 和 `hfss` 配置段。
- `tools/check_pipeline_contract.py` 已能检查 HFSS workflow script、Home HFSS profile、AEDT 可执行文件、pyAEDT host Python、workspace 和 stackup_config。
- `tools/run_sim_filter_candidate.py` 已作为标准单候选薄入口，可用 `--backend ads|hfss|both` 生成或执行 ADS/HFSS 命令；第一阶段不改动稳定的 `tools/run_ads_filter_candidate.py`。
- `tools/run_ads_filter_sweep.py` 已支持显式 `--backend hfss|both|auto`，将 HFSS 后端接入串行 sweep；默认仍为 `--backend ads`，不改变旧 ADS 批量行为。
- `tools/run_ads_filter_sweep_parallel.py` 暂保持 ADS/RFPro 专用，传入 HFSS/both/auto 会拒绝并提示改用串行 sweep。
- HFSS 仍输出独立 run/artifact manifest；串行 sweep 结束时会从 run manifests 写出 `backend_summary.csv`，其中包含 `pipeline_id`。ADS/HFSS compare 保持独立 workflow，不混入 HFSS backend 主流程。
- smoke：使用 `--backend hfss --hfss-build-only --hfss-dry-run --skip-layout-check` 跑通 round13 基础候选的标准 sweep 编排，实际调用到 HFSS workflow dry-run，并确认 manifest context 中 `run_id`、`round_id`、`candidate_id`、`profile_id=home` 正确。

2026-08-03 已跑通标准 sweep 的 HFSS build-only gate：

- round13 layout 已用 `JLC04161H_7628_1P6MM` stackup 重新生成，正式目录不跳过 layout gate 可通过。
- 修复 `src/simads/hfss/layout.py`：HFSS geometry builder 现在同时接受旧 `cond` 和配置化 `signal_layer`，例如 `ETCH_TOP`。此前真实 build-only 在 `CreateEdgePort(input_feed, edge=1)` 失败，根因是 `ETCH_TOP` 信号图形未被创建。
- 工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss.aedt`
- 结果索引：`projects\bfp_6_8g_i7_fr4\results\hfss_round13_standard_backend_build\backend_summary.csv`
- 最新成功 run：`bfp_6_8g_i7_fr4_round13_i7_fr4_r13_retest_base_l555_taper_home_20260803_223950`
- 状态：`completed/setup_ready`，`geometry_count=26`，ports=`Port1/Port2`，manifest 已记录 `pipeline_id=bfp_6_8g_i7_fr4_home_parallel_round13_retest_4to10_40`。

2026-08-03 已通过标准 sweep 入口完成真实 HFSS solve：

- 命令入口：`tools\run_ads_filter_sweep.py --backend hfss`，不再使用 verdict-only 手工命令。
- 工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss.aedt`
- 结果目录：`projects\bfp_6_8g_i7_fr4\results\hfss_round13_standard_backend_solve\`
- 最新 run：`bfp_6_8g_i7_fr4_round13_i7_fr4_r13_retest_base_l555_taper_home_20260803_224339`
- 状态：`completed/scored`，elapsed `176.178s`，AEDT reported solve time 约 `2m29s`。
- 输出：S2P、trace CSV、score CSV、S 参数 SVG、run/artifact manifest、`backend_summary.csv`。
- 摘要：score=`TUNE`，`S21@5/6/7/8/9GHz=-21.67/-3.24/-4.04/-5.52/-33.34dB`，`passband_min_s21=-5.52dB`，`worst_s11/s22=-6.92/-6.88dB`。
- ADS/HFSS compare：`projects\bfp_6_8g_i7_fr4\results\compare_ads_hfss_round13_standard_backend\i7_fr4_r13_base_ads_smoke_vs_hfss_standard_summary.csv`。
- Compare 结论：S21 overall mean abs delta `6.21dB`，6-8 GHz passband mean abs delta `1.21dB`；5 GHz HFSS 比 ADS 弱约 `5.06dB`，9 GHz 差异仍很大。

2026-08-03 同一标准 HFSS backend 已完成 round13 三个候选：

| Candidate | Status | S21@5G | S21@6G | S21@8G | Passband min | Ripple | Worst S11 | Worst S22 | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `i7_fr4_r13_retest_r11b_asym3016` | TUNE | -23.48 | -3.36 | -4.92 | -4.92 | 1.62 | -5.74 | -5.89 | 通带 S21 最好，但 5GHz 阻带和回损未达目标。 |
| `i7_fr4_r13_retest_r10_asym0555` | TUNE | -22.87 | -3.29 | -5.35 | -5.35 | 2.08 | -6.09 | -6.12 | 回损刚过 -6dB，但 5GHz 阻带和 8GHz 通带未达目标。 |
| `i7_fr4_r13_retest_base_l555_taper` | TUNE | -21.67 | -3.24 | -5.52 | -5.52 | 2.27 | -6.92 | -6.88 | 回损最好，但 5GHz 阻带和 8GHz 通带最弱。 |

统一索引：`projects\bfp_6_8g_i7_fr4\results\hfss_round13_standard_backend_solve\backend_summary.csv`，ranking：`projects\bfp_6_8g_i7_fr4\results\hfss_round13_standard_backend_solve\hfss_score_ranking.csv`。

2026-08-02 用 `aedt-edge + port-edges GND` 跑通 `i7_fr4_r13_retest_base_l555_taper` 的 HFSS 3D Layout 4-10 GHz、40 点 sweep。

- 工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss_aedt_edge_port_gnd_airbox.aedt`
- 结果目录：`projects\bfp_6_8g_i7_fr4\results\hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd`
- 耗时：HFSS solve 约 `1m43s`，完整脚本约 `136.1s`
- 输出：`i7_fr4_r13_retest_base_l555_taper_hfss.s2p`、`i7_fr4_r13_retest_base_l555_taper_hfss_score.csv`、`svg\i7_fr4_r13_retest_base_l555_taper_hfss_s_curves.svg`
- SVG：S11 蓝色、S21 红色、S22 紫色；6-8 GHz 用绿色背景标出，5 GHz 用红色虚线标出，-20 dB 用红色虚线目标线标出。x 轴按数据频率范围显示，4-10 GHz 结果不会再显示 1-4 GHz 空白段。
- 摘要：score=`TUNE`，`S21@5G=-20.38dB`，`S21@6G=-4.81dB`，`S21@7G=-5.08dB`，`S21@8G=-9.64dB`，`S21@9G=-27.44dB`
- 带内：6-8 GHz 最差 `S21=-9.64dB`，通带高端 8 GHz 下垂明显。
- 回损：6-8 GHz 最差 `S11=-6.78dB`、`S22=-6.90dB`

结论：端口和 GND 范围已经按当前理解修正，结果可作为当前 HFSS 裁决口径。响应仍不是合格 6-8 GHz 带通，核心问题从回损转为 8 GHz 端插损过大；5 GHz 抑制约 20 dB，也仍偏弱。

2026-08-02 用模块化后的 `--route reliable` 和真实 JLC 层叠配置重跑同一候选，完整链路 build/solve/export/manifest 通过。

- 工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_RELIABLE_SMOKE\i7_fr4_r13_retest_base_l555_taper_jlc_hfss_reliable_4to10_40.aedt`
- 结果目录：`projects\bfp_6_8g_i7_fr4\results\hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40`
- Run manifest：`projects\bfp_6_8g_i7_fr4\runs\hfss_smoke_i7_fr4_r13_reliable_jlc_4to10_40\run_manifest.json`
- 耗时：完整脚本 `129.349s`，HFSS solve 约 `1m46s`
- 摘要：score=`TUNE`，`S21@5G=-21.67dB`，`S21@6G=-3.24dB`，`S21@7G=-4.04dB`，`S21@8G=-5.52dB`，`S21@9G=-33.34dB`
- 带内：6-8 GHz 最差 `S21=-5.52dB`，比旧简化层叠 HFSS 结果接近 ADS，但仍略低于 -5 dB 硬约束。
- 回损：6-8 GHz 最差 `S11=-6.92dB`、`S22=-6.88dB`，满足当前 -6 dB 目标。
- ADS/HFSS 对照：`projects\bfp_6_8g_i7_fr4\results\compare_ads_hfss_i7_fr4_r13_reliable_jlc\i7_fr4_r13_base_ads_vs_hfss.svg`

结论：HFSS 自动化主流程现在可以真实跑通。JLC 层叠口径下，HFSS 与 ADS 在 6-8 GHz 的 S21 差异均值约 `1.21 dB`，但 5 GHz 和 9 GHz 带外差异仍明显，后续需要继续对齐 ADS 层叠、端口属性读回和高频带外边界条件。

## 待办

- [x] 将 HFSS 从 verdict-only 文档口径推进为标准 backend 的第一阶段：pipeline contract、HFSS config、只读 gate、单候选入口。
- [x] 将 `run state machine` 从 ADS 专用 stage 泛化为 backend 通用 stage，覆盖 HFSS build/ports/setup/solve/export/score。
- [x] 在 sweep/backend summary 中记录每个 candidate 的 backend、simulator、run_id、score path 和 trace path。
- [x] 将 HFSS backend 接入串行 sweep 编排；默认仍保持 ADS/RFPro。
- [x] 重新生成 round13 layout JSON，使 `metadata.layer_map_version` 与当前 pipeline contract 对齐，再去掉 `--skip-layout-check` 跑 build-only gate。
- [x] 通过标准 sweep 入口执行真实 HFSS solve，生成 S2P/trace/score/SVG，并与 ADS/RFPro 结果对比。
- [x] 对 round13 另外两个候选执行同一标准 HFSS backend solve，并用统一 summary 排序。
- [ ] 按当前 round13 pipeline 同口径补跑 r10/r11b 的 ADS/RFPro，再生成 ADS/HFSS compare。

- [x] 安装 pyAEDT 到 `ads-automation` 虚拟环境。
- [x] 新增 HFSS 3D Layout 裁决入口。
- [x] build-only 新建 AEDT/HFSS 工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss_verdict.aedt`。
- [x] 修正端口边号策略：P1/P2 从 layout 端口坐标自动匹配馈线外侧，GND reference edge 同侧匹配。
- [x] 增加 `--skip-ports`，支持生成无端口 HFSS 工程给人工选端口。
- [x] 生成人工端口基准工程：`D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss_manual_ports.aedt`。
- [x] 当前方案：使用 AEDT 原生 `create_edge_port()` 创建 GUI 可见端口，不传 GND reference primitive，再补齐人工端口的 Gap/Vertical/Reference/Renormalize 属性。
- [x] 增加 `--gnd-boundary-mode port-edges`，让 HFSS GND 左右边界对齐 P1/P2 端口截面。
- [x] 增加默认空气盒子/HFSS model extents：`Radiation` open region，airbox horizontal `0.15`，Z 正负 `2`，工作频率 `5GHz`。
- [x] 增加保存后的 EDB 端口属性补丁：把自动 `pin-gap` 的 `ReferenceName` 和 `PEC Launch Width` 写成手工基准值。
- [x] 历史排查：生成过自动 `pin-gap`+空气盒子基准工程 `..._hfss_pin_gap_airbox_ref4.aedt`；该路线已被 pyEDB edge-gap 替代。
- [x] 改为 pyEDB `create_edge_port_on_polygon()` 生成 referenced edge gap port，匹配人工 `Port -> Create` 的 edge port 逻辑。
- [x] 修正 edge terminal 的 `DoRenormalize/DoDeembed/Renormalization Impedance` 持久化写法。
- [x] 历史排查：曾生成 `..._hfss_pyedb_gap_airbox.aedt`；由于 GUI 未显示端口，已删除该自动工程。
- [x] pyEDB `edge-gap` 在 GUI 未显示端口后，切换为 AEDT 原生 `create_edge_port()` 方法。
- [x] 实测并修正 AEDT 矩形 edge 编号映射：`top=0,left=1,bottom=2,right=3`。
- [x] 删除位置错误的自动工程，重新生成 `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\i7_fr4_r13_retest_base_l555_taper_hfss_aedt_edge_airbox.aedt`。
- [x] 读取 AEDB 验证新自动端口：Port1/Port2 与人工基准一致，均为 gap edge port，无显式 GND edge reference terminal。
- [x] 验证 port-edge GND 范围：GND bbox=`x=-3.54..7.0502mm`、`y=-1.5..7.5323mm`。
- [x] 用 `aedt-edge + port-edges GND` 路线重新跑 `i7_fr4_r13_retest_base_l555_taper` 的 HFSS 4-10 GHz 40 点裁决。
- [ ] 在 AEDT GUI 打开 `_aedt_edge_port_gnd_airbox`，确认 Port1/Port2 可见且 signal edge 位于输入左边、输出右边。
- [x] 增加 Touchstone 到 SVG 的绘图适配，让 HFSS result 自动生成 S11/S21/S22 曲线，并按数据范围显示 x 轴。
- [x] 把 HFSS/ADS/FEM_a 对比记录写入 `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`。
