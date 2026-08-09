# Element-Level HFSS Layout Workflow

## Scope

The HFSS layout edit path is now element-policy driven. The generic interface selects layout primitives from extracted layout JSON, deletes matching AEDT objects through API calls, and redraws the selected primitives from the candidate layout JSON.

The BFP 7th-order interdigital filter core is one caller of this interface. Connector launches, 2.4 mm connector bodies, feed lines, ports, and global reference planes are not part of the filter-core policy unless explicitly added by config.

## Policy Contract

Policy JSON supports:

- `include.roles`, `include.names`, `include.prefixes`, `include.regions`, `include.bbox_mm`: positive element selectors.
- `include.kinds`, `include.layers`: type/layer constraints applied after positive selection.
- `exclude.roles`, `exclude.names`, `exclude.prefixes`, `exclude.kinds`, `exclude.layers`: hard exclusions.
- `draw.suppress_default_reference_ground_plane`: prevents partial redraw from creating a new full reference ground plane.

Default BFP filter policy:

`projects/bfp_real_board_hfss/config/bfp_filter_core_element_policy.json`

## Tool Usage

Dry-run selected BFP filter-core replacement:

```powershell
& 'D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe' tools\hfss\replace_hfss3dlayout_layout_primitives.py `
  --project 'D:\Work\ADS\BFP_parallel\BFP_HFSS.aedt' `
  --design BFP `
  --layout projects\bfp_real_board_hfss\layouts\baseline\bfp_real_board_extracted_baseline_layout.json `
  --scope layout-elements `
  --element-policy projects\bfp_real_board_hfss\config\bfp_filter_core_element_policy.json
```

Execute only after dry-run selected names match the intended middle filter body:

```powershell
& 'D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe' tools\hfss\replace_hfss3dlayout_layout_primitives.py `
  --project 'D:\Work\ADS\BFP_parallel\BFP_HFSS.aedt' `
  --design BFP_TEST_COPY `
  --layout projects\bfp_real_board_hfss\layouts\candidates\<candidate>_layout.json `
  --scope layout-elements `
  --element-policy projects\bfp_real_board_hfss\config\bfp_filter_core_element_policy.json `
  --execute `
  --save `
  --remove-lock
```

## Validation Gate

Before solving a candidate:

- Dry-run must list only intended filter body shapes in `selected_shape_names`.
- `requested_delete_names` must not contain connector names, feed names, port names, global ground plane names, or via names unless they are explicitly selected by policy.
- Partial candidates must carry `metadata.suppress_default_reference_ground_plane=true`.
- First write-back must target a copied/test AEDT design, not the active baseline design.
