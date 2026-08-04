#!/usr/bin/env python3
"""Audit HFSS connector parameters across source, project, and layout instance.

This tool is intentionally read-only by default.  It compares:

* source HFSS design variables,
* project variables such as ``$sma_Pin_D``,
* HFSS 3D Layout component PassedParameterTab values,
* source-model geometry bounding boxes for key objects.

Use ``--sync-project-variables --execute --save`` only when the source connector
variables should be written into project variables.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_VARIABLES = [
    "Base_L",
    "Front_L",
    "Feet_L",
    "Base_D",
    "Front_W",
    "Feet_W",
    "PTFE_D",
    "Pin_D",
    "Pin_P",
    "Hole_D",
]


@dataclass(frozen=True)
class NumericValue:
    raw: str
    value: float
    unit: str


def _json_default(value: Any) -> str:
    return str(value)


def _safe(call) -> Any:
    try:
        return call()
    except Exception as exc:
        return {"error": repr(exc)}


def _parse_numeric(value: Any) -> NumericValue | None:
    text = str(value).strip()
    match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([A-Za-z]*)", text)
    if not match:
        return None
    return NumericValue(raw=text, value=float(match.group(1)), unit=match.group(2).lower())


def _to_mm(value: Any) -> float | None:
    parsed = _parse_numeric(value)
    if parsed is None:
        return None
    scale = {
        "": 1.0,
        "mm": 1.0,
        "mil": 0.0254,
        "um": 0.001,
        "nm": 1e-6,
        "m": 1000.0,
        "cm": 10.0,
        "in": 25.4,
    }.get(parsed.unit)
    if scale is None:
        return None
    return parsed.value * scale


def _same_expression(a: Any, b: Any) -> bool:
    left = str(a).replace(" ", "").lower()
    right = str(b).replace(" ", "").lower()
    if left == right:
        return True
    left_mm = _to_mm(a)
    right_mm = _to_mm(b)
    if left_mm is None or right_mm is None:
        return False
    return abs(left_mm - right_mm) <= 1e-9


def _variable_dict(variable_manager: Any, attr: str) -> dict[str, str]:
    data = _safe(lambda: getattr(variable_manager, attr))
    if isinstance(data, dict):
        return {str(key): str(value) for key, value in data.items()}
    return {}


def _schematic_components(editor: Any) -> list[str]:
    components = _safe(lambda: list(editor.GetAllComponents()))
    if not isinstance(components, list):
        return []
    return [str(component) for component in components]


def _component_server_by_id(editor: Any, component_id: str, components: list[str]) -> str | None:
    marker = f";{component_id};"
    for component in components:
        if marker in component:
            return component
    for component in components:
        comp_id = _safe(lambda component=component: editor.GetPropertyValue("ComponentTab", component, "ID"))
        if str(comp_id) == str(component_id):
            return component
    if len(components) == 1:
        return components[0]
    return None


def _tab_values(editor: Any, tab: str, server: str) -> dict[str, str]:
    props = _safe(lambda: list(editor.GetProperties(tab, server)))
    if not isinstance(props, (list, tuple)):
        return {}
    values: dict[str, str] = {}
    for prop in props:
        values[str(prop)] = str(_safe(lambda prop=prop: editor.GetPropertyValue(tab, server, prop)))
    return values


def _read_instance_parameters(layout_app: Any, component_id: str) -> dict[str, Any]:
    schematic = layout_app.odesign.SetActiveEditor("SchematicEditor")
    components = _schematic_components(schematic)
    server = _component_server_by_id(schematic, component_id, components)
    payload: dict[str, Any] = {
        "component_id": component_id,
        "schematic_components": components,
        "schematic_server": server,
    }
    if server is None:
        payload["status"] = "component_not_found"
        return payload
    payload["component_tab"] = _tab_values(schematic, "ComponentTab", server)
    payload["passed_parameters"] = _tab_values(schematic, "PassedParameterTab", server)
    effective_component_id = payload["component_tab"].get("ID") or component_id
    payload["effective_component_id"] = effective_component_id

    layout = layout_app.odesign.SetActiveEditor("Layout")
    payload["layout_info"] = [str(item) for item in _safe(lambda: layout.GetComponentInfo(effective_component_id)) or []]
    payload["layout_base"] = _tab_values(layout, "BaseElementTab", effective_component_id)
    payload["status"] = "inspected"
    return payload


def _bbox_for_object(source_app: Any, name: str) -> dict[str, Any]:
    if name not in source_app.modeler.object_names:
        return {"status": "missing"}
    obj = source_app.modeler[name]
    bbox = [float(item) for item in obj.bounding_box]
    return {
        "status": "inspected",
        "bbox_mm": bbox,
        "size_mm": [bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]],
        "center_mm": [(bbox[0] + bbox[3]) / 2.0, (bbox[1] + bbox[4]) / 2.0, (bbox[2] + bbox[5]) / 2.0],
        "material": str(getattr(obj, "material_name", "")),
        "solve_inside": str(getattr(obj, "solve_inside", "")),
    }


def _compare_variables(
    *,
    variable_names: list[str],
    source_variables: dict[str, str],
    project_variables: dict[str, str],
    instance_parameters: dict[str, str],
    project_prefix: str,
) -> list[dict[str, Any]]:
    rows = []
    for name in variable_names:
        project_name = f"{project_prefix}{name}"
        source_value = source_variables.get(name)
        project_value = project_variables.get(project_name)
        instance_value = instance_parameters.get(name)
        row = {
            "name": name,
            "source_value": source_value,
            "project_variable": project_name,
            "project_value": project_value,
            "instance_value": instance_value,
            "source_vs_project": None if project_value is None or source_value is None else _same_expression(source_value, project_value),
            "source_vs_instance": None if instance_value is None or source_value is None else _same_expression(source_value, instance_value),
        }
        row["status"] = "ok"
        if source_value is None:
            row["status"] = "missing_source"
        elif instance_value is None:
            row["status"] = "missing_instance"
        elif not row["source_vs_instance"]:
            row["status"] = "instance_mismatch"
        elif project_value is None:
            row["status"] = "missing_project"
        elif not row["source_vs_project"]:
            row["status"] = "project_mismatch"
        rows.append(row)
    return rows


def _geometry_checks(source_variables: dict[str, str], bboxes: dict[str, dict[str, Any]], tolerance_mm: float) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    pin_d_mm = _to_mm(source_variables.get("Pin_D", ""))
    hole_d_mm = _to_mm(source_variables.get("Hole_D", ""))

    pin = bboxes.get("Pin", {})
    if pin.get("status") == "inspected":
        size = pin.get("size_mm", [])
        pin_y = float(size[1])
        pin_z = float(size[2])
        expected = pin_d_mm
        actual = max(pin_y, pin_z)
        checks.append(
            {
                "name": "Pin diameter from bbox",
                "object": "Pin",
                "expected_variable": "Pin_D",
                "expected_mm": expected,
                "actual_y_mm": pin_y,
                "actual_z_mm": pin_z,
                "actual_max_mm": actual,
                "tolerance_mm": tolerance_mm,
                "matches_pin_d": expected is not None and abs(actual - expected) <= tolerance_mm,
                "matches_hole_d": hole_d_mm is not None and abs(actual - hole_d_mm) <= tolerance_mm,
            }
        )

    solder = bboxes.get("Solder_S", {})
    if solder.get("status") == "inspected":
        size = solder.get("size_mm", [])
        solder_y = float(size[1])
        checks.append(
            {
                "name": "Solder width from bbox",
                "object": "Solder_S",
                "expected_variable": "Pin_D",
                "expected_mm": pin_d_mm,
                "actual_y_mm": solder_y,
                "tolerance_mm": tolerance_mm,
                "matches_pin_d": pin_d_mm is not None and abs(solder_y - pin_d_mm) <= tolerance_mm,
            }
        )
    return checks


def _sync_project_variables(source_app: Any, source_variables: dict[str, str], variable_names: list[str], project_prefix: str) -> list[dict[str, Any]]:
    rows = []
    for name in variable_names:
        value = source_variables.get(name)
        if value is None:
            rows.append({"name": name, "status": "missing_source"})
            continue
        project_name = f"{project_prefix}{name}"
        result = source_app.variable_manager.set_variable(project_name, expression=value)
        rows.append({"name": name, "project_variable": project_name, "value": value, "result": bool(result)})
    return rows


def audit(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss, Hfss3dLayout

    variable_names = args.variable or list(DEFAULT_VARIABLES)
    bbox_names = args.bbox_object or ["Pin", "Solder_S", "Base_GND", "PTFE_CYL"]
    payload: dict[str, Any] = {
        "project": str(args.project),
        "source_design": args.source_design,
        "layout_design": args.layout_design,
        "component_id": args.component_id,
        "project_prefix": args.project_prefix,
        "variables_requested": variable_names,
        "bbox_objects_requested": bbox_names,
        "execute": args.execute,
        "sync_project_variables": args.sync_project_variables,
        "save": args.save,
    }

    source_app = Hfss(
        project=str(args.project),
        design=args.source_design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        source_vm = source_app.variable_manager
        source_variables = _variable_dict(source_vm, "design_variables") or _variable_dict(source_vm, "variables")
        project_variables = _variable_dict(source_vm, "project_variables")
        payload["source"] = {
            "model_units": str(source_app.modeler.model_units),
            "design_variables": source_variables,
            "project_variables": project_variables,
            "object_names": [str(item) for item in source_app.modeler.object_names],
            "bbox": {name: _bbox_for_object(source_app, name) for name in bbox_names},
        }
        if args.sync_project_variables:
            if args.execute:
                payload["project_variable_sync"] = _sync_project_variables(
                    source_app, source_variables, variable_names, args.project_prefix
                )
                if args.save:
                    payload["source_save_result"] = bool(source_app.save_project(str(args.project), overwrite=True))
                project_variables = _variable_dict(source_vm, "project_variables")
                payload["source"]["project_variables_after_sync"] = project_variables
            else:
                payload["project_variable_sync"] = [
                    {
                        "name": name,
                        "project_variable": f"{args.project_prefix}{name}",
                        "value": source_variables.get(name),
                        "status": "dry_run",
                    }
                    for name in variable_names
                ]
    finally:
        source_app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)

    layout_app = Hfss3dLayout(
        project=str(args.project),
        design=args.layout_design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        instance = _read_instance_parameters(layout_app, args.component_id)
        payload["layout_instance"] = instance
    finally:
        layout_app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)

    instance_parameters = payload.get("layout_instance", {}).get("passed_parameters", {})
    if not isinstance(instance_parameters, dict):
        instance_parameters = {}
    comparisons = _compare_variables(
        variable_names=variable_names,
        source_variables=source_variables,
        project_variables=project_variables,
        instance_parameters=instance_parameters,
        project_prefix=args.project_prefix,
    )
    geometry = _geometry_checks(source_variables, payload["source"]["bbox"], args.tolerance_mm)
    payload["comparisons"] = comparisons
    payload["geometry_checks"] = geometry

    hard_failures = [
        row
        for row in comparisons
        if row["status"] in {"missing_source", "missing_instance", "instance_mismatch", "project_mismatch"}
    ]
    geometry_failures = [
        row
        for row in geometry
        if row.get("matches_pin_d") is False and row.get("name") in {"Pin diameter from bbox", "Solder width from bbox"}
    ]
    missing_project = [row for row in comparisons if row["status"] == "missing_project"]
    if hard_failures or geometry_failures:
        status = "fail"
    elif missing_project:
        status = "warn_missing_project_variables"
    else:
        status = "ok"
    payload["summary"] = {
        "status": status,
        "hard_failure_count": len(hard_failures),
        "missing_project_variable_count": len(missing_project),
        "geometry_failure_count": len(geometry_failures),
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit HFSS connector source/project/instance parameters.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--source-design", required=True)
    parser.add_argument("--layout-design", required=True)
    parser.add_argument("--component-id", default="70")
    parser.add_argument("--project-prefix", default="$sma_")
    parser.add_argument("--variable", action="append", default=None, help="Variable name to audit. Repeatable.")
    parser.add_argument("--bbox-object", action="append", default=None, help="Source object bbox to audit. Repeatable.")
    parser.add_argument("--tolerance-mm", type=float, default=0.02)
    parser.add_argument("--sync-project-variables", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--new-desktop", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = audit(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 1 if payload.get("summary", {}).get("status") == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
