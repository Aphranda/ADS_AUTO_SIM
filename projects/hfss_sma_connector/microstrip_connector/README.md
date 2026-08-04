# HFSS SMA Connector CPWG Fixture

Status: Active
Last updated: 2026-08-03

本项目是独立 HFSS 连接器仿真夹具，不并入 `bfp_6_8g_i7_fr4` 滤波器 pipeline。当前约定是一个 AEDT 工程内放多个 HFSS 3D Layout design，不为每个 fixture 新建独立 `.aedt`。

## Scope

- Stackup: `config/stackups/JLC04161H_7628_1P6MM.json`
- Signal/reference: `ETCH_TOP` over `ETCH_INNER1`
- Structure: CPWG/GCPW with top GND rails and uniform via fence beside the 50R line
- 50R CPWG line width: `0.3175 mm` (`12.5 mil`)
- CPWG ground gap: `0.2032 mm` (`8 mil`)
- SMA signal pad: `1.2 mm` wide by `4.8 mm` long
- Ideal baseline: P1-to-P2 exact `100.0 mm`
- Single-end SMA fixture: P1 SMA launch + `100.0 mm` 50R CPWG + ideal P2 port, total `106.9 mm`
- Dual-end SMA fixture: two SMA launches + `100.0 mm` 50R CPWG center section, total `113.8 mm`
- HFSS sweep: `0.5 GHz` to `10 GHz`, `96` points
- HFSS profile: `home`
- AEDT version: `2026.1`
- HFSS workspace: `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT`
- Combined AEDT project: `D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt`
- Reference SMA model: `D:\Work\ADS\HFSS_SMA_Connector\SMA_KE.aedt`

## AEDT Project

The combined AEDT project contains these designs:

| Design | Layout | Notes |
|---|---|---|
| `IDEAL_50R_CPW_100MM` | `projects/hfss_sma_connector/simulations/ideal_50r_microstrip/layouts/nominal/ideal_50r_cpw_100mm_jlc04161h_7628_1p6mm_baseline_layout.json` | Ideal 100 mm CPWG through line |
| `SINGLE_END_SMA_CPW_100MM` | `projects/hfss_sma_connector/simulations/single_end_connector_50r/layouts/nominal/single_end_connector_cpw_100mm_jlc04161h_7628_1p6mm_layout.json` | One SMA launch surrogate |
| `DUAL_END_SMA_CPW_100MM` | `projects/hfss_sma_connector/simulations/dual_end_connector_50r/layouts/nominal/dual_end_connector_cpw_100mm_jlc04161h_7628_1p6mm_layout.json` | Two SMA launch surrogates |

Build-only manifests were written for each design under `projects/hfss_sma_connector/runs/`.

## Rebuild Commands

Each command uses `project_action=add` to append or rebuild a design in the same AEDT project:

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\hfss\run_hfss3dlayout_filter_verdict.py --profile home --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT --project D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt --project-model single_aedt_project_multiple_designs --project-action add --layout projects\hfss_sma_connector\simulations\ideal_50r_microstrip\layouts\nominal\ideal_50r_cpw_100mm_jlc04161h_7628_1p6mm_baseline_layout.json --out-dir projects\hfss_sma_connector\simulations\ideal_50r_microstrip\results\nominal --design IDEAL_50R_CPW_100MM --route reliable --stackup-config config\stackups\JLC04161H_7628_1P6MM.json --start-ghz 0.5 --stop-ghz 10 --points 96 --setup Setup_0p5to10G --sweep Sweep_0p5to10G_96pt --build-only --write-manifest --project-id hfss_sma_connector --round-id ideal_50r_microstrip --device-id fixture.microstrip_50r --candidate-id ideal_50r_cpw_100mm
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\hfss\run_hfss3dlayout_filter_verdict.py --profile home --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT --project D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt --project-model single_aedt_project_multiple_designs --project-action add --layout projects\hfss_sma_connector\simulations\single_end_connector_50r\layouts\nominal\single_end_connector_cpw_100mm_jlc04161h_7628_1p6mm_layout.json --out-dir projects\hfss_sma_connector\simulations\single_end_connector_50r\results\nominal --design SINGLE_END_SMA_CPW_100MM --route reliable --stackup-config config\stackups\JLC04161H_7628_1P6MM.json --start-ghz 0.5 --stop-ghz 10 --points 96 --setup Setup_0p5to10G --sweep Sweep_0p5to10G_96pt --build-only --write-manifest --project-id hfss_sma_connector --round-id single_end_connector_50r --device-id fixture.microstrip_single_connector --candidate-id single_end_connector_cpw_100mm
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\hfss\run_hfss3dlayout_filter_verdict.py --profile home --workspace-dir D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT --project D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT\hfss_sma_connector_cpw.aedt --project-model single_aedt_project_multiple_designs --project-action add --layout projects\hfss_sma_connector\simulations\dual_end_connector_50r\layouts\nominal\dual_end_connector_cpw_100mm_jlc04161h_7628_1p6mm_layout.json --out-dir projects\hfss_sma_connector\simulations\dual_end_connector_50r\results\nominal --design DUAL_END_SMA_CPW_100MM --route reliable --stackup-config config\stackups\JLC04161H_7628_1P6MM.json --start-ghz 0.5 --stop-ghz 10 --points 96 --setup Setup_0p5to10G --sweep Sweep_0p5to10G_96pt --build-only --write-manifest --project-id hfss_sma_connector --round-id dual_end_connector_50r --device-id fixture.microstrip_connector --candidate-id dual_end_connector_cpw_100mm
```

## Next

- 在当前合并工程中先 solve `IDEAL_50R_CPW_100MM`，确认 Results 表格可见 S 参数曲线。
- 再 solve `SINGLE_END_SMA_CPW_100MM` 和 `DUAL_END_SMA_CPW_100MM`，导出 S2P/trace/score。
- 用 ideal CPWG baseline 对 single-end 和 dual-end SMA fixture 做 delta compare。
- 如果 Route A/B surrogate 失配明显，再建立首批 DoE 扫描 pad/taper/feed/clearance/via fence。
- 完整 3D SMA 模型导入仍放到 Route C，先不阻塞当前 CPWG fixture 流程。
