# TX_BAND1 MCFIL HFSS 参数化建模记录

Status: R0 geometry extraction
Source DXF: `D:\Work\ADS\TX_Band\mfg\TX_Band_lib_DA_CLFilter1_TX_BAND1\dxf\DA_CLFilter1_TX_BAND1.dxf`
HFSS project: `projects/RFSOC_RF/TX_Fillter.aedt`
HFSS result dir: `projects/RFSOC_RF/TX_Fillter.aedtresults`

## 1. 已确认的 DXF 结构

- DXF 来自 ADS MCFIL，图层为 `cond`。
- `$INSUNITS=13`，坐标单位为 micron，转 HFSS layout JSON 时使用 `0.001 mm/um`。
- `ENTITIES` 内只有 10 个闭合 `LWPOLYLINE`。
- 所有 `LWPOLYLINE` 都是 4 点轴对齐矩形。
- DXF 内未包含过孔、地层、端口或 HATCH。

## 2. 输出文件

生成命令：

```powershell
python tools/hfss/build_mcfil_dxf_hfss_layout.py
```

默认输出目录：

```text
projects/RFSOC_RF/layouts/tx_band1_mcfil
```

主要文件：

- `tx_band1_mcfil_r0_layout.json`: HFSS 3D Layout 可用的 SIMADS layout JSON。
- `tx_band1_mcfil_r0_params.json`: MCFIL 耦合段参数清单。
- `tx_band1_mcfil_r0_dxf_summary.json`: DXF 实体、单位、边界盒和矩形识别摘要。
- `tx_band1_mcfil_r0_review.svg`: 离线几何审图 SVG。

## 3. R0 几何参数摘要

整体金属边界：

```text
x: -5.738417 mm to 1.483007 mm
y: -0.347613 mm to 2.182753 mm
size: 7.221424 mm x 2.530366 mm
```

识别为 5 组 coupled-line section，每组 2 条矩形耦合线。R0 先保持 DXF 原始矩形，不重综合拓扑。

## 4. HFSS 建模策略

当前 `TX_Fillter.aedt` 是空工程，尚未发现已有 HFSS 3D Layout design。R0 推荐使用主 workflow 在该工程内追加一个 design：

```powershell
python tools/hfss/run_hfss3dlayout_filter_verdict.py `
  --layout projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json `
  --out-dir projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r0 `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --project-action add `
  --design TX_BAND1_MCFIL_R0 `
  --project-id RFSOC_RF `
  --device-id filter.mcfil `
  --candidate-id tx_band1_mcfil_r0 `
  --start-ghz 8 `
  --stop-ghz 24 `
  --points 161 `
  --adaptive-frequency-ghz 18.5 `
  --setup Setup_8to24G `
  --sweep Sweep_8to24G_161pt `
  --port-type aedt-edge `
  --gnd-boundary-mode port-edges `
  --build-only
```

先检查计划而不启动 AEDT：

```powershell
python tools/hfss/run_hfss3dlayout_filter_verdict.py `
  --layout projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json `
  --out-dir projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r0 `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --project-action add `
  --design TX_BAND1_MCFIL_R0 `
  --project-id RFSOC_RF `
  --device-id filter.mcfil `
  --candidate-id tx_band1_mcfil_r0 `
  --start-ghz 8 `
  --stop-ghz 24 `
  --points 161 `
  --adaptive-frequency-ghz 18.5 `
  --setup Setup_8to24G `
  --sweep Sweep_8to24G_161pt `
  --port-type aedt-edge `
  --gnd-boundary-mode port-edges `
  --dry-run
```

当前脚本按现有 HFSS 工具约定把右侧候选端命名为 `input_feed`，左侧候选端命名为 `output_feed`，并写入 `P1/P2` 端口元数据。因为 MCFIL 是 open-coupled-line 结构，正式仿真前需要用 ADS 原理图 pin 方向复核 P1/P2 边。

如果后续工程里已经有目标 design，再用 `replace_hfss3dlayout_layout_primitives.py` 做重画。

## 5. 参数化建模边界

R0 已参数化记录：

- 每组 section 的 `length_mm`。
- 每条 strip 的 `width_mm`、`center_y_mm`。
- 每组内的 `coupling_gaps_mm`。
- 全局 `x_offset_mm`、`y_offset_mm`、`boundary_margin_mm`。

从参数文件重建 layout：

```powershell
python tools/hfss/build_mcfil_dxf_hfss_layout.py `
  --params-in projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_params.json `
  --layout-id tx_band1_mcfil_r1
```

可直接编辑的扫描量：

- `global_parameters.x_offset_mm`
- `global_parameters.y_offset_mm`
- `coupled_sections[].tuning.length_delta_mm`
- `coupled_sections[].tuning.width_delta_mm`
- `coupled_sections[].tuning.gap_delta_mm`
- `coupled_sections[].tuning.x_delta_mm`
- `coupled_sections[].tuning.y_delta_mm`

第一轮 HFSS 参数扫描建议：

- 先固定原始 MCFIL 拓扑，只扫耦合间隙。
- 再扫每组 section 的长度，观察 17.700-19.325 GHz 通带中心和带宽偏移。
- 最后扫外侧 section 宽度和端口过渡，处理 S11/S22。

## 6. TX-F1 验收窗口

```text
Passband: 17.700-19.325 GHz
LO stopband: 14.400-15.025 GHz
Image stopband: 10.1-13.6 GHz
Sweep: 8-24 GHz
Target: IL <= 2.5 dB, RL >= 15 dB, stopband >= 40 dB, GD ripple <= 0.25 ns
```

R0 目标是确认 ADS MCFIL 版图在 HFSS 中的 EM 基线；R1 再根据 HFSS S 参数做 gap/length/port transition 参数扫描。

## 7. R0 HFSS 14-23 GHz Broadband Run

已执行自动仿真：

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools/hfss/run_hfss3dlayout_filter_verdict.py `
  --layout projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json `
  --out-dir projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_bb_14_23g `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --project-action add `
  --design TX_BAND1_MCFIL_BB_14_23G `
  --project-id RFSOC_RF `
  --device-id filter.mcfil `
  --candidate-id tx_band1_mcfil_r0 `
  --start-ghz 14 `
  --stop-ghz 23 `
  --points 181 `
  --adaptive-frequency-ghz 18.5 `
  --setup Setup_14to23G `
  --sweep Sweep_BB_14to23G_181pt `
  --sweep-type Interpolating `
  --port-type aedt-edge `
  --gnd-boundary-mode port-edges `
  --write-manifest
```

本次 layout 已将 10 个金属矩形统一设置为 `RF` net。

输出：

- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_bb_14_23g/tx_band1_mcfil_r0_hfss.s2p`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_bb_14_23g/tx_band1_mcfil_r0_hfss_trace.csv`
- `projects/RFSOC_RF/runs/RFSOC_RF_manual_tx_band1_mcfil_r0_home_20260830_201106`

按 TX-F1 窗口重算的关键结果：

| 窗口 | 频段 GHz | S21 min/max dB | S11 worst dB | S22 worst dB |
|---|---:|---:|---:|---:|
| LO stopband | 14.400-15.025 | -46.45 / -45.84 | -0.35 | -0.47 |
| TX-F1 passband | 17.700-19.325 | -43.53 / -42.13 | -0.53 | -0.44 |
| Upper sweep | 20.000-23.000 | -41.43 / -31.70 | -0.73 | -0.45 |

结论：当前 HFSS R0 不是可验收通带结果。全带 S21 过低且 S11/S22 接近 0 dB，更像端口接在 MCFIL 开路耦合端或端口/参考地定义不匹配。下一步应优先复核 ADS MCFIL 原理图 pin 对应的实体边，再考虑加入 feed extension、port launch 或按 ADS EM 端口定义重建激励。

## 8. Corrected ADS MCFIL Stackup

按 ADS Substrate Layer Stackup 截图新增：

```text
Air
cond  : PERFECT_CONDUCTOR, 18 um
Alumina: 250 um
cover : PERFECT_CONDUCTOR, 18 um
```

配置文件：

```text
config/stackups/ALUMINA_250UM_MCFIL_2L.json
```

HFSS 几何映射：

```text
signal_layer = cond
reference_ground_layer = cover
ground_plane_name = hfss_ground_plane
```

重新仿真命令：

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools/hfss/run_hfss3dlayout_filter_verdict.py `
  --layout projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json `
  --out-dir projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_bb_14_23g `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --project-action add `
  --design TX_BAND1_MCFIL_ALUMINA_BB_14_23G `
  --project-id RFSOC_RF `
  --device-id filter.mcfil `
  --candidate-id tx_band1_mcfil_r0_alumina `
  --stackup-config config/stackups/ALUMINA_250UM_MCFIL_2L.json `
  --start-ghz 14 `
  --stop-ghz 23 `
  --points 181 `
  --adaptive-frequency-ghz 18.5 `
  --setup Setup_14to23G `
  --sweep Sweep_BB_14to23G_181pt `
  --sweep-type Interpolating `
  --port-type aedt-edge `
  --gnd-boundary-mode port-edges `
  --write-manifest
```

执行结果：

```text
Design: TX_BAND1_MCFIL_ALUMINA_BB_14_23G
Run id: RFSOC_RF_manual_tx_band1_mcfil_r0_alumina_home_20260830_205732
Solve time: about 1 min 35 s
```

输出：

- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_bb_14_23g/tx_band1_mcfil_r0_hfss.s2p`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_bb_14_23g/tx_band1_mcfil_r0_hfss_trace.csv`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_bb_14_23g/svg/tx_band1_mcfil_alumina_tx_windows.svg`
- `projects/RFSOC_RF/runs/RFSOC_RF_manual_tx_band1_mcfil_r0_alumina_home_20260830_205732`

按 TX-F1 窗口重算：

| 窗口 | 频段 GHz | S21 min/max dB | S11 worst dB | S22 worst dB |
|---|---:|---:|---:|---:|
| LO stopband | 14.400-15.025 | -45.15 / -43.06 | -0.30 | -0.30 |
| TX-F1 passband | 17.700-19.325 | -16.67 / -4.86 | -5.03 | -1.11 |
| Upper sweep | 20.000-23.000 | -40.38 / -12.07 | -0.17 | -0.32 |

全扫频 S21 峰值：

```text
19.25 GHz: S21=-4.8588 dB, S11=-10.0208 dB, S22=-3.4939 dB
```

结论：Alumina 250 um 层叠后响应接近目标频段，证明层叠修正有效；但当前端口/馈线定义仍未达到验收。主要问题是 TX-F1 通带斜率过大，P2 匹配很差，20 GHz 以上滚降过快。下一步应按 ADS MCFIL 原始 pin/feed 结构补真实输入输出馈线，再做 gap/length 调参。

## 9. Manual Outer-Line Port Run

用户已在 AEDT 中手动修正端口，端口放在最外侧两根线上。本轮没有重建 layout 或端口，只对已有 design 重新求解并导出结果。

执行命令：

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools/hfss/run_existing_hfss3dlayout_verdict.py `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --design TX_BAND1_MCFIL_ALUMINA_BB_14_23G `
  --setup Setup_14to23G `
  --sweep Sweep_BB_14to23G_181pt `
  --candidate tx_band1_mcfil_alumina_manual_ports `
  --out-dir projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_manual_ports_bb_14_23g `
  --postprocess-profile filter `
  --skip-validate
```

输出：

- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_manual_ports_bb_14_23g/tx_band1_mcfil_alumina_manual_ports.s2p`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_manual_ports_bb_14_23g/tx_band1_mcfil_alumina_manual_ports_trace.csv`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_manual_ports_bb_14_23g/tx_band1_mcfil_alumina_manual_ports_tx_score.csv`
- `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_alumina_manual_ports_bb_14_23g/svg/tx_band1_mcfil_alumina_manual_ports_tx_windows.svg`

按 TX-F1 窗口重算：

| 窗口 | 频段 GHz | S21 min/max dB | S11 worst dB | S22 worst dB |
|---|---:|---:|---:|---:|
| LO stopband | 14.400-15.025 | not listed here | not listed here | not listed here |
| TX-F1 passband | 17.700-19.325 | -11.60 / -2.28 | -5.02 | -5.52 |

全扫频 S21 峰值：

```text
19.30 GHz: S21=-2.2799 dB
```

结论：手动端口修正有效，峰值插损已接近 `<=2.5 dB` 目标；但 17.7 GHz 低边仍明显不足，通带波动约 9.32 dB，S11/S22 仍未达到 15 dB return loss。下一轮微调方向应是全段略加长以压低中心频率，同时继续减小耦合间隙以抬升低边。

## 10. Parameterized Fine Tune With CNN/Score Feedback

端口确认后，以 `tx_band1_mcfil_alumina_manual_ports` 作为有效基线，生成并求解 R1 参数化候选。所有候选均作为新 design 加入 `projects/RFSOC_RF/TX_Fillter.aedt`，不覆盖手动端口基线。

新增工具：

- `tools/make_tx_band_mcfil_cnn_iteration.py`
- `src/simads/hfss/workflow.py` 增加 `--graphical`，用于在当前机器非图形 gRPC 不稳定时强制走图形 AEDT 会话。

R1/R2 HFSS 结果汇总：

| Candidate | Design | Score | Peak GHz | Peak S21 dB | Passband min/max dB | Ripple dB | Worst S11/S22 dB | LO max S21 dB | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| manual ports baseline | `TX_BAND1_MCFIL_ALUMINA_BB_14_23G` | -877.347 | 19.300 | -2.280 | -11.603 / -2.280 | 9.323 | -5.019 / -5.520 | -43.466 | Port fix valid; low edge weak |
| R1_CNN001 len +35um, gap mild | `TX_BAND1_MCFIL_R1_CNN001` | -887.082 | 19.050 | -4.381 | -11.656 / -4.381 | 7.275 | -6.627 / -1.846 | -41.226 | Worse than baseline score |
| R1_CNN002 len +55um, gap stronger | `TX_BAND1_MCFIL_R1_CNN002` | -448.779 | 18.850 | -4.167 | -7.330 / -4.167 | 3.163 | -3.885 / -1.792 | -38.474 | Current best |
| R1_CNN003 len +75um, gap strongest | `TX_BAND1_MCFIL_R1_CNN003` | -470.318 | 18.900 | -3.834 | -7.637 / -3.834 | 3.804 | -3.938 / -1.971 | -38.275 | Worse than CNN002 |
| R1_CNN004 CNN002 + outer width | `TX_BAND1_MCFIL_R1_CNN004` | -460.893 | 18.950 | -3.826 | -7.991 / -3.826 | 4.165 | -4.979 / -2.471 | -38.259 | Width probe did not improve match |
| R2_CNN002 uniform longer, gap relaxed | `TX_BAND1_MCFIL_R2_CNN002` | -612.721 | 18.700 | -4.505 | -8.739 / -4.505 | 4.234 | -3.074 / -1.196 | -38.684 | Over-shifted; high edge collapsed |

Artifacts:

- R1 feedback: `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_round1_tx_feedback.csv`
- All feedback: `projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_all_tx_feedback.csv`
- CNN checkpoint: `projects/RFSOC_RF/layouts/tx_band1_mcfil_iter/round2/tx_band1_mcfil_section_cnn.pt`
- R2 CNN plan: `projects/RFSOC_RF/layouts/tx_band1_mcfil_iter/round2/tx_band1_mcfil_round2_cnn_candidate_plan.csv`
- Per-run SVG windows are under each `projects/RFSOC_RF/hfss_runs/*/svg/` directory.

Interpretation:

- Correct-port baseline proves the model is close enough for fine tuning.
- The useful move was `R1_CNN002`: moderate length increase plus stronger coupling reduced passband ripple from 9.32 dB to 3.16 dB and lifted the weak low edge from -11.60 dB to -7.33 dB.
- `R1_CNN003` and `R2_CNN002` show that simply continuing uniform length increase is not reliable. R2 pulled the peak toward 18.7 GHz but damaged the high-frequency passband edge.
- `R1_CNN004` shows outer/feed width increase alone does not solve return loss; S22 remains the dominant match problem.

Next tuning direction:

- Keep `R1_CNN002` as the active best parent.
- Avoid further uniform lengthening.
- Use nonuniform length tuning: less added length on outer sections, slightly more on middle sections only if high-edge S21 is protected.
- Relax central coupling gap slightly to recover LO rejection, while keeping outer coupling close to CNN002 to preserve low-edge transmission.
- Add explicit feed/port transition variables in the next candidate set, because passband return loss remains poor even when S21 improves.

## 11. High-Frequency Return-Loss Weighted Loop

2026-08-31 update: 高频端回损成为主约束。评分脚本 `tools/score_tx_band_filter.py` 已提高 `18.8-19.325 GHz` 半段 S11/S22 权重，并新增：

- `worst_high_return_loss_db`
- `high_return_loss_margin_db`

当前目标口径：

```text
Passband: 17.700-19.325 GHz
High passband RL window: 18.800-19.325 GHz
Insertion loss baseline: S21 >= -3 dB
Return loss baseline: S11/S22 <= -10 dB
Boardband sweep: 14-23 GHz, 181 points, Interpolating
```

有效反馈表：

```text
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_corrected_tx_feedback.csv
```

当前有效反馈数：`73`。

当前排序重点：

| Candidate | Score | Passband min S21 dB | Worst high RL dB | High RL margin dB | Notes |
|---|---:|---:|---:|---:|---|
| `tx_band1_mcfil_r23_cnn042_rand33_p2up_graphical` | 50.278 | -5.0103 | -9.8966 | -0.1034 | 当前综合最好，已经逼近 -10 dB 高频回损 |
| `tx_band1_mcfil_r14_cnn043_rand37_p2up_graphical` | 46.625 | -5.1159 | -9.2879 | -0.7121 | 高频回损接近达标，但仍差一点 |
| `tx_band1_mcfil_r14_cnn022_rand16_p2up_graphical` | 46.438 | -5.1441 | -11.3937 | +1.3937 | 高频回损已过 -10 dB，但低边 S21 仍弱 |
| `tx_band1_mcfil_r16_cnn023_rand14_p2up_graphical` | 44.976 | -4.8469 | -8.6784 | -1.3216 | 低边插损更好，但高频回损不足 |

Interpretation:

- 这轮最好候选已经把高频回损推到 `-9 to -11.4 dB` 区间，说明端口与 boardband 口径是有效的。
- 现在瓶颈仍然是“高频回损、低边插损、通带平坦度”的三方折中。
- `R23_CNN042` 是当前主父本参考：它在高频回损接近达标的同时，保留了较好的整体分数。
- 下一轮候选应围绕 `R23_CNN042` 和 `R14_CNN022` 做局部搜索：一个偏向整体最优，一个偏向高频回损达标。

Automation updates:

- `tools/run_tx_band_mcfil_boardband_batch.py` 增加 `--timeout-minutes`，单候选超时后终止整棵子进程树并停止该批，避免 HFSS 挂起长期阻塞。
- `tools/hfss/prune_tx_band_mcfil_low_score_designs.py` 可按反馈分数清理低分 HFSS design，并支持 `--delete-design` 删除无效/未完成 design。
- `tools/run_tx_band_mcfil_long_optimization.py` 是长期滚动入口；当前重启目标设为 200 轮，生成 CNN 候选、运行 Top 子集、定期清理低分 design。
- `round51` 已生成，当前继续从 `r50_*` / `r51_*` 候选中滚动推进。
- `round52` 已生成并开始跑首批候选。
- `tools/make_tx_band_mcfil_cnn_iteration.py` 已把所有历史 `*_params.json` 纳入去重，避免未评分/超时几何在后续轮次重复生成。

HFSS project cleanup:

- 已清理 `tx_score < -100` 的历史低分 design。
- 已删除无效/超时 design：`TX_BAND1_MCFIL_R12_CNN025`、`TX_BAND1_MCFIL_R13_CNN026`。
- 工程保留基线、当前 Top 候选和少量早期对照 design；参数化模型、SVG、HFSS 输出和评分反馈保留在项目目录，HFSS 重型产物通过 `.gitignore` 排除。

Long-run command pattern:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\run_tx_band_mcfil_long_optimization.py `
  --target-count 200 `
  --batch-size 3 `
  --timeout-minutes 6 `
  --prune-every 2 `
  --keep-top-n 12
```

## 12. Current State Snapshot

2026-08-31 update:

- Target count: 200
- Current valid feedback count: 73
- Latest generated round: `round55`
- Active candidate batch: `tx_band1_mcfil_r55_cnn021_rand12_p2up_graphical` and peers
- Current state: generated layouts exist, but no `tx_score.csv` has been produced yet for the latest round
- Workspace intent: keep `HPEESOF_DIR` unset and continue boardband sweeps at `14-23 GHz`, `181 points`, `Interpolating`

2026-08-31 later update:

- Current valid feedback count: 75
- `round56` has started and the first scored candidate is `tx_band1_mcfil_r56_cnn018_rand09_p2up_graphical`
- `tx_score`: `-4.643`
- `round56` batch is still running; next candidate `tx_band1_mcfil_r56_cnn020_rand11_p2up_graphical` has started outputting files

2026-08-31 even later update:

- Current valid feedback count: 76
- `tx_band1_mcfil_r56_cnn020_rand11_p2up_graphical`
- `tx_score`: `27.490`
- `round56` is still active; `tx_band1_mcfil_r56_cnn034_rand25_p2up_graphical` has been queued next

2026-08-31 final round56 update:

- Current valid feedback count: 77
- `tx_band1_mcfil_r56_cnn034_rand25_p2up_graphical`
- `tx_score`: `-37.326`
- `round56` batch has completed its first three candidates and `round57` already exists

2026-08-31 round57 update:

- Current valid feedback count: 78
- `tx_band1_mcfil_r57_cnn016_rand07_p2up_graphical`
- `tx_score`: `26.137`
- `r57_cnn047` output directory has not produced a score yet

2026-08-31 round58 update:

- Current valid feedback count: 80
- `round58` has started
- First active candidate: `tx_band1_mcfil_r58_cnn015_rand06_p2up_graphical`
- `r58_c015` is still running; no `tx_score.csv` yet

2026-08-31 latest clean-state update:

- Current valid feedback count: 79
- Latest generated round: `round63`
- Active candidate batch: `tx_band1_mcfil_r63_cnn022_rand13_p2up_graphical`
- Workspace is now clean enough for the current iteration loop; keep `HPEESOF_DIR` unset
- Practical checkpoint for this clean-state phase: `110` feedback rows; long-run objective remains `200` total versions
- Boardband sweep remains `14-23 GHz`, `181 points`, `Interpolating`

2026-08-31 live watch update:

- `round63` is still running
- `ansysedt` PID `18312` is alive but non-responsive; `ansyscl` PID `36120` is still alive
- No `tx_score.csv` has been written yet for `tx_band1_mcfil_r63_cnn022_rand13_p2up_graphical`
- Feedback count remains `79`

2026-08-31 rolling update:

- `round64` has been generated at `2026-08-31 06:43:28`
- `round65` has been generated at `2026-08-31 06:49:35`
- No new feedback has been appended yet; current count is still `79`
- The long-run loop is still advancing generation even while the current HFSS solve has not written back

2026-08-31 latest rolling update:

- `round66` has been generated at `2026-08-31 06:58:45`
- Active candidate batch: `tx_band1_mcfil_r66_cnn043_rand34_p2up_graphical`
- No new feedback has been appended yet; current count is still `79`
- The pruning pass finished and the main loop kept rolling forward

2026-08-31 round66 score update:

- `tx_band1_mcfil_r66_cnn043_rand34_p2up_graphical` scored `4.268`
- `passband_min_s21_db`: `-5.0545`
- `worst_high_return_loss_db`: `-7.0913`
- The candidate is valid and its HFSS chain is complete
- Current valid feedback count: `80`

2026-08-31 round67 start update:

- `round67` has been generated at `2026-08-31 07:07:07`
- Active candidate batch: `tx_band1_mcfil_r67_cnn015_rand06_p2up_graphical`
- `r67_cnn015` has started but has not written `tx_score.csv` yet
- `r66_cnn026` is still pending final writeback in the same long-run chain

2026-08-31 round68 start update:

- `round68` has been generated at `2026-08-31 07:16:15`
- Active candidate batch: `tx_band1_mcfil_r68_cnn029_rand20_p2up_graphical`
- Feedback count remains `80`
- The main loop is still advancing after prune completed

2026-08-31 round69 start update:

- `round69` has been generated at `2026-08-31 07:22:24`
- Active candidate batch: `tx_band1_mcfil_r69_cnn037_rand28_p2up_graphical`
- Feedback count remains `80`
- The long-run loop is still active and moving forward

2026-08-31 round70 start update:

- `round70` has been generated at `2026-08-31 07:31:33`
- Active candidate batch: `tx_band1_mcfil_r70_cnn041_rand32_p2up_graphical`
- Feedback count remains `80`
- The long-run loop continues to advance

2026-08-31 round70 score update:

- `tx_band1_mcfil_r70_cnn041_rand32_p2up_graphical` scored `33.334`
- `passband_min_s21_db`: `-5.1659`
- `worst_high_return_loss_db`: `-8.7463`
- Current valid feedback count: `81`

2026-08-31 round71 start update:

- `round71` has been generated at `2026-08-31 07:40:41`
- Active candidate batch: `tx_band1_mcfil_r71_cnn032_rand23_p2up_graphical`
- Feedback count remains `81`

2026-08-31 round72 start update:

- `round72` has been generated at `2026-08-31 07:49:49`
- Active candidate batch: `tx_band1_mcfil_r72_cnn013_rand04_p2up_graphical`
- Feedback count remains `81`

2026-08-31 round75/76 live update:

- `round75` and `round76` are both present in the live loop
- Valid feedback count: `88`
- Latest generated round: `round76`
- Active candidate batch: `tx_band1_mcfil_r76_cnn044_rand35_p2up_graphical`
- Newly scored round76 candidate: `tx_band1_mcfil_r76_cnn045_rand36_p2up_graphical`
- `tx_score`: `-33.581`
- Current best remains `tx_band1_mcfil_r23_cnn042_rand33_p2up_graphical` at `50.278`

2026-08-31 round76/77 live update:

- Valid feedback count: `90`
- Latest generated round: `round77`
- Active candidate batch: `tx_band1_mcfil_r77_cnn019_rand10_p2up_graphical`
- Newly scored round76 candidates:
  - `tx_band1_mcfil_r76_cnn044_rand35_p2up_graphical` `tx_score = 9.226`
  - `tx_band1_mcfil_r76_cnn025_rand16_p2up_graphical` `tx_score = -5.726`
- Current best remains `tx_band1_mcfil_r23_cnn042_rand33_p2up_graphical` at `50.278`
