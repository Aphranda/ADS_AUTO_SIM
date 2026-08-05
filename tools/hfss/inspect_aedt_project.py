#!/usr/bin/env python3
"""Inspect an AEDT project without modifying it.

The default mode is intentionally lightweight: list designs, design types,
ports/excitations, setup names, and object group counts. Use --include-objects
or --include-properties only when a detailed object dump is needed because
large imported connector models can be slow to enumerate through AEDT gRPC.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import apply_grpc_startup_compat, apply_pyaedt_settings, startup_snapshot

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _clean_design_name(name: str) -> str:
    text = str(name)
    if ";" in text and text.split(";", 1)[0].isdigit():
        return text.split(";", 1)[1]
    return text


def _safe(call, default: Any = None) -> Any:
    try:
        return call()
    except Exception as exc:  # pragma: no cover - depends on AEDT COM/gRPC.
        if default is not None:
            return default
        return {"error": repr(exc)}


def _properties(oeditor: Any, tab: str, server: str) -> dict[str, Any]:
    try:
        names = list(oeditor.GetProperties(tab, server))
    except Exception as exc:
        return {"_error": repr(exc)}
    output: dict[str, Any] = {}
    for name in names:
        try:
            output[str(name)] = oeditor.GetPropertyValue(tab, server, name)
        except Exception as exc:
            output[str(name)] = {"error": repr(exc)}
    return output


def _object_group_names(oeditor: Any, group: str) -> list[str] | dict[str, str]:
    try:
        return [str(name) for name in oeditor.GetObjectsInGroup(group)]
    except Exception as exc:
        return {"error": repr(exc)}


def _unique_in_order(values: list[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        if value and value not in output:
            output.append(value)
    return output


def _top_level_design_entries(text: str) -> list[dict[str, Any]]:
    entries = []
    pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\(1002,\s*0,\s*(\d+),\s*(\d+),", re.MULTILINE)
    for match in pattern.finditer(text):
        name = match.group(1)
        entries.append(
            {
                "name": name,
                "kind_code": int(match.group(2)),
                "active_flag": int(match.group(3)),
                "connector_like": any(token in name.lower() for token in ("sma", "connector", "conn", "coax", "launch")),
            }
        )
    return entries


def _planar_circuit_blocks(text: str) -> dict[str, str]:
    blocks = {}
    pattern = re.compile(r"\$begin 'PlanarEMCircuit'(?P<body>.*?)\$end 'PlanarEMCircuit'", re.DOTALL)
    for match in pattern.finditer(text):
        body = match.group("body")
        name_match = re.search(r"^\s*Name='([^']+)'", body, re.MULTILINE)
        if name_match:
            blocks[name_match.group(1)] = body
    return blocks


def _parse_component_instances(block: str) -> list[dict[str, Any]]:
    instances = []
    comp_pattern = re.compile(r"\$begin 'Compinst'(?P<body>.*?)\$end 'Compinst'", re.DOTALL)
    for match in comp_pattern.finditer(block):
        body = match.group("body")
        comp_name = re.search(r"^\s*CompName='([^']+)'", body, re.MULTILINE)
        comp_id = re.search(r"^\s*ID='([^']+)'", body, re.MULTILINE)
        inst_name = re.search(r"TextProp\('InstanceName',\s*'[^']*',\s*'[^']*',\s*'([^']+)'\)", body)
        instances.append(
            {
                "id": comp_id.group(1) if comp_id else None,
                "component": comp_name.group(1) if comp_name else None,
                "instance_name": inst_name.group(1) if inst_name else None,
            }
        )
    schematic_pattern = re.compile(
        r"SchCompInst\('(?P<component>[^']+)',\s*'(?P<page>[^']+)',\s*'(?P<symbol_id>[^']+)',\s*(?P<orient>\d+),\s*'(?P<id>[^']+)',\s*'(?P<mode>[^']+)',\s*(?P<x>[-+0-9.eE]+),\s*(?P<y>[-+0-9.eE]+),\s*(?P<angle>[-+0-9.eE]+),"
    )
    schematic = {}
    for match in schematic_pattern.finditer(block):
        schematic[match.group("id")] = {
            "component": match.group("component"),
            "page": match.group("page"),
            "symbol_id": match.group("symbol_id"),
            "orientation_code": int(match.group("orient")),
            "mode": match.group("mode"),
            "x_m": float(match.group("x")),
            "y_m": float(match.group("y")),
            "angle_deg": float(match.group("angle")),
        }
    for instance in instances:
        if instance["id"] in schematic:
            instance["schematic"] = schematic[instance["id"]]
    return instances


def _parse_ports(block: str) -> list[dict[str, Any]]:
    ports = []
    port_pattern = re.compile(r"\$begin 'IPort'(?P<body>.*?)\$end 'IPort'", re.DOTALL)
    for match in port_pattern.finditer(block):
        body = match.group("body")
        port = re.search(r"^\s*PortName='([^']+)'", body, re.MULTILINE)
        domain = re.search(r"Domain\(([^)]*)\)", body)
        ports.append({"name": port.group(1) if port else None, "domain": domain.group(1) if domain else None})
    return ports


def _parse_nets(block: str) -> list[str]:
    return _unique_in_order(re.findall(r"^\s*NetName='([^']+)'", block, re.MULTILINE))


def inspect_project_file(args: argparse.Namespace) -> dict[str, Any]:
    text = args.project.read_text(encoding="utf-8-sig", errors="replace")
    top_level_entries = _top_level_design_entries(text)
    all_names = [entry["name"] for entry in top_level_entries]
    selected = [_clean_design_name(name) for name in args.design] if args.design else all_names
    circuit_blocks = _planar_circuit_blocks(text)
    lowered_tokens = ("sma", "connector", "conn", "coax", "launch")
    token_lines = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        if any(token in lower for token in lowered_tokens):
            token_lines.append({"line": line_no, "text": line.strip()[:240]})
            if 0 <= args.max_file_token_lines <= len(token_lines):
                break
    designs = []
    for design in selected:
        occurrences = [m.start() for m in re.finditer(re.escape(design), text)]
        block = circuit_blocks.get(design, "")
        designs.append(
            {
                "design": design,
                "occurrences": len(occurrences),
                "connector_like": any(token in design.lower() for token in lowered_tokens),
                "top_level_entry": next((entry for entry in top_level_entries if entry["name"] == design), None),
                "planar_circuit": bool(block),
                "component_instances": _parse_component_instances(block) if block else [],
                "ports": _parse_ports(block) if block else [],
                "nets": _parse_nets(block) if block else [],
            }
        )
    return {
        "backend": "file",
        "project": str(args.project),
        "exists": args.project.exists(),
        "size_bytes": args.project.stat().st_size if args.project.exists() else None,
        "top_level_designs": top_level_entries,
        "selected_designs": selected,
        "designs": designs,
        "connector_like_names": [name for name in all_names if any(token in name.lower() for token in lowered_tokens)],
        "token_lines": token_lines,
        "notes": [
            "file backend reads only saved AEDT content and does not see unsaved AEDT GUI changes",
            "use --backend pyaedt for live session details",
        ],
    }


def _design_names_from_app(app: Any) -> list[str]:
    for attr in ("design_list", "design_names"):
        value = getattr(app, attr, None)
        if value:
            names = value() if callable(value) else value
            return [_clean_design_name(str(name)) for name in names]
    return [_clean_design_name(str(getattr(app, "design_name", "")))]


def _project_design_type(app: Any, design: str) -> str | None:
    def query() -> str | None:
        project_name = app.project_name
        oproject = app.odesktop.GetProjectByName(project_name)
        odesign = oproject.GetDesign(design)
        return str(odesign.GetDesignType())

    result = _safe(query, default=None)
    return str(result) if result else None


def _inspect_design(
    app: Any,
    *,
    design: str,
    include_objects: bool,
    include_properties: bool,
    max_objects: int,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "design": design,
        "design_type": _project_design_type(app, design),
    }
    try:
        app.set_active_design(design)
        item["active"] = True
    except Exception as exc:
        item["active"] = False
        item["set_active_design_error"] = repr(exc)
        return item

    item["app_design_type"] = str(getattr(app, "design_type", ""))
    item["solution_type"] = _safe(lambda: app.solution_type)
    item["setups"] = _safe(lambda: list(app.setup_names), default=[])
    item["ports"] = _safe(lambda: list(getattr(app, "port_list", [])), default=[])
    item["excitations"] = _safe(lambda: list(getattr(app, "excitations", [])), default=[])

    try:
        boundaries = []
        for boundary in app.boundaries:
            entry = {"name": getattr(boundary, "name", str(boundary)), "type": getattr(boundary, "type", None)}
            if include_properties:
                entry["props"] = dict(getattr(boundary, "props", {}))
            boundaries.append(entry)
        item["boundaries"] = boundaries
    except Exception as exc:
        item["boundaries_error"] = repr(exc)

    oeditor = getattr(getattr(app, "modeler", None), "oeditor", None)
    if oeditor is None:
        return item

    groups = {}
    for group in ("Solids", "Sheets", "Lines", "Unclassified", "Non Model", "Measure", "Planes", "Points"):
        names = _object_group_names(oeditor, group)
        groups[group] = {"count": len(names), "names": names} if isinstance(names, list) else names
    item["object_groups"] = groups

    if not include_objects:
        return item

    object_names: list[str] = []
    for value in groups.values():
        names = value.get("names") if isinstance(value, dict) else None
        if isinstance(names, list):
            for name in names:
                if name not in object_names:
                    object_names.append(name)
    if max_objects >= 0:
        object_names = object_names[:max_objects]

    objects = []
    for name in object_names:
        obj: dict[str, Any] = {"name": name}
        if include_properties:
            for tab in ("Geometry3DAttributeTab", "Geometry3DCmdTab", "BaseElementTab"):
                props = _properties(oeditor, tab, name)
                if props and "_error" not in props:
                    obj[tab] = props
        primitive = _safe(lambda n=name: app.modeler[n], default=None)
        if primitive is not None:
            for attr in ("material_name", "solve_inside", "model", "group_name", "transparency", "color"):
                try:
                    obj[attr] = getattr(primitive, attr)
                except Exception:
                    pass
            obj["bounding_box"] = _safe(lambda p=primitive: p.bounding_box, default=None)
        objects.append(obj)
    item["objects"] = objects
    item["objects_truncated"] = max_objects >= 0 and len(objects) == max_objects
    return item


def _create_app(args: argparse.Namespace, *, design: str | None = None) -> Any:
    if args.app == "hfss":
        from ansys.aedt.core import Hfss, settings

        apply_pyaedt_settings(settings)

        cls = Hfss
    else:
        from ansys.aedt.core import Hfss3dLayout, settings

        apply_pyaedt_settings(settings)

        cls = Hfss3dLayout

    return cls(
        project=str(args.project),
        design=design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )


def inspect_project(args: argparse.Namespace) -> dict[str, Any]:
    app = _create_app(args, design=args.design[0] if args.app == "hfss" and args.design else None)
    try:
        all_designs = _design_names_from_app(app)
        selected = [_clean_design_name(name) for name in args.design] if args.design else all_designs
        payload: dict[str, Any] = {
            "project": str(args.project),
            "project_name": getattr(app, "project_name", None),
            "active_design": getattr(app, "design_name", None),
            "app": args.app,
            "aedt_startup": startup_snapshot(),
            "all_designs": all_designs,
            "selected_designs": selected,
            "designs": [],
        }
        if args.app == "hfss":
            if not args.design:
                payload["warning"] = "--app hfss works best with explicit --design for HFSS 3D connector designs."
            for idx, design in enumerate(selected):
                design_app = app if idx == 0 else _create_app(args, design=design)
                try:
                    payload["designs"].append(
                        _inspect_design(
                            design_app,
                            design=design,
                            include_objects=args.include_objects or args.include_properties,
                            include_properties=args.include_properties,
                            max_objects=args.max_objects,
                        )
                    )
                finally:
                    if idx != 0 and not args.keep_attached:
                        design_app.release_desktop(close_projects=False, close_desktop=False)
        else:
            payload["designs"] = [
                _inspect_design(
                    app,
                    design=design,
                    include_objects=args.include_objects or args.include_properties,
                    include_properties=args.include_properties,
                    max_objects=args.max_objects,
                )
                for design in selected
            ]
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect an AEDT project without saving it.")
    parser.add_argument("--project", type=Path, required=True, help="AEDT project path.")
    parser.add_argument(
        "--backend",
        choices=["file", "pyaedt"],
        default="file",
        help="file parses saved AEDT text without launching AEDT; pyaedt reads the live project through AEDT APIs.",
    )
    parser.add_argument("--design", action="append", default=[], help="Design name to inspect. Repeat for multiple designs.")
    parser.add_argument(
        "--app",
        choices=["hfss3dlayout", "hfss"],
        default="hfss3dlayout",
        help="AEDT application API to use. Use hfss for imported 3D connector designs.",
    )
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--new-desktop", action="store_true", help="Start a new AEDT desktop session instead of attaching when possible.")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--include-objects", action="store_true", help="List object names and lightweight object data.")
    parser.add_argument("--include-properties", action="store_true", help="Dump object properties. This can be slow for connector models.")
    parser.add_argument("--max-objects", type=int, default=50, help="Max objects per design. Use -1 for no limit.")
    parser.add_argument("--max-file-token-lines", type=int, default=80, help="Max connector-related lines to include for file backend. Use -1 for no limit.")
    parser.add_argument("--keep-attached", action="store_true", help="Do not release the PyAEDT desktop object before exit.")
    parser.add_argument("--close-projects", action="store_true", help="Close AEDT projects on release.")
    parser.add_argument("--close-desktop", action="store_true", help="Close AEDT desktop on release.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect_project_file(args) if args.backend == "file" else inspect_project(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
