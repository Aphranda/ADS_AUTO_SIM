#!/usr/bin/env python3
"""Read HFSS 3D Layout primitive bounding boxes by layer without modifying the project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import (
    aedt_automation_lock,
    apply_grpc_startup_compat,
    apply_pyaedt_settings,
    start_aedt_reaper,
    startup_snapshot,
    wait_for_hfss3dlayout_ready,
)

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _safe(call, default: Any = None) -> Any:
    try:
        return call()
    except Exception as exc:  # pragma: no cover - AEDT API dependent.
        if default is not None:
            return default
        return {"error": f"{type(exc).__name__}: {exc}"}


def _num(value: Any) -> float | None:
    try:
        raw = getattr(value, "value", value)
        return float(raw)
    except Exception:
        return None


def _bbox_mm(value: Any) -> list[float] | None:
    if value is None:
        return None
    try:
        items = list(value)
    except Exception:
        return None
    nums = [_num(item) for item in items]
    if any(item is None for item in nums):
        return None
    vals = [float(item) for item in nums if item is not None]
    if len(vals) == 4:
        # EDB-like bbox is usually meters.
        scale = 1000.0 if max(abs(v) for v in vals) < 1.0 else 1.0
        return [v * scale for v in vals]
    if len(vals) == 6:
        # Modeler bbox is usually already in model units for 3D Layout.
        return vals
    return vals


def _object_record(app: Any, name: str, layer: str) -> dict[str, Any]:
    primitive = _safe(lambda: app.modeler[name], default=None)
    record: dict[str, Any] = {"name": name, "layer_query": layer}
    if primitive is None:
        record["primitive_found"] = False
        return record
    record["primitive_found"] = True
    for attr in ("name", "net_name", "layer_name", "type", "is_negative", "negative"):
        try:
            value = getattr(primitive, attr)
            record[attr] = value() if callable(value) else value
        except Exception:
            pass
    bbox = _safe(lambda: primitive.bounding_box, default=None)
    if bbox is None:
        bbox = _safe(lambda: primitive.bbox, default=None)
        if callable(bbox):
            bbox = _safe(bbox, default=None)
    record["bbox_raw"] = bbox
    record["bbox_mm"] = _bbox_mm(bbox)
    if record.get("bbox_mm") and len(record["bbox_mm"]) >= 4:
        b = record["bbox_mm"]
        if len(b) == 4:
            x0, y0, x1, y1 = b
            record["size_mm"] = [x1 - x0, y1 - y0]
            record["center_mm"] = [(x0 + x1) / 2.0, (y0 + y1) / 2.0]
        elif len(b) >= 6:
            x0, y0, z0, x1, y1, z1 = b[:6]
            record["size_mm"] = [x1 - x0, y1 - y0, z1 - z0]
            record["center_mm"] = [(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0]
    return record


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout, settings

    apply_pyaedt_settings(settings)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "layers": list(args.layer),
        "name_filters": list(args.name_filter),
        "aedt_startup": startup_snapshot(settings),
    }
    with aedt_automation_lock("inspect_hfss3dlayout_layer_bboxes") as lock_info:
        payload["aedt_lock"] = lock_info
        app = Hfss3dLayout(
            project=str(args.project),
            design=args.design,
            version=args.version,
            non_graphical=True,
            new_desktop=True,
            close_on_exit=False,
            remove_lock=args.remove_lock,
        )
        payload["aedt_reaper"] = start_aedt_reaper(
            app,
            label="inspect_hfss3dlayout_layer_bboxes",
            execute=True,
            script_started=True,
        )
        try:
            payload["ready"] = wait_for_hfss3dlayout_ready(app, timeout_s=args.ready_timeout_s)
            payload["ports"] = _safe(lambda: list(getattr(app, "port_list", [])), default=[])
            by_layer: dict[str, Any] = {}
            for layer in args.layer:
                names = _safe(lambda layer=layer: [str(item) for item in app.modeler.objects_by_layer(layer)], default=[])
                if args.name_filter:
                    names = [name for name in names if any(token.lower() in name.lower() for token in args.name_filter)]
                by_layer[layer] = {
                    "count": len(names),
                    "names": names,
                    "objects": [_object_record(app, name, layer) for name in names],
                }
            payload["objects_by_layer"] = by_layer
        finally:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read HFSS 3D Layout primitive bboxes by layer.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--layer", action="append", required=True)
    parser.add_argument("--name-filter", action="append", default=[])
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
