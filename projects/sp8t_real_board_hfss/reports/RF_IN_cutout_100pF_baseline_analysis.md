# RF_IN_cutout 100pF Baseline Analysis

Date: 2026-08-06

## Scope

This note records the corrected `100pF` AC coupling baseline for the imported
real SP8T RF_IN cutout HFSS design.

Primary artifacts:

- S2P: `projects/sp8t_real_board_hfss/results/baselines/RF_IN_cutout_100pF/RF_IN_cutout_100pF.s2p`
- Score: `projects/sp8t_real_board_hfss/results/baselines/RF_IN_cutout_100pF/RF_IN_cutout_100pF_score.csv`
- Smith chart: `projects/sp8t_real_board_hfss/results/baselines/RF_IN_cutout_100pF/svg/RF_IN_cutout_100pF_smith.svg`
- TDR: `projects/sp8t_real_board_hfss/results/baselines/RF_IN_cutout_100pF/RF_IN_cutout_100pF_tdr.csv`

## S-Parameter Evidence

- Worst return is `S11 = -13.50 dB @ 3.55 GHz`.
- Worst insertion loss is `S21 = -1.38 dB @ 3.55 GHz`.
- At `3.55 GHz`, `S22 = -33.90 dB`, so the main resonance signature is input-side dominant.
- At `8 GHz`, `S11 = -18.77 dB`, `S21 = -0.74 dB`, `S22 = -17.35 dB`; this is not the primary defect after correcting the AC coupling value.

## Smith Evidence

At `3.55 GHz`, S11 maps to normalized input impedance about:

`Zin/Z0 = 0.652 + j0.030`

For `Z0 = 50 ohm`, this is approximately:

`Zin = 32.6 + j1.5 ohm`

This is a low-resistance launch mismatch near resonance, not a simple
high-frequency series-inductance-only problem. Geometry review should focus on
the RF_IN launch discontinuity and local return path around the input side.

## TDR Evidence

The Touchstone-derived TDR is band-limited from `0.5-10 GHz`, so it is a
diagnostic curve rather than a calibrated absolute-distance measurement.

- Input-side minimum: about `41.47 ohm @ 0.078 ns`.
- Output-side minimum: about `41.53 ohm @ 0.137 ns`.

The early low-impedance dip is consistent with excessive local capacitance or a
low-impedance launch discontinuity near the RF_IN side.

## Next Checks

1. Use AEDT/PyAEDT API to extract RF_IN cutout layout primitives and layer/net
   context without editing `.aedt` or `.aedb` files directly.
2. Correlate the early TDR low-impedance dip with connector pad, AC coupling
   component landing, L2/L3/L4 reference plane geometry, and via/feet return.
3. Generate the first candidate only after geometry extraction identifies which
   physical discontinuity maps to the 3.55 GHz event.
