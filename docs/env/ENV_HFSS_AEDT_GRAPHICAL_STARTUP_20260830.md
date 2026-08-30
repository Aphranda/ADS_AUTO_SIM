# HFSS/AEDT Graphical Startup Notes

Date: 2026-08-30
Project context: `projects/RFSOC_RF/TX_Fillter.aedt`, TX_BAND1 MCFIL boardband simulation.

## Conclusion

On this machine, AEDT/HFSS 3D Layout should use the graphical backend for production runs:

```powershell
--graphical
```

The non-graphical gRPC startup path has repeatedly failed or stalled before project/design work starts. The stable path is to keep PyAEDT in graphical mode, even when the automation is otherwise unattended.

## Hidden Graphical Mode Test

The following experimental option was tested:

```powershell
--graphical --hidden-graphical
```

This keeps `non_graphical=False` so AEDT initializes the GUI backend, while setting:

```text
SIMADS_AEDT_HIDDEN_GRAPHICAL=1
ANSYS_DISABLE_DISPLAY=1
```

The intent is to get the same stable backend initialization as GUI mode while reducing visible window behavior.

Result on this Windows + AEDT 2026.1 machine:

```text
Hidden graphical did not hide the AEDT window.
AEDT still opened a visible UI while solving.
```

Therefore `--hidden-graphical` is kept only as an experimental switch. It must not be treated as the default unattended mode on this machine.

## Public Documentation Check

Checked on 2026-08-30:

- PyAEDT `Desktop.non_graphical` documentation describes only whether AEDT is running in non-graphical mode.
- PyAEDT `Hfss3dLayout` and `Hfss` constructors expose `non_graphical`, with default `False`.
- PyAEDT examples describe `non_graphical` as the choice between an interactive session and non-graphical mode.
- No official PyAEDT option was found for "graphical backend but hidden AEDT window" on Windows.

Sources checked:

```text
https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.desktop.Desktop.non_graphical.html
https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.desktop.Desktop.html
https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.hfss3dlayout.Hfss3dLayout.html
https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.hfss.Hfss.html
https://examples.aedt.docs.pyansys.com/version/dev/examples/aedt_general/report/automatic_report.html
```

Conclusion: on this machine, the reliable choices are:

- `--graphical`: stable, visible AEDT UI.
- `--non-graphical`: true headless intent, but currently unreliable for this workflow.
- `--graphical --hidden-graphical`: starts and solves, but the UI is still visible; do not rely on it for hidden operation.

## Environment Rules

- Do not keep a persistent system `HPEESOF_DIR` when ADS versions coexist.
- `apply_grpc_startup_compat()` removes `HPEESOF_DIR` by default unless `SIMADS_KEEP_HPEESOF_DIR=1`.
- Keep AEDT user/cache directories under `.simads/aedt_user` by default to avoid polluting the normal Windows user profile during automation.
- For TX_BAND1 boardband runs, use `RFSOC_RF` project defaults:
  - Start: `14 GHz`
  - Stop: `23 GHz`
  - Points: `181`
  - Sweep: `Interpolating`
  - Adaptive frequency: `18.5 GHz`

## Validated Run

The following graphical boardband run completed successfully:

```text
Candidate: tx_band1_mcfil_r5_cnn034_p2up_graphical
Design: TX_BAND1_MCFIL_R5_CNN034
Sweep: 14-23 GHz, 181 points, Interpolating
Solve time: about 1m46s
Run id: RFSOC_RF_round5_tx_band1_mcfil_r5_cnn034_p2up_graphical_home_20260830_224550
```

Important artifacts:

```text
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn034_p2up_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn034_rand28_hfss.s2p
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn034_p2up_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn034_rand28_hfss_trace.csv
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn034_p2up_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn034_p2up_graphical_tx_score.csv
projects/RFSOC_RF/runs/RFSOC_RF_round5_tx_band1_mcfil_r5_cnn034_p2up_graphical_home_20260830_224550
```

## Current Automation Policy

Use this command pattern for the next TX_BAND1 HFSS candidates:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\hfss\run_hfss3dlayout_filter_verdict.py `
  --layout <candidate_layout.json> `
  --out-dir <candidate_boardband_result_dir> `
  --project projects\RFSOC_RF\TX_Fillter.aedt `
  --project-action add `
  --project-id RFSOC_RF `
  --device-id filter.mcfil `
  --stackup-config config\stackups\ALUMINA_250UM_MCFIL_2L.json `
  --start-ghz 14 `
  --stop-ghz 23 `
  --points 181 `
  --adaptive-frequency-ghz 18.5 `
  --setup Setup_14to23G `
  --sweep Sweep_BB_14to23G_181pt `
  --sweep-type Interpolating `
  --port-type aedt-edge `
  --gnd-boundary-mode port-edges `
  --graphical `
  --write-manifest
```

## Faster Iteration Strategy

The visible AEDT GUI is still the reliable backend on this machine, but it should
not be restarted for every candidate.  The preferred production loop is now:

1. Start the first candidate with graphical AEDT and keep the session open.
2. Run later candidates with `--attach-existing --keep-open`.
3. Keep using boardband `14-23 GHz`, `181` points, `Interpolating`, adaptive
   frequency `18.5 GHz`.

The single-candidate runner supports:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\run_tx_band_mcfil_boardband_candidate.py `
  --layout <candidate_layout.json> `
  --keep-open
```

For later candidates in the same batch:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\run_tx_band_mcfil_boardband_candidate.py `
  --layout <candidate_layout.json> `
  --attach-existing `
  --keep-open
```

The batch runner automates that pattern:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\run_tx_band_mcfil_boardband_batch.py `
  --plan projects\RFSOC_RF\layouts\tx_band1_mcfil_iter\round6\tx_band1_mcfil_round6_cnn_candidate_plan.csv `
  --limit 3
```

If AEDT is already open before starting the batch, use:

```powershell
& "D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe" tools\run_tx_band_mcfil_boardband_batch.py `
  --plan projects\RFSOC_RF\layouts\tx_band1_mcfil_iter\round6\tx_band1_mcfil_round6_cnn_candidate_plan.csv `
  --attach-existing-first
```

This does not hide the GUI.  It reduces the slow part by avoiding repeated AEDT
cold starts while preserving the graphical backend that has solved reliably.

## GitHub and Documentation Survey

Checked on 2026-08-30:

- `ansys/pyaedt`: official PyAEDT package for controlling AEDT from Python.
- PyAEDT desktop session docs: PyAEDT can start a new AEDT session or connect to
  an existing one; `close_on_exit` controls whether the session is closed.
- `ansys/pyaedt-mcp`: official MCP wrapper around a persistent PyAEDT-backed
  Python session.  It can launch AEDT or connect to an existing gRPC session,
  then open projects, create designs, analyze, inspect, export, and run custom
  scripts.
- `mradway/hycohanz`: older Windows COM wrapper for HFSS.  It is useful as a
  reference for classic HFSS automation, but it is less suitable here because
  this workflow already depends on HFSS 3D Layout and PyAEDT APIs.
- AEDT command-line help documents `BatchSolve`, `RunScript`, and
  `RunScriptAndExit`.  These are valid future diagnostics for true batch mode,
  but this machine's earlier non-graphical/gRPC startup failures mean they must
  be validated separately before replacing the current graphical route.

Decision:

- Short term: use PyAEDT session reuse with `--attach-existing`.
- Medium term: consider a true in-process persistent worker or PyAEDT-MCP style
  service if command-per-candidate attach overhead is still too high.
- Experimental only: `ansysedt.exe -RunScriptAndExit` or `-BatchSolve`; test on a
  clone of the project first because solver/export behavior must match the
  existing boardband manifest and scoring flow.

## Hidden Graphical Validation Run

The following run completed, but AEDT still showed a visible window:

```text
Candidate: tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical
Design: TX_BAND1_MCFIL_R5_CNN018
Sweep: 14-23 GHz, 181 points, Interpolating
Solve time: about 1m31s
Run id: RFSOC_RF_round5_tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_home_20260830_225338
```

Important artifacts:

```text
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn018_rand12_hfss.s2p
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn018_rand12_hfss_trace.csv
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_bb_14_23g/tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_tx_score.csv
projects/RFSOC_RF/runs/RFSOC_RF_round5_tx_band1_mcfil_r5_cnn018_rand12_p2up_hidden_graphical_home_20260830_225338
```
