# SP8T Real Board HFSS Optimization

This project tracks optimization of the imported real SP8T board HFSS layout.

## Source

- HFSS project: `F:/1.Hardware/HFSS/SP8T/SP8T_HFSS.aedt`
- Active design: `RF_IN_cutout`
- Setup/Sweep: `Setup1` / `Sweep1`
- Ports: `Port1`, `S1_1_Pin_T1`
- Frequency: 0.5-10 GHz, 0.05 GHz step

The external AEDT project is not copied into the repository. Automation must use
PyAEDT/AEDT APIs; do not edit `.aedt` or `.aedb` files directly.

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
  --project "F:\1.Hardware\HFSS\SP8T\SP8T_HFSS.aedt" `
  --design RF_IN_cutout `
  --setup Setup1 `
  --sweep Sweep1 `
  --candidate RF_IN_cutout `
  --out-dir projects\sp8t_real_board_hfss\results\rf_in_cutout\RF_IN_cutout `
  --output .simads\sp8t\RF_IN_cutout_run.json `
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
