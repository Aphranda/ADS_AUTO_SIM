# BFP Measured Curve Fit 001

Status: completed
Date: 2026-08-09

## Reference Image

The clearest screenshot for visual review is the second one. The batch fit
below uses the manually read markers from all four screenshots.

## Inputs

- Measured markers: `projects/bfp_real_board_hfss/measurements/bfp_batch_s21_markers_20260807.csv`
- HFSS real-board rerun S2P:
  `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809.s2p`

## Fit Outputs

- Dense curve CSV: `projects/bfp_real_board_hfss/results/measurement_fit/bfp_batch_20260807_fit/bfp_batch_s21_markers_20260807_fit.csv`
- Fit vs sim CSV: `projects/bfp_real_board_hfss/results/measurement_fit/bfp_batch_20260807_fit/bfp_batch_s21_markers_20260807_fit_vs_sim.csv`
- Fit SVG: `projects/bfp_real_board_hfss/results/measurement_fit/bfp_batch_20260807_fit/bfp_batch_s21_markers_20260807_fit.svg`

## Summary

- Interpolator: PCHIP when SciPy is available
- Marker frequencies used: `5.0 / 6.0 / 6.3 / 8.0 / 9.0 GHz`
- Board spread at markers is small, so the four screenshots represent a stable batch
- Fit vs HFSS marker RMS error: `10.34 dB`
- Mean absolute error: `7.53 dB`
- Max absolute error: `20.36 dB`

## Reading

The fitted measurement curve confirms the earlier marker-based conclusion:

- The HFSS model is close around `6.3 GHz` and `8 GHz`
- The model is too optimistic around `6 GHz`
- Measured `5 GHz` and `9 GHz` rejection are much stronger than the simulation

The clearest next-step comparison is therefore not a generic full-curve match,
but a low-edge calibration of the filter core while keeping the `6.3-8 GHz`
region stable.
