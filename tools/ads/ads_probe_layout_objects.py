#!/usr/bin/env python3
r"""Deep-read ADS layout OA objects for EM port reference debugging."""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]


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


def _safe_attr(obj: object, attr: str) -> tuple[bool, Any]:
    try:
        return True, getattr(obj, attr)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _safe_signature(obj: object) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return ""


def _scalar(value: object, *, depth: int = 0) -> object:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Path):
        return str(value)
    if depth >= 2:
        return repr(value)
    if isinstance(value, tuple | list):
        return [_scalar(item, depth=depth + 1) for item in value[:20]]
    if isinstance(value, dict):
        return {str(key): _scalar(item, depth=depth + 1) for key, item in list(value.items())[:50]}
    attrs: dict[str, object] = {}
    for name in (
        "name",
        "number",
        "x",
        "y",
        "left",
        "bottom",
        "right",
        "top",
        "layer",
        "purpose",
        "term_name",
        "is_positive",
        "object",
    ):
        ok, item = _safe_attr(value, name)
        if ok and item is not value:
            attrs[name] = _scalar(item, depth=depth + 1)
    if attrs:
        attrs["_repr"] = repr(value)
        return attrs
    return repr(value)


def _iter_collection(value: object | None) -> list[object]:
    if value is None:
        return []
    try:
        return list(value)
    except Exception:
        return []


def _snapshot_props(obj: object) -> list[dict[str, object]]:
    ok, props = _safe_attr(obj, "props")
    if not ok:
        return [{"error": _scalar(props)}]
    rows: list[dict[str, object]] = []
    for prop in _iter_collection(props):
        row: dict[str, object] = {"repr": repr(prop)}
        for attr in ("name", "value", "expr", "expression", "var_name"):
            ok, value = _safe_attr(prop, attr)
            if ok:
                row[attr] = _scalar(value)
        rows.append(row)
    return rows


def _snapshot_group_members(obj: object) -> list[dict[str, object]]:
    ok, members = _safe_attr(obj, "members")
    if not ok:
        return []
    rows: list[dict[str, object]] = []
    for member in _iter_collection(members):
        row: dict[str, object] = {"repr": repr(member), "python_type": type(member).__name__}
        ok, member_object = _safe_attr(member, "object")
        if ok:
            row["object"] = _snapshot_object(member_object, include_members=False)
        rows.append(row)
    return rows


def _snapshot_object(obj: object, *, include_members: bool = False) -> dict[str, object]:
    row: dict[str, object] = {
        "repr": repr(obj),
        "python_type": type(obj).__name__,
    }
    ok, ads_type = _safe_attr(obj, "type")
    if ok:
        row["type"] = _scalar(ads_type)
    for attr in (
        "name",
        "number",
        "term_type",
        "is_implicit",
        "is_delta_gap_port",
        "ref_plane_shift_dbu",
        "ref_plane_shift_meters",
        "angle",
        "snap_point",
        "layer",
        "purpose",
        "bbox",
        "layer_id",
        "net",
        "parent",
        "groups",
        "members",
        "group_members",
        "objects",
        "object",
        "fig_group_mem",
        "has_any_pinfigs",
    ):
        ok, value = _safe_attr(obj, attr)
        if ok:
            row[attr] = _scalar(value)
    ok, secondary = _safe_attr(obj, "secondary_term_info")
    if ok:
        row["secondary_term_info"] = [_scalar(item) for item in _iter_collection(secondary)]
    row["props"] = _snapshot_props(obj)
    group_members = _snapshot_group_members(obj)
    if group_members:
        row["group_member_objects"] = group_members
    if include_members:
        attrs: dict[str, str] = {}
        methods: dict[str, str] = {}
        for name in dir(obj):
            if name.startswith("_"):
                continue
            ok, value = _safe_attr(obj, name)
            if not ok:
                attrs[name] = str(value)
            elif callable(value):
                methods[name] = _safe_signature(value)
            else:
                attrs[name] = type(value).__name__
        row["public_attrs"] = attrs
        row["public_methods"] = methods
    return row


def _try_iterators(db_uu: object, design: object, *, limit: int) -> dict[str, object]:
    result: dict[str, object] = {}
    for name in sorted(n for n in dir(db_uu) if n.endswith("Iter")):
        cls = getattr(db_uu, name, None)
        if cls is None:
            continue
        entry: dict[str, object] = {"signature": _safe_signature(cls)}
        try:
            iterator = cls(design)
            items = list(iterator)[:limit]
            entry["count_sample"] = len(items)
            entry["items"] = [_snapshot_object(item) for item in items]
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
        result[name] = entry
    return result


def probe_layout_objects(
    workspace_path: Path,
    library_name: str,
    cell_name: str,
    view_name: str,
    *,
    limit: int,
    include_design_members: bool,
) -> dict[str, object]:
    ensure_hpeesof_dir()
    import keysight.ads.de as de
    from keysight.ads.de import db_uu

    workspace = de.open_workspace(str(workspace_path))
    try:
        design = db_uu.open_design((library_name, cell_name, view_name), "ReadOnly")
        try:
            report: dict[str, object] = {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "python": sys.executable,
                "target": {
                    "workspace": str(workspace_path),
                    "library": library_name,
                    "cell": cell_name,
                    "view": view_name,
                },
                "design": _snapshot_object(design, include_members=include_design_members),
                "collections": {},
                "iterators": _try_iterators(db_uu, design, limit=limit),
            }
            collections = report["collections"]
            assert isinstance(collections, dict)
            for attr in ("terms", "nets", "pins", "figs", "groups", "instances", "refs"):
                ok, value = _safe_attr(design, attr)
                if ok:
                    collections[attr] = [
                        _snapshot_object(item, include_members=include_design_members)
                        for item in _iter_collection(value)[:limit]
                    ]
                else:
                    collections[attr] = {"error": _scalar(value)}
            return report
        finally:
            close_design = getattr(design, "close_design", None)
            if callable(close_design):
                close_design()
    finally:
        workspace.close()


def render_markdown(report: dict[str, object]) -> str:
    target = report.get("target", {})
    cell = target.get("cell", "") if isinstance(target, dict) else ""
    lines = [
        "# ADS Layout Object Probe",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Cell: `{cell}`",
        "",
        "## Collections",
        "",
    ]
    collections = report.get("collections", {})
    if isinstance(collections, dict):
        for name, rows in collections.items():
            if isinstance(rows, list):
                lines.append(f"- `{name}`: {len(rows)} sampled")
            else:
                lines.append(f"- `{name}`: {rows}")
    lines.extend(["", "## Iterator Samples", ""])
    iterators = report.get("iterators", {})
    if isinstance(iterators, dict):
        for name, entry in iterators.items():
            if not isinstance(entry, dict):
                continue
            if "error" in entry:
                continue
            lines.append(f"- `{name}`: {entry.get('count_sample', 0)} sampled")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deep-read ADS layout objects for EM port reference debugging.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--view", default="layout")
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--include-design-members", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser.parse_args()


def _resolve_output_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return _REPO_ROOT / path


def main() -> None:
    args = parse_args()
    report = probe_layout_objects(
        args.workspace,
        args.library,
        args.cell,
        args.view,
        limit=args.limit,
        include_design_members=args.include_design_members,
    )
    out_path = _resolve_output_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote ADS layout object probe: {out_path}", flush=True)
    if args.markdown_out:
        markdown_path = _resolve_output_path(args.markdown_out)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
        print(f"Wrote ADS layout object summary: {markdown_path}", flush=True)


if __name__ == "__main__":
    main()
