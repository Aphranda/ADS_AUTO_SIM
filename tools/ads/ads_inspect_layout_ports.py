#!/usr/bin/env python3
r"""Inspect ADS layout port objects and EM setup port state.

Run with ADS Python for live OpenAccess layout inspection, for example:

    D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe \
        tools\ads\ads_inspect_layout_ports.py \
        --workspace D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR \
        --library SIMADS_EM_PAR_lib \
        --cell i7_fr4_r13_rt_b_l555_tp_jlc_fe9e10_mm \
        --out projects\bfp_6_8g_i7_fr4\reports\ads_layout_ports_i7_r13_20260803.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


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


def _safe_call(obj: object, method: str, *args: object) -> tuple[bool, Any]:
    candidate = getattr(obj, method, None)
    if not callable(candidate):
        return False, "missing"
    try:
        return True, candidate(*args)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _scalar(value: object) -> object:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple | list):
        return [_scalar(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _scalar(item) for key, item in value.items()}

    attrs = {}
    for name in ("x", "y", "left", "bottom", "right", "top", "layer", "purpose", "name"):
        ok, item = _safe_attr(value, name)
        if ok and item is not value:
            attrs[name] = _scalar(item)
    if attrs:
        attrs["_repr"] = repr(value)
        return attrs
    return repr(value)


def _object_type(obj: object) -> str:
    type_attr = _safe_attr(obj, "type")
    if type_attr[0]:
        return str(type_attr[1])
    return type(obj).__name__


def _iter_collection(collection: object | None) -> list[object]:
    if collection is None:
        return []
    try:
        return list(collection)
    except Exception:
        return []


def _named_object(obj: object | None) -> object:
    if obj is None:
        return None
    ok, name = _safe_attr(obj, "name")
    if ok:
        return str(name)
    return repr(obj)


def _snapshot_layer_id(layer_id: object | None) -> dict[str, object] | None:
    if layer_id is None:
        return None
    data: dict[str, object] = {"repr": repr(layer_id)}
    for attr in ("layer", "purpose"):
        ok, value = _safe_attr(layer_id, attr)
        if ok:
            data[attr] = _scalar(value)
    return data


def _snapshot_secondary_term_info(items: Iterable[object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in items:
        row: dict[str, object] = {"repr": repr(item)}
        for attr in ("term_name", "is_positive"):
            ok, value = _safe_attr(item, attr)
            if ok:
                row[attr] = _scalar(value)
        result.append(row)
    return result


def _snapshot_param_collection(collection: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in _iter_collection(collection):
        row: dict[str, object] = {"repr": repr(item)}
        for attr in ("name", "var_name", "value", "expr", "expression"):
            ok, value = _safe_attr(item, attr)
            if ok:
                row[attr] = _scalar(value)
        for method in ("evaluate_without_expr",):
            ok, value = _safe_call(item, method)
            if ok:
                row[method] = _scalar(value)
        rows.append(row)
    return rows


def _snapshot_pinfig(pinfig: object) -> dict[str, object]:
    data: dict[str, object] = {
        "repr": repr(pinfig),
        "python_type": type(pinfig).__name__,
        "type": _object_type(pinfig),
    }
    for attr in ("layer", "purpose", "is_filled", "is_closed"):
        ok, value = _safe_attr(pinfig, attr)
        if ok:
            data[attr] = _scalar(value)
    ok, layer_id = _safe_attr(pinfig, "layer_id")
    if ok:
        data["layer_id"] = _snapshot_layer_id(layer_id)
    ok, bbox = _safe_attr(pinfig, "bbox")
    if ok:
        data["bbox"] = _scalar(bbox)
    ok, net = _safe_attr(pinfig, "net")
    if ok:
        data["net"] = _named_object(net)
    ok, sticky = _safe_call(pinfig, "net_is_sticky")
    if ok:
        data["net_is_sticky"] = _scalar(sticky)
    return data


def _snapshot_pin(pin: object, db_uu: object | None = None) -> dict[str, object]:
    data: dict[str, object] = {
        "repr": repr(pin),
        "python_type": type(pin).__name__,
        "type": _object_type(pin),
    }
    for attr in (
        "name",
        "term_name",
        "term_number",
        "angle",
        "has_any_pinfigs",
        "needs_drawing_artifact",
        "snap_point",
    ):
        ok, value = _safe_attr(pin, attr)
        if ok:
            data[attr] = _scalar(value)
    ok, net = _safe_attr(pin, "net")
    if ok:
        data["net"] = _named_object(net)
    for method in ("get_pinfig_bbox", "get_pin_artifact_bbox_only", "get_pinfig_bbox_with_artifact"):
        ok, value = _safe_call(pin, method)
        if ok:
            data[method] = _scalar(value)

    pinfigs: list[object] = []
    if db_uu is not None:
        pinfig_iter = getattr(db_uu, "PinFigIter", None)
        if pinfig_iter is not None:
            try:
                pinfigs = list(pinfig_iter(pin))
            except Exception as exc:
                data["pinfig_iter_error"] = f"{type(exc).__name__}: {exc}"
    data["pinfigs"] = [_snapshot_pinfig(pinfig) for pinfig in pinfigs]
    return data


def snapshot_term(term: object, db_uu: object | None = None) -> dict[str, object]:
    data: dict[str, object] = {
        "repr": repr(term),
        "python_type": type(term).__name__,
        "type": _object_type(term),
    }
    for attr in (
        "name",
        "number",
        "term_type",
        "is_implicit",
        "is_delta_gap_port",
        "ref_plane_shift_dbu",
        "ref_plane_shift_meters",
    ):
        ok, value = _safe_attr(term, attr)
        if ok:
            data[attr] = _scalar(value)
    ok, net = _safe_attr(term, "net")
    if ok:
        data["net"] = _named_object(net)
    ok, secondary = _safe_attr(term, "secondary_term_info")
    if ok:
        data["secondary_term_info"] = _snapshot_secondary_term_info(_iter_collection(secondary))
    ok, params = _safe_attr(term, "parameters")
    if ok:
        data["parameters"] = _snapshot_param_collection(params)
    ok, props = _safe_attr(term, "props")
    if ok:
        data["props"] = _snapshot_param_collection(props)
    ok, pins = _safe_attr(term, "pins")
    data["pins"] = [_snapshot_pin(pin, db_uu) for pin in _iter_collection(pins if ok else None)]
    return data


def _em_port_rows(xml_path: Path) -> list[dict[str, object]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows: list[dict[str, object]] = []
    for port in root.findall(".//PortView/Ports/Port"):
        row: dict[str, object] = {}
        for child in list(port):
            tag = child.tag.split("}", 1)[-1]
            row[tag] = (child.text or "").strip()
        rows.append(row)
    return rows


def inspect_em_setup_xml(workspace: Path, library: str, cell: str) -> dict[str, object]:
    candidates = {
        "canonical_em_state": workspace / library / cell / "em%Setup" / "emStateFile.xml",
        "gui_layout_state": workspace / "undefined" / "state" / library / cell / "layout" / "emSetup.xml",
    }
    result: dict[str, object] = {}
    for label, path in candidates.items():
        entry: dict[str, object] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            try:
                entry["ports"] = _em_port_rows(path)
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
        result[label] = entry
    return result


def inspect_layout_ports(
    workspace_path: Path,
    library_name: str,
    cell_name: str,
    view_name: str,
    terms: tuple[str, ...],
) -> dict[str, object]:
    ensure_hpeesof_dir()
    import keysight.ads.de as de
    from keysight.ads.de import db_uu

    workspace = de.open_workspace(str(workspace_path))
    try:
        try:
            library = de.Library.get(library_name)
        except RuntimeError:
            library = None
        if library is None:
            library_path = workspace_path / library_name
            library = workspace.open_library(library_name, library_path, mode=de.LibraryMode.SHARED)
        if library is None:
            raise RuntimeError(f"ADS library not found: {library_name}")

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
                "design": {},
                "terms": [],
                "em_setup": inspect_em_setup_xml(workspace_path, library_name, cell_name),
            }
            for attr in (
                "design_name",
                "unit_name",
                "uu_to_dbu_factor",
                "dbu_to_uu_factor",
                "meter_to_dbu_factor",
                "dbu_to_meter_factor",
                "meter_to_uu_factor",
                "uu_to_meter_factor",
                "bbox",
            ):
                ok, value = _safe_attr(design, attr)
                if ok:
                    report["design"][attr] = _scalar(value)  # type: ignore[index]

            selected_terms: list[object] = []
            if terms:
                for term_name in terms:
                    term = design.find_term(term_name)
                    if term is None:
                        selected_terms.append({"missing": term_name})
                    else:
                        selected_terms.append(term)
            else:
                selected_terms = list(design.terms)

            for term in selected_terms:
                if isinstance(term, dict):
                    report["terms"].append(term)  # type: ignore[union-attr]
                else:
                    report["terms"].append(snapshot_term(term, db_uu))  # type: ignore[union-attr]
            return report
        finally:
            close_design = getattr(design, "close_design", None)
            if callable(close_design):
                close_design()
    finally:
        workspace.close()


def render_markdown(report: dict[str, object]) -> str:
    target = report.get("target", {})
    target_text = (
        f"{target.get('library')}:{target.get('cell')}:{target.get('view')}"
        if isinstance(target, dict)
        else ""
    )
    lines = [
        "# ADS Layout Port Inspection",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Target: `{target_text}`",
        f"Python: `{report.get('python', '')}`",
        "",
        "## Layout Terms",
        "",
    ]
    for term in report.get("terms", []):
        if not isinstance(term, dict):
            continue
        if "missing" in term:
            lines.append(f"- `{term['missing']}`: missing")
            continue
        name = term.get("name", "")
        net = term.get("net", "")
        pin_count = len(term.get("pins", [])) if isinstance(term.get("pins"), list) else 0
        secondary = term.get("secondary_term_info", [])
        secondary_text = json.dumps(secondary, ensure_ascii=False) if secondary else "[]"
        lines.append(
            f"- `{name}`: net=`{net}`, pins={pin_count}, "
            f"delta_gap=`{term.get('is_delta_gap_port', '')}`, secondary={secondary_text}"
        )
        for pin in term.get("pins", []) if isinstance(term.get("pins"), list) else []:
            if not isinstance(pin, dict):
                continue
            pinfigs = pin.get("pinfigs", [])
            lines.append(
                f"  - pin `{pin.get('name', '')}`: angle=`{pin.get('angle', '')}`, "
                f"snap=`{pin.get('snap_point', '')}`, pinfigs={len(pinfigs) if isinstance(pinfigs, list) else 0}"
            )
            for pinfig in pinfigs if isinstance(pinfigs, list) else []:
                if not isinstance(pinfig, dict):
                    continue
                layer_id = pinfig.get("layer_id")
                lines.append(
                    f"    - fig type=`{pinfig.get('type', '')}`, "
                    f"layer=`{pinfig.get('layer', '')}`, purpose=`{pinfig.get('purpose', '')}`, "
                    f"layer_id=`{layer_id}`"
                )
    lines.extend(["", "## EM Setup XML", ""])
    em_setup = report.get("em_setup", {})
    if isinstance(em_setup, dict):
        for label, entry in em_setup.items():
            if not isinstance(entry, dict):
                continue
            lines.append(f"### `{label}`")
            lines.append("")
            lines.append(f"- path: `{entry.get('path', '')}`")
            lines.append(f"- exists: `{entry.get('exists', False)}`")
            ports = entry.get("ports", [])
            if isinstance(ports, list):
                for port in ports:
                    if isinstance(port, dict):
                        lines.append(
                            f"- port `{port.get('portName', '')}`: "
                            f"gndLayer=`{port.get('gndLayer', '')}`"
                        )
            if entry.get("error"):
                lines.append(f"- error: `{entry['error']}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect ADS layout Term/Pin port objects and EM setup gndLayer state.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--view", default="layout")
    parser.add_argument("--term", action="append", dest="terms", help="Term name to inspect. May be repeated.")
    parser.add_argument("--out", type=Path, required=True, help="JSON report path.")
    parser.add_argument("--markdown-out", type=Path, default=None, help="Optional Markdown summary path.")
    return parser.parse_args()


def _resolve_output_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return _REPO_ROOT / path


def main() -> None:
    args = parse_args()
    terms = tuple(args.terms or ("P1", "P2"))
    report = inspect_layout_ports(args.workspace, args.library, args.cell, args.view, terms)
    out_path = _resolve_output_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        markdown_path = _resolve_output_path(args.markdown_out)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote ADS layout port report: {out_path}", flush=True)
    if args.markdown_out:
        print(f"Wrote ADS layout port summary: {markdown_path}", flush=True)


if __name__ == "__main__":
    main()
