#!/usr/bin/env python3
r"""Apply ADS OA secondary-term EM port references to a layout.

This is an experimental probe for ADS EM port reference persistence. It writes
the layout/OA Term.secondary_term_info field, which is separate from the
emSetup XML UI cache.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_TOOLS_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
for _path in (_TOOLS_ROOT, _SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import profile_names, resolve_library, resolve_workspace
from simads.ads.layout import load_p1_p2_locations


def ensure_hpeesof_dir() -> None:
    if os.environ.get("HPEESOF_DIR"):
        return
    executable = Path(sys.executable).resolve()
    try:
        ads_root = executable.parents[2]
    except IndexError:
        return
    if (ads_root / "tools").exists():
        os.environ["HPEESOF_DIR"] = str(ads_root)


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{stamp}] {message}", flush=True)


def _read_layer_context(params_path: Path | None) -> tuple[str, str, tuple[float, float], tuple[float, float]]:
    if params_path is None:
        return "ETCH_TOP", "ETCH_INNER1", (0.0, 0.0), (1.0, 0.0)
    data = json.loads(params_path.read_text(encoding="utf-8"))
    params = data.get("parameters", {}) if isinstance(data, dict) else {}
    signal_layer = str(params.get("signal_layer") or params.get("metal_layer") or "ETCH_TOP")
    reference_layer = str(params.get("reference_ground_layer") or params.get("ground_layer") or "ETCH_INNER1")
    p1, p2 = load_p1_p2_locations(params_path)
    return signal_layer, reference_layer, p1, p2


def _find_or_create_term_with_pin(
    design: Any,
    db_uu: Any,
    *,
    name: str,
    layer: str,
    point: tuple[float, float],
) -> Any:
    try:
        existing = design.find_term(name)
    except Exception:
        existing = None
    if existing is not None:
        return existing

    net = design.find_or_add_net(name)
    term_type = getattr(getattr(db_uu, "TermType", None), "INPUT_OUTPUT", None)
    term = design.add_term(net, name, term_type) if term_type is not None else design.add_term(net, name)
    dot = design.add_dot(design.create_layer_id(layer), point)
    design.add_pin(term, [dot])
    return term


def _secondary_snapshot(term: Any) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in list(term.secondary_term_info):
        rows.append(
            {
                "term_name": getattr(item, "term_name", None),
                "is_positive": getattr(item, "is_positive", None),
            }
        )
    return rows


def apply_secondary_references(
    workspace_path: Path,
    library_name: str,
    cell_name: str,
    params_path: Path | None,
    *,
    mode: str,
    reference_layer: str | None,
) -> dict[str, object]:
    ensure_hpeesof_dir()
    from keysight.ads import de
    from keysight.ads.de import db_uu

    signal_layer, params_reference_layer, p1, p2 = _read_layer_context(params_path)
    ref_layer = reference_layer or params_reference_layer

    log(f"Opening ADS workspace: {workspace_path}")
    workspace = de.open_workspace(str(workspace_path))
    try:
        design = db_uu.open_design((library_name, cell_name, "layout"), "Append")
        try:
            rows: list[dict[str, object]] = []
            targets = [("P1", p1), ("P2", p2)]
            shared_ground_term = None
            if mode == "shared-ground-term":
                shared_ground_term = _find_or_create_term_with_pin(
                    design,
                    db_uu,
                    name="Gnd",
                    layer=ref_layer,
                    point=p1,
                )
                dot = design.add_dot(design.create_layer_id(ref_layer), p2)
                design.add_pin(shared_ground_term, [dot])

            for port_name, point in targets:
                term = design.find_term(port_name)
                if term is None:
                    raise RuntimeError(f"Term not found: {port_name}")

                if mode == "special-gnd-token":
                    secondary_name = "::__GND__"
                elif mode == "shared-ground-term":
                    secondary_name = "Gnd"
                elif mode == "per-port-ground-term":
                    secondary_name = f"{port_name}_GND"
                    _find_or_create_term_with_pin(
                        design,
                        db_uu,
                        name=secondary_name,
                        layer=ref_layer,
                        point=point,
                    )
                else:
                    raise ValueError(f"unknown mode: {mode}")

                term.is_delta_gap_port = True
                term.secondary_term_info = [db_uu.SecondaryTermInfo(secondary_name, False)]
                rows.append(
                    {
                        "port": port_name,
                        "signal_layer": signal_layer,
                        "reference_layer": ref_layer,
                        "secondary_name": secondary_name,
                        "secondary_term_info": _secondary_snapshot(term),
                        "is_delta_gap_port": bool(term.is_delta_gap_port),
                    }
                )

            log(f"Saving layout with secondary EM port references: {library_name}:{cell_name}:layout")
            design.save_design()
        finally:
            close_design = getattr(design, "close_design", None)
            if callable(close_design):
                close_design()
    finally:
        workspace.close()

    return {
        "workspace": str(workspace_path),
        "library": library_name,
        "cell": cell_name,
        "mode": mode,
        "rows": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply ADS OA secondary-term port references to a layout.")
    parser.add_argument("--profile", default="home_simads_em_parallel", choices=profile_names())
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--library", default=None)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--params", type=Path, default=None)
    parser.add_argument("--reference-layer", default=None)
    parser.add_argument(
        "--mode",
        default="per-port-ground-term",
        choices=["special-gnd-token", "shared-ground-term", "per-port-ground-term"],
    )
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    result = apply_secondary_references(
        workspace,
        library,
        args.cell,
        args.params,
        mode=args.mode,
        reference_layer=args.reference_layer,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote secondary port reference probe: {args.out}", flush=True)
    print(text, flush=True)


if __name__ == "__main__":
    main()
