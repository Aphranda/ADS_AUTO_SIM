# 6-8 GHz Interdigital Filter ADS Automation Workflow

This flow keeps ADS as the EM solver. Python handles candidate generation,
DXF import, port placement, FEM setup cloning, RFPro/FEM execution, and scoring.

ADS workspace:

```text
D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
```

ADS Python:

```text
D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

## 1. Generate Candidate Layouts

Edit:

```text
SIM/ADS/filter_sweep_plan.csv
```

Then run:

```powershell
python SIM/tools/generate_filter_sweep.py
```

Use the generated `*_mm_coords.dxf` files. Import unit is `mm`; do not use
mil for these files.

## 2. One-Command Candidate Run

Recommended command for one candidate:

```powershell
python SIM/tools/run_ads_filter_candidate.py `
  interdigital_9o_ro4350b_508um_v4_more_coupling `
  --overwrite-setup
```

This runs:

```text
DXF import + P1/P2 pins
clone/patched V3 FEM setup
RFPro/FEM simulation
CSV result scoring
```

Use these switches while debugging:

```text
--dry-run        print commands only
--prepare-only   create/update RFPro view but do not start FEM
--skip-fem       stop after import/setup
--skip-import    reuse an existing imported layout cell
--reuse-layout   skip import/pin placement entirely for an existing layout cell
--skip-setup     reuse an existing emSetup/em%Setup
```

Default result files:

```text
SIM/ADS/results/<cell>_rfpro.csv
SIM/ADS/results/<cell>_score.csv
```

## 3. Import DXF And Add Pins

Example for V4:

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" `
  SIM/tools/ads_import_dxf_add_ports.py `
  --dxf SIM/ADS/sweep/interdigital_9o_ro4350b_508um_v4_more_coupling_mm_coords.dxf `
  --params SIM/ADS/sweep/interdigital_9o_ro4350b_508um_v4_more_coupling_params.json
```

Defaults:

```text
workspace  = D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
library    = 6-8G_Fillter_lib
layer map  = D:\Work\ADS\6-8G_Fillter\6-8G_Fillter\setup_dxf.opt
cell       = DXF stem
```

The script places:

```text
P1 = input feed left edge center
P2 = output feed right edge center
```

For the current generator this is:

```text
P1 = (-feed_len_mm, tap_from_bottom_mm)
P2 = (field_width_mm + feed_len_mm, tap_from_bottom_mm)
```

In ADS 2026 Update 1 command-line automation, the DXF translator AEL words may
not be exposed. The importer now falls back to the generated DXF subset used
here:

```text
SOLID  -> layout rectangle/polygon
CIRCLE -> circular via on pcvia1
LINE   -> EM_BOUNDARY line
```

## 4. Clone FEM Setup From V3

The current known-good template is:

```text
interdigital_9o_ro4350b_508um_v3_wide_mm_coords:emSetup
```

Clone it to a new imported cell:

```powershell
python SIM/tools/ads_clone_emsetup_template.py `
  --target-cell interdigital_9o_ro4350b_508um_v4_more_coupling_mm_coords `
  --params SIM/ADS/sweep/interdigital_9o_ro4350b_508um_v4_more_coupling_params.json `
  --overwrite
```

This patches:

```text
topLibCellView
dataset/display cell names
cosim intermediate cell name
P1/P2 snapshot coordinates
frequency plan: 4-10 GHz, 50 (max)
```

## 5. Run RFPro/FEM

Prepare RFPro view and start FEM:

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" `
  SIM/tools/ads_run_rfpro_fem.py `
  --cell interdigital_9o_ro4350b_508um_v4_more_coupling_mm_coords `
  --out SIM/ADS/results/interdigital_9o_ro4350b_508um_v4_more_coupling_rfpro.csv
```

Defaults:

```text
emsetup view = emSetup
rfpro view   = rfpro
solver preset = FEM
frequency plan = Adaptive, 4 GHz to 10 GHz, 50 points
max adaptive passes = 15
field storage = disabled
```

Use `--prepare-only` to stop after creating/updating the RFPro view.

## 6. Score Results

For RFPro CSV:

```powershell
python SIM/tools/analyze_ads_dataset.py `
  SIM/ADS/results/interdigital_9o_ro4350b_508um_v4_more_coupling_rfpro.csv
```

For ADS `.ds` files:

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" `
  SIM/tools/analyze_ads_dataset.py `
  "D:\Work\ADS\6-8G_Fillter\6-8G_Fillter\data\interdigital_9o_ro4350b_508um_v3_wide_mm_coords_FEM.ds" `
  --inspect
```

Scoring targets:

```text
S21 @ 5 GHz <= -45 dB, preferably <= -50 dB
S21 @ 6 GHz >= -3 dB
S21 @ 8 GHz >= -3 dB
Passband 6-8 GHz minimum S21 >= -3.5 dB
Passband ripple <= 3 dB
Worst S11/S22 in 6-8 GHz <= -10 dB, preferably <= -12 dB
```

## 7. Iterate

Batch closed-loop command:

```powershell
python SIM/tools/run_ads_filter_sweep.py
```

Run only one candidate:

```powershell
python SIM/tools/run_ads_filter_sweep.py `
  --candidates interdigital_9o_ro4350b_508um_v4_more_coupling `
  --skip-generate
```

The sweep driver:

```text
generates DXF/JSON from SIM/ADS/filter_sweep_plan.csv
runs import/layout reuse, FEM setup clone, RFPro/FEM, and scoring
writes SIM/ADS/results/sweep_summary.csv
```

Use unique candidate names when changing geometry. If a cell already exists,
the sweep driver reuses the layout by default to avoid duplicate port creation.
Use `--force-import-existing` only when the existing ADS cell is intentionally
disposable.

Recommended near-term sweep around V3/V4:

```text
First tune tap for S11/S22.
Then tune S1/S8 for 5 GHz rejection and edge match.
Then tune S3/S6 and S4/S5 for passband width/ripple.
Use L only to shift the whole response in frequency.
```

For this filter, do not accept a candidate with only 30 dB rejection at 5 GHz.
Use 45 dB as the minimum numeric target and 50 dB as the practical design goal.

Current V4 FEM result from the closed loop:

```text
status: TUNE
S21 @ 5 GHz: -37.28 dB
S21 @ 6 GHz: -3.13 dB
S21 @ 8 GHz: -4.06 dB
passband min S21: -4.06 dB
passband ripple: 2.87 dB
worst S11/S22 in 6-8 GHz: -3.93 / -4.00 dB
```
