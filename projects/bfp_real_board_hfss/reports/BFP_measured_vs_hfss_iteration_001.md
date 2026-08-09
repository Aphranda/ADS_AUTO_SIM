# BFP Measured vs HFSS Iteration 001

Status: analysis complete; geometry iteration gated by BFP write-back validation
Date: 2026-08-09

## Inputs

- Measured markers: `projects/bfp_real_board_hfss/measurements/bfp_batch_s21_markers_20260807.csv`
- HFSS simulation metrics: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809_optimization_metrics.json`
- Comparison CSV: `projects/bfp_real_board_hfss/results/measurement_compare/BFP_real_board_api_rerun_20260809_vs_measured_batch.csv`
- Comparison JSON: `projects/bfp_real_board_hfss/results/measurement_compare/BFP_real_board_api_rerun_20260809_vs_measured_batch.json`

The measured values were read manually from four VNA screenshots in
`projects/bfp_6_8g_i7_fr4/docs/实测值*.jpg`.

## Comparison

| Frequency | Measured S21 mean | Measured std | HFSS S21 | HFSS - measured |
|---:|---:|---:|---:|---:|
| 5.0 GHz | -40.48 dB | 0.27 dB | -28.22 dB | +12.26 dB |
| 6.0 GHz | -17.92 dB | 0.49 dB | -6.45 dB | +11.46 dB |
| 6.3 GHz | -8.74 dB | 0.14 dB | -6.73 dB | +2.02 dB |
| 8.0 GHz | -8.23 dB | 0.37 dB | -8.05 dB | +0.17 dB |
| 9.0 GHz | -46.01 dB | 0.20 dB | -26.78 dB | +19.23 dB |

## Reading

The four measured boards are consistent; the largest marker spread is only
about `0.49 dB` at 6 GHz. The discrepancy is therefore systematic, not a
single-board assembly outlier.

The HFSS model is close to the measured board at 6.3 GHz and 8 GHz, but is much
too optimistic at 6 GHz. At the same time, measured 5 GHz and 9 GHz rejection is
much stronger than HFSS. This points to a sharper and higher actual low-side
transition than the simulation predicts. A pure launch-loss or material-loss
correction is not enough, because that would degrade the whole passband rather
than mainly the 6 GHz edge.

The current HFSS return loss is still poor, around `-5 dB` worst case in
6-8 GHz, so launch/feed matching is real work. However, matching alone is not
the first-order explanation for the measured-vs-simulated 6 GHz gap.

## Optimization Direction

R1 should prioritize the filter core low-frequency edge while preserving the
already-good 6.3-8 GHz fit:

1. Add a BFP-specific two-port layout write-back workflow that rebuilds the
   extracted board layout in a copied/test AEDT design before touching `BFP`.
2. Sweep core coupling/edge geometry first: close selected resonator gaps or
   increase end coupling enough to improve 6 GHz, while watching 5 GHz rejection.
3. Run a small resonator-length sensitivity after coupling: lengthening fingers
   can pull the band down, but it may also move 8 GHz/9 GHz in the wrong
   direction.
4. After the core is calibrated against measured 6/6.3/8/9 GHz markers, return
   to launch/feed matching to improve S11/S22 and TDR without using it to mask
   a core frequency error.

## R1 Gate

Do not directly reuse `replace_hfss3dlayout_layout_primitives.py` on active
`BFP`: it currently assumes the connector single-ended fixture and recreates
only a PCB output edge port. The BFP real-board flow needs its own two-port
source-layout rebuild policy and a copied/test design validation step.
