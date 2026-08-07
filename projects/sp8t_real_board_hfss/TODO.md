# SP8T Real Board HFSS TODO

- [x] Register standalone project `sp8t_real_board_hfss`.
- [x] Archive invalid `100nF` `RF_IN_cutout` baseline.
- [x] Freeze corrected `100pF` `RF_IN_cutout` baseline with S-parameter, Smith, and TDR artifacts.
- [x] Add Touchstone-derived TDR output to connector HFSS post-processing.
- [x] Extract `RF_IN_cutout` layout geometry through AEDT/PyAEDT APIs and render focused/full-extent SVG layout reviews.
- [x] Add SP8T four-port Touchstone scoring with input/output isolation metrics.
- [x] Re-run `RF-PPA-SP10T-4F4H-ENIG-V1.0_cutout` in home AEDT and update the connector report with the isolation score page.
- [ ] Analyze the remaining 3.55 GHz resonance using S-parameters, Smith chart, and TDR together.
- [ ] Analyze the four-port `S43` high-frequency insertion-loss dip and through ripple; isolation is not the current bottleneck.
- [ ] Derive editable launch/cutout parameters from the extracted JSON/SVG before generating the first candidate layout.
- [ ] Add API command to clone `RF_IN_cutout` into candidate designs.
- [ ] Add API-safe candidate runner that writes under `projects/sp8t_real_board_hfss/results/rf_in_cutout/<candidate_id>/`.
- [ ] Build first L2/L3 relief candidate from Smith chart diagnosis.
- [ ] Compare baseline vs candidates with S-curve, Smith chart, and TDR pages.
