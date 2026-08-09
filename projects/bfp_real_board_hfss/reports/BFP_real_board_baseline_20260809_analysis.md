# BFP Real Board Baseline Simulation Analysis

Status: completed
Date: 2026-08-09
Source project: `D:/Work/ADS/BFP_parallel/BFP_HFSS.aedt`
Design: `BFP`
Setup/Sweep: `Setup1` / `Sweep1`

## Artifacts

- S2P: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/BFP_real_board_baseline_20260809.s2p`
- Trace CSV: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/BFP_real_board_baseline_20260809_trace.csv`
- Filter score: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/BFP_real_board_baseline_20260809_filter_score.csv`
- Smith chart: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/svg/BFP_real_board_baseline_20260809_smith.svg`
- TDR CSV: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/BFP_real_board_baseline_20260809_tdr.csv`
- TDR plot: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/svg/BFP_real_board_baseline_20260809_tdr.svg`
- Optimization metrics: `projects/bfp_real_board_hfss/results/baseline/BFP_real_board_baseline_20260809/BFP_real_board_baseline_20260809_optimization_metrics.json`

## S-Parameter Markers

| Frequency | S11 dB | S21 dB | S22 dB |
|---:|---:|---:|---:|
| 5.0 GHz | -1.37 | -28.22 | -1.42 |
| 6.0 GHz | -8.09 | -6.45 | -7.79 |
| 6.3 GHz | -6.59 | -6.73 | -6.30 |
| 7.0 GHz | -7.31 | -7.00 | -6.49 |
| 8.0 GHz | -9.10 | -8.05 | -8.17 |
| 9.0 GHz | -7.65 | -26.78 | -5.78 |
| 10.0 GHz | -2.53 | -53.42 | -2.26 |

## Filter Metrics

- S21 peak: `-5.92 dB @ 6.10 GHz`
- Approximate -3 dB band relative to peak: `5.6-8.3 GHz`
- 6-8 GHz S21 min: `-8.05 dB`
- 6-8 GHz S21 ripple: `2.13 dB`
- Worst S11 in 6-8 GHz: `-5.48 dB @ 6.45 GHz`
- Worst S22 in 6-8 GHz: `-5.06 dB @ 7.20 GHz`
- 5 GHz rejection: `-28.22 dB`
- 9 GHz rejection: `-26.78 dB`

## TDR Notes

- Input-side early low impedance: about `21.24 ohm @ 0.195 ns`
- Output-side early low impedance: about `20.44 ohm @ 0.195 ns`
- The later near-zero-ohm region begins around `0.264 ns`; use it as a relative localization hint, not as a literal 50-ohm transmission-line impedance.

## Optimization Reading

The current simulated board is lossy across the whole intended passband. The
main issue is not a single narrow notch: S21 is already about `-6.45 dB` at
6 GHz and degrades toward `-8.05 dB` at 8 GHz. Return loss is also weak, with
both ports only around `-5 dB` worst case in 6-8 GHz.

The Smith/TDR result points to excessive capacitive loading or a low-impedance
section near the launch/filter feed. The first optimization loop should isolate
launch discontinuity before changing the interdigital core:

1. Sweep INNER1/INNER2 relief below the two connector launches.
2. Sweep feed width/taper while keeping the core fixed.
3. Only after launch and feed impedance improve, sweep interdigital finger gaps
   to recover 6 GHz insertion loss and control 8 GHz edge loss.

Measured boards showed about `-17~-18 dB` near 6 GHz but around `-8 dB` near
6.3/8 GHz. This simulation is still optimistic at 6 GHz but close around
6.3-8 GHz, so the next comparison should focus on whether the measured 6 GHz
extra loss is caused by launch/feed mismatch, material loss, or realized core
frequency shift.

