# Archive

Status: Active
Domain: PROJECT_ARCHIVE
Canonical: `archive/README.md`
Last updated: 2026-08-08

This root-level directory stores frozen or retired project families.

## Purpose

- Keep completed project snapshots out of active project roots.
- Preserve reproducible result/report/reference bundles for later audit.
- Avoid mixing frozen history with currently iterated simulation work.

## Layout

- One subdirectory per project family.
- One freeze tag or date directory under each family.
- No live iterative outputs here.

## SP8T Example

Planned archive target for frozen SP8T snapshots:

`archive/sp8t_real_board_hfss/`

If the SP8T board-side or connector-side work is frozen later, place the frozen
copy here and leave the active roots only for live work.

## Rule

Do not move active run outputs here while the corresponding project is still
changing.
