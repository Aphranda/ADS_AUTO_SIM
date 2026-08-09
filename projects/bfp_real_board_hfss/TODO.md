# TODO

- [x] Extract the live `BFP` layout from `BFP_HFSS.aedt` through AEDT/PyAEDT API.
- [x] Freeze the extracted layout as the first editable baseline for this project.
- [x] Create the first candidate register for actual-board layout optimization.
- [x] Create an API-only run entry for the current BFP_HFSS design.
- [x] Export baseline S2P, Smith chart, TDR, and filter optimization metrics.
- [x] Rerun the actual-board BFP design and export S2P, Smith, TDR, group delay, and optimization metrics.
- [x] Compare measured VNA marker data against the BFP real-board HFSS rerun.
- [x] Add a generic element-level delete/redraw policy interface for partial HFSS layout edits.
- [ ] Create an independent 5.5-7.5 GHz shifted-band baseline for BFP and compare it against the current baseline.
- [ ] Verify editable baseline write-back in a copied/test AEDT design.
- [ ] Add a BFP-specific two-port source-layout rebuild workflow.
- [ ] Rebase optimization on the 7th-order interdigital filter layout through the generic element policy interface.
- [ ] Generate 7th-order interdigital 6G S11 tuning candidates.
- [ ] Simulate the 7th-order interdigital candidates and compare against the current baseline.
- [ ] Add a simulation-vs-measured comparison report for the same board batch.
- [ ] Parameterize the launch / connector / pad / via region for optimization.
- [ ] Add a validation step for port reference and connectivity before every run.
