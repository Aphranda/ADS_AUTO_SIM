# SP8T Real Board HFSS Optimization

This project tracks optimization of the imported real SP8T board HFSS layout.

## Source

- HFSS project: `D:/Work/ADS/SP8T/SP8T_HFSS.aedt`
- Script management path: `projects/sp8t_real_board_hfss`
- Active input launch design: `ppa_rf_cutout_RF_IN`
- Output launch example design: `ppa_rf_cutout_RF_OUT`
- Frozen legacy baseline design: `RF_IN_cutout`
- Setup/Sweep: `Setup1` / `Sweep1`
- Ports: `Port1`, `S1_1_Pin_T1`
- Frequency: 0.5-10 GHz, 0.05 GHz step

The external AEDT project is not copied into the repository. Automation must use
PyAEDT/AEDT APIs; do not edit `.aedt` or `.aedb` files directly.

## Layout Lifecycle Note

When a board outline is clipped/cropped, the clipping frame is a temporary
source-layout object and must be included in the delete lifecycle before the
next layout is written. If the frame remains in HFSS/EDB, it can overlap the
real PCB layout, participate in solving, and create misleading port,
connectivity, resonance, or S-parameter problems.

Treat this first as a layout lifecycle issue, not as evidence that the
connector face excitation is disconnected from PCB copper. The connector pin
and solder launch can bridge the physical distance from the connector reference
face to the PCB pad.

The standard cleanup flow removes common `clip/cut/crop frame` names by default.
If a manually created frame uses another name, pass it explicitly through
`--delete-extra-name` or `--delete-extra-prefix` in the layout delete/replace
tool.

## Baseline

Baseline artifacts are frozen under:

`projects/sp8t_real_board_hfss/results/baselines/RF_IN_cutout/`

Current baseline summary:

- Status: `TUNE`
- Connector score: `32.188`
- S21 min 0.5-10G: `-1.46 dB`
- S21 avg 0.5-10G: `-0.45 dB`
- S21 ripple 0.5-10G: `1.41 dB`
- Worst return: `S11 = -11.46 dB @ 3.55 GHz`
- 8 GHz: `S11=-21.01 dB`, `S21=-0.53 dB`, `S22=-23.59 dB`
- Smith hint: `reduce_series_inductance_or_recover_local_capacitance`

## Run Command

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\hfss\run_existing_hfss3dlayout_verdict.py `
  --project "D:\Work\ADS\SP8T\SP8T_HFSS.aedt" `
  --design ppa_rf_cutout_RF_IN `
  --setup Setup1 `
  --sweep Sweep1 `
  --candidate ppa_rf_cutout_RF_IN `
  --out-dir projects\sp8t_real_board_hfss\results\rf_in_launch\ppa_rf_cutout_RF_IN `
  --output .simads\sp8t\ppa_rf_cutout_RF_IN_run.json `
  --postprocess-profile connector
```

## Optimization Direction

Use `projects/sp8t_real_board_hfss/plans/rf_in_cutout_optimization_plan.csv`
as the candidate register. New candidates should write to
`projects/sp8t_real_board_hfss/results/rf_in_cutout/<candidate_id>/`.

Primary first-pass knobs:

- L2/L3 RF_IN launch relief shape and length.
- Local microstrip compensation to pull the launch trajectory toward 50 ohm on the Smith chart.
- Ground/via continuity near connector feet, while avoiding excessive complete GND plane under the launch pad.
