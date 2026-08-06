# SP8T Real Board HFSS TODO

- [x] Register standalone project `sp8t_real_board_hfss`.
- [x] Archive invalid `100nF` `RF_IN_cutout` baseline.
- [x] Freeze corrected `100pF` `RF_IN_cutout` baseline with S-parameter, Smith, and TDR artifacts.
- [x] Add Touchstone-derived TDR output to connector HFSS post-processing.
- [x] Extract `RF_IN_cutout` layout geometry through AEDT/PyAEDT APIs and render focused/full-extent SVG layout reviews.
- [ ] Analyze the remaining 3.55 GHz resonance using S-parameters, Smith chart, and TDR together.
- [ ] Derive editable launch/cutout parameters from the extracted JSON/SVG before generating the first candidate layout.
- [ ] Add API command to clone `RF_IN_cutout` into candidate designs.
- [ ] Add API-safe candidate runner that writes under `projects/sp8t_real_board_hfss/results/rf_in_cutout/<candidate_id>/`.
- [ ] Build first L2/L3 relief candidate from Smith chart diagnosis.
- [ ] Compare baseline vs candidates with S-curve, Smith chart, and TDR pages.
