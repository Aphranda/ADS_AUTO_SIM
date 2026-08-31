# TX_BAND1 MCFIL Server Deployment Workflow

Last updated: 2026-08-31

## Current State

- Valid feedback rows: 97
- Current best candidate: `tx_band1_mcfil_r23_cnn042_rand33_p2up_graphical`
- Current best score: `50.278`
- Best low-edge S21: `-5.0103 dB`
- Best high-frequency worst return loss: `-9.8966 dB`
- HFSS sweep: Broadband `14-23 GHz`, `181` points, `Interpolating`
- Port convention:
  - `P1`: right lower outer strip
  - `P2`: left upper outer strip

The recent extra feedback from `round80` to `round84` improved training coverage but did not replace the current best. `round84_cnn032_rand23` reached `39.258`, useful as feedback but still below `r23_cnn042`.

## Repository Inputs

Minimum tracked source needed to recreate candidates on another machine:

- `projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_params.json`
- `projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json`
- `projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_dxf_summary.json`
- `projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_review.svg`
- `config/stackups/ALUMINA_250UM_MCFIL_2L.json`
- `tools/make_tx_band_mcfil_cnn_iteration.py`
- `tools/run_tx_band_mcfil_boardband_candidate.py`
- `tools/run_tx_band_mcfil_boardband_batch.py`
- `tools/run_tx_band_mcfil_long_optimization.py`
- `tools/score_tx_band_filter.py`
- `tools/hfss/run_hfss3dlayout_filter_verdict.py`

The full historical `layouts/tx_band1_mcfil_iter/round*` tree is not required on the server if the server will generate new candidates from the seed model and feedback CSV.

## Server Environment

Use a Windows server with Ansys Electronics Desktop / HFSS installed and licensed. Current local validation used AEDT 2026 R1 with PyAEDT `1.3.0`.

Recommended Python setup:

```powershell
cd D:\Work\SIM\ADS_AUTO_SIM
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[hfss,nn,reports]"
$env:ADS_AUTOMATION_PYTHON = "D:\Work\SIM\ADS_AUTO_SIM\.venv\Scripts\python.exe"
```

Keep `HPEESOF_DIR` unset for ADS multi-version coexistence unless a wrapper script sets it only for one process.

## Feedback Data

The CNN loop is driven by:

```text
projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_corrected_tx_feedback.csv
```

To continue from the current training state on the server, this CSV must be copied or pushed before deployment. Heavy per-candidate result folders under `projects/RFSOC_RF/hfss_runs/*_bb_14_23g/` should stay local to the machine that generated them.

## Single Candidate Smoke Test

After cloning and installing dependencies, first run one known layout to validate AEDT, stackup, ports, sweep, Touchstone export, scoring, and feedback append.

```powershell
$env:ADS_AUTOMATION_PYTHON = "D:\Work\SIM\ADS_AUTO_SIM\.venv\Scripts\python.exe"

& $env:ADS_AUTOMATION_PYTHON tools/run_tx_band_mcfil_boardband_candidate.py `
  --layout projects/RFSOC_RF/layouts/tx_band1_mcfil/tx_band1_mcfil_r0_layout.json `
  --project projects/RFSOC_RF/TX_Fillter.aedt `
  --start-ghz 14 `
  --stop-ghz 23 `
  --points 181 `
  --sweep-type Interpolating `
  --graphical `
  --keep-open
```

Expected artifacts:

- `*.s2p`
- `*_hfss_trace.csv`
- `*_hfss_score.csv`
- `*_tx_score.csv`
- appended row in `tx_band1_mcfil_corrected_tx_feedback.csv`

## Rolling CNN/HFSS Loop

Run the long loop after the smoke test passes:

```powershell
$env:ADS_AUTOMATION_PYTHON = "D:\Work\SIM\ADS_AUTO_SIM\.venv\Scripts\python.exe"

& $env:ADS_AUTOMATION_PYTHON tools/run_tx_band_mcfil_long_optimization.py `
  --target-count 200 `
  --batch-size 3 `
  --top-k 12 `
  --build-top-k 6 `
  --epochs 1600 `
  --timeout-minutes 20 `
  --max-rounds 50 `
  --attach-existing-first `
  --prune-every 2 `
  --prune-score-below -100 `
  --keep-top-n 12
```

Operational notes:

- Use graphical AEDT with `--attach-existing-first` for the most stable automation path.
- Current non-graphical AEDT startup was unreliable for this workflow.
- Broadband setup is created as `Setup_14to23G` / `Sweep_BB_14to23G_181pt`.
- A normal successful candidate solves in roughly 1.5 minutes locally; some candidates can stall and should rely on `--timeout-minutes`.
- Avoid running multiple HFSS jobs against the same AEDT project at the same time.

## Candidate Generation Flow

Each round does the following:

1. Read `tx_band1_mcfil_corrected_tx_feedback.csv`.
2. Match feedback candidates back to existing `*_params.json`.
3. Train `TxBandMcfilSectionCnn`.
4. Generate local perturbations around the current best parent.
5. Penalize duplicate tuning signatures.
6. Build the top layouts and SVG reviews.
7. Run HFSS Broadband for selected layouts.
8. Score S-parameters and append feedback.

The current generator includes extra logic for weak low-edge passband S21:

- detect `pass_low_s21_db` weaker than high-edge S21
- reduce selected coupling gaps to increase low-edge coupling
- keep high-frequency return loss in the scoring feedback loop

## Scoring Targets

Baseline acceptance target:

- Insertion loss: about `-3 dB`
- Return loss: below `-10 dB`
- High-frequency return loss is important and should be included in ranking, not only center passband S21.

Current best is close on high-frequency return loss but still weak on insertion loss:

```text
candidate: tx_band1_mcfil_r23_cnn042_rand33_p2up_graphical
tx_score: 50.278
pass_low_s21_db: -5.0103
pass_high_s21_db: -2.4285
worst_high_return_loss_db: -9.8966
peak_freq_ghz: 19.1500
```

## Cleanup Policy

To prevent AEDT projects from growing without bound:

- Keep top scoring designs and recent active designs.
- Prune clearly low scoring HFSS designs from the AEDT project.
- Do not commit `TX_Fillter.aedt`, `.aedb`, `.aedtresults`, `runs/`, or heavy `hfss_runs/*_bb_14_23g/` folders.
- Keep reproducible source artifacts in Git: scripts, stackup config, seed params/layout/SVG, and feedback CSV when a new training checkpoint should be shared.

Use pruning only when no HFSS solve is active:

```powershell
& $env:ADS_AUTOMATION_PYTHON tools/hfss/prune_tx_band_mcfil_low_score_designs.py `
  --score-below -100 `
  --keep-top-n 12 `
  --execute `
  --save `
  --graphical `
  --attach-existing `
  --keep-open
```

## Monitoring

Check current training size and best candidate:

```powershell
$csv = "projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_corrected_tx_feedback.csv"
$rows = @(Import-Csv -LiteralPath $csv -Encoding UTF8)
"FEEDBACK_ROWS=$($rows.Count)"
$rows | Sort-Object {[double]$_.tx_score} -Descending |
  Select-Object -First 10 candidate,tx_score,pass_low_s21_db,pass_high_s21_db,worst_high_return_loss_db,peak_freq_ghz
```

Check active AEDT and automation processes:

```powershell
Get-Process -Name ansysedt -ErrorAction SilentlyContinue |
  Select-Object Name,Id,CPU,Responding,MainWindowTitle

Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match "run_tx_band_mcfil|run_hfss3dlayout_filter_verdict" } |
  Select-Object ProcessId,ParentProcessId,Name,CommandLine
```

## Git Handoff

Before server deployment:

```powershell
git status --short --branch
git pull --ff-only
git push origin main
```

If the server should continue from the latest local 97-row dataset, include:

```powershell
git add projects/RFSOC_RF/hfss_runs/tx_band1_mcfil_corrected_tx_feedback.csv
git commit -m "Update TX MCFIL feedback dataset"
git push origin main
```

Do not add heavy generated result directories unless a specific result must be archived for review.
