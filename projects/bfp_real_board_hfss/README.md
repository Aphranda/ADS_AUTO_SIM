# BFP Real Board HFSS Optimization

This project tracks optimization of the actual BFP board layout in HFSS.

## Source

- External AEDT workspace: `D:/Work/ADS/BFP_parallel`
- AEDT project: `BFP_HFSS.aedt`
- Active designs seen in the project tree: `2.4_CON`, `BFP`, `T7_FR4_HFSS_VERDICT`
- Repository script root: `projects/bfp_real_board_hfss`

The AEDT project is external. Automation must use the HFSS/PyAEDT API path only;
do not edit `.aedt` or `.aedb` files directly.

## Current Observation

The current board-side simulation should be treated as a launch-plus-board
problem, not as an isolated BFP core problem.

The measured board batch shows a much deeper loss around 6 GHz than the current
simulation, while the 5 GHz and 9 GHz rejection are also shifted. That points to
systematic differences in connector launch, pad/via parasitics, reference plane,
and stackup/loss assumptions.

## Layout First

The first optimization step is to read the layout from the live HFSS project
through AEDT/PyAEDT APIs, then freeze that extracted layout as the editable
baseline.

Recommended extraction target:

- Source design: `BFP`
- Output root: `projects/bfp_real_board_hfss/layouts/extracted/`
- Result root: `projects/bfp_real_board_hfss/results/extracted/`

The extraction should produce layout JSON, distilled geometry, and a quick SVG
review image. Later candidates should be generated from that extracted layout,
not by hand-editing the AEDT project file.

## Extracted Baseline

Baseline manifest:

`projects/bfp_real_board_hfss/baselines/extracted_20260809/baseline_manifest.json`

Editable layout:

`projects/bfp_real_board_hfss/layouts/baseline/bfp_real_board_extracted_baseline_layout.json`

Current extracted geometry:

- Board outline: about `30.0 mm x 20.0 mm`
- TOP polygons: `22`
- Reference planes: `INNER1`, `INNER2`, `BOTTOM`
- Unique GND vias: `142`
- RF/feed polygons classified by geometry: `16`
- GND top polygons classified by geometry: `6`

First candidate register:

`projects/bfp_real_board_hfss/plans/bfp_real_board_optimization_plan.csv`

## Current Simulation

Current baseline run:

`projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/`

Current API rerun:

`projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/`

Analysis note:

`projects/bfp_real_board_hfss/reports/BFP_real_board_baseline_20260809_analysis.md`

Rerun analysis note:

`projects/bfp_real_board_hfss/reports/BFP_real_board_api_rerun_20260809_analysis.md`

Key result:

- S21 peak: `-5.92 dB @ 6.10 GHz`
- S21 at `6/7/8 GHz`: `-6.45 / -7.00 / -8.05 dB`
- Worst return in `6-8 GHz`: about `-5.06 dB`
- Early TDR low impedance: about `20-21 ohm @ 0.195 ns`

## Next Work

- Register the current best layout as the working baseline for this project.
- Separate board core, connector launch, and reference plane effects.
- Compare simulation, Smith chart, and TDR on the same port reference.
- Keep results, reports, and candidate plans under this project only.
