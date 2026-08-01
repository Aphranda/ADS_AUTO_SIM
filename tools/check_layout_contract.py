#!/usr/bin/env python3
"""Validate generated layout JSON files against a standard pipeline contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_pipeline, load_project, resolve_pipeline_id
from simads.geometry import load_layout_json, validate_layout_contract, validate_pixel_qr_bpf_layout


def repo_root() -> Path:
    return _SIM_ROOT


def cell_base(name: str) -> str:
    return name.removesuffix("_mm_coords")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check layout JSON units/layers/ports/vias against a pipeline contract.")
    parser.add_argument("layout_json", nargs="*", type=Path, help="Explicit *_layout.json files to check.")
    parser.add_argument("--candidate", nargs="*", default=None, help="Candidate ids. The checker reads <candidate>_layout.json from --out-dir.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Layout output directory. Default uses the active project sweep or pipeline.")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--sweep-id", default=None)
    parser.add_argument("--pipeline-id", default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--topology-check", choices=("auto", "none", "pixel_qr_bpf"), default="auto")
    parser.add_argument("--min-metal-spacing-mm", type=float, default=0.1016)
    parser.add_argument("--max-island-components", type=int, default=None)
    return parser.parse_args()


def resolve_layout_paths(args: argparse.Namespace, root: Path, out_dir: Path | None) -> list[Path]:
    paths = [path if path.is_absolute() else root / path for path in args.layout_json]
    for candidate in args.candidate or []:
        if out_dir is None:
            raise SystemExit("--candidate requires --out-dir or a project/pipeline layout output directory.")
        paths.append(out_dir / f"{cell_base(candidate)}_layout.json")
    if not paths:
        raise SystemExit("No layout JSON specified. Use positional files or --candidate.")
    return paths


def main() -> int:
    args = parse_args()
    root = repo_root()
    project = load_project(args.project_id, root=root)
    sweep = project.get_sweep(args.sweep_id)
    pipeline_id = resolve_pipeline_id(project, sweep, args.pipeline_id)
    if not pipeline_id:
        raise SystemExit("No pipeline_id found. Set --pipeline-id or add pipeline_id to project/sweep config.")
    pipeline = load_pipeline(pipeline_id, root=root)
    out_dir = args.out_dir or pipeline.layout.layout_output_dir or (sweep.layouts_dir if sweep else None)
    if out_dir is not None and not out_dir.is_absolute():
        out_dir = root / out_dir

    paths = resolve_layout_paths(args, root, out_dir)
    report_rows: list[dict[str, object]] = []
    all_ok = True

    print(f"pipeline_id: {pipeline.pipeline_id}")
    print(f"project_id:  {project.project_id}")
    print(f"sweep_id:    {sweep.sweep_id if sweep else ''}")
    for path in paths:
        print(f"\nlayout_json: {path}")
        if not path.exists():
            all_ok = False
            row = {"layout_json": str(path), "name": "layout_json.exists", "ok": False, "message": "layout JSON file must exist"}
            report_rows.append(row)
            print("FAIL layout_json.exists: layout JSON file must exist")
            continue

        layout = load_layout_json(path)
        checks = validate_layout_contract(
            layout,
            units=pipeline.units,
            metal_layer=pipeline.layer_map.metal_layer,
            via_layer=pipeline.layer_map.via_layer,
            boundary_layer=pipeline.layer_map.boundary_layer,
            layer_map_version=pipeline.layer_map.layer_map_version,
            port_names=tuple(pipeline.ports.names),
        )
        metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
        run_pixel_qr_check = args.topology_check == "pixel_qr_bpf" or (
            args.topology_check == "auto" and (metadata.get("topology") == "pixel_qr_bpf" or pipeline.device_id == "filter.pixel_qr_bpf")
        )
        if run_pixel_qr_check:
            checks.extend(
                validate_pixel_qr_bpf_layout(
                    layout,
                    metal_layer=pipeline.layer_map.metal_layer,
                    min_spacing_mm=args.min_metal_spacing_mm,
                    max_island_components=args.max_island_components,
                )
            )
        for check in checks:
            all_ok = all_ok and check.ok
            report_rows.append(
                {
                    "layout_json": str(path),
                    "name": check.name,
                    "ok": check.ok,
                    "message": check.message,
                }
            )
            status = "PASS" if check.ok else "FAIL"
            print(f"{status} {check.name}: {check.message}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(
                {
                    "pipeline_id": pipeline.pipeline_id,
                    "project_id": project.project_id,
                    "sweep_id": sweep.sweep_id if sweep else None,
                    "checks": report_rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nWrote layout check report: {args.json_out}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

