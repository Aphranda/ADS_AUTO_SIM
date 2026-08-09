# BFP Real Board API Rerun Analysis

Status: completed
Date: 2026-08-09
Source project: `D:/Work/ADS/BFP_parallel/BFP_HFSS.aedt`
Design: `BFP`
Setup/Sweep: `Setup1` / `Sweep1`

## Artifacts

- S2P: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809.s2p`
- Trace CSV: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809_trace.csv`
- Filter score: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809_score.csv`
- Optimization metrics: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809_optimization_metrics.json`
- S-parameter plot: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/svg/BFP_real_board_api_rerun_20260809_s_curves.svg`
- Smith chart: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/svg/BFP_real_board_api_rerun_20260809_smith.svg`
- TDR CSV: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/BFP_real_board_api_rerun_20260809_tdr.csv`
- TDR plot: `projects/bfp_real_board_hfss/results/rerun/BFP_real_board_api_rerun_20260809/svg/BFP_real_board_api_rerun_20260809_tdr.svg`

## S-Parameter Markers

| Frequency | S11 dB | S21 dB | S22 dB | S11 VSWR | S22 VSWR |
|---:|---:|---:|---:|---:|---:|
| 5.0 GHz | -1.37 | -28.22 | -1.42 | 12.69 | 12.27 |
| 6.0 GHz | -8.09 | -6.45 | -7.79 | 2.30 | 2.38 |
| 6.3 GHz | -6.59 | -6.73 | -6.30 | 2.76 | 2.88 |
| 7.0 GHz | -7.31 | -7.00 | -6.49 | 2.51 | 2.80 |
| 8.0 GHz | -9.10 | -8.05 | -8.17 | 2.08 | 2.28 |
| 9.0 GHz | -7.65 | -26.78 | -5.78 | 2.42 | 3.12 |
| 10.0 GHz | -2.53 | -53.42 | -2.26 | 6.91 | 7.72 |

## Optimization Metrics

- S21 peak: `-5.92 dB @ 6.10 GHz`
- Approximate -3 dB band relative to peak: `5.6-8.3 GHz`
- 6-8 GHz S21 average/min: `-6.98 / -8.05 dB`
- 6-8 GHz S21 ripple: `2.13 dB`
- Worst 6-8 GHz return: `-5.06 dB`, from S22 near `7.20 GHz`
- S11 worst in 6-8 GHz: `-5.48 dB @ 6.45 GHz`
- 6-8 GHz group delay average: `0.828 ns`
- 6-8 GHz group delay peak-to-peak: `0.318 ns`
- Stopband S21: `-28.22 dB @ 5 GHz`, `-26.78 dB @ 9 GHz`, `-53.42 dB @ 10 GHz`

## Smith/TDR Reading

- At 6.0 GHz, the S11-derived impedance is about `63 + j46 ohm`; S22 is about `64 + j49 ohm`.
- At 6.3 GHz, both ports move to about `41 + j48 ohm`, showing strong capacitive/inductive transition rather than a clean 50 ohm feed.
- At 8.0 GHz, both ports are high-resistance with negative reactance: S11 about `76 - j38 ohm`, S22 about `86 - j43 ohm`.
- Early TDR low impedance is about `21.24 ohm` on input and `20.44 ohm` on output at `0.195 ns`.
- The later near-zero-ohm TDR point around `0.264 ns` should be treated as a relative discontinuity locator, not a literal 50 ohm line impedance.

## Optimization Direction

This rerun is numerically identical to the baseline, which means the current data is stable enough for candidate comparison. The main limitation is not a narrow single-frequency notch; the whole 6-8 GHz passband is lossy and poorly matched.

For the first optimization loop, isolate launch/feed mismatch before changing the interdigital core:

1. Sweep connector launch and feed transition geometry while keeping the filter core fixed.
2. Use S11/S22 Smith movement and early TDR low-Z change as the primary launch indicators.
3. Only after return loss improves toward at least `-10 dB`, retune interdigital gaps/lengths to recover insertion loss and edge placement.
