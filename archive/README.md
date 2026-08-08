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

## SP8T Family

Frozen SP8T snapshots live under:

`archive/sp8t/`

Active SP8T work stays in `projects/`. Only frozen report, baseline, and
reference snapshots move into the archive tree.

## Rule

Do not move active run outputs here while the corresponding project is still
changing.
