# SP8T Archive

Status: Active
Domain: PROJECT_ARCHIVE_FAMILY
Canonical: `archive/sp8t/README.md`
Last updated: 2026-08-09

This family archive stores frozen SP8T snapshots only.

## Layout

- `archive/sp8t/<freeze-date>/reports/`
- `archive/sp8t/<freeze-date>/baselines/`
- `archive/sp8t/<freeze-date>/results/`
- `archive/sp8t/<freeze-date>/results/<connector-best-layout>/`

## Policy

- Active iterated work remains in `projects/`.
- Frozen snapshots copy the report, baseline, or result bundle as-is.
- Source HFSS projects are not copied into the archive tree.
