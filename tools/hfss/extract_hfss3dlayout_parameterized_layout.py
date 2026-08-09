#!/usr/bin/env python3
"""Extract a HFSS 3D Layout design through AEDT/PyAEDT APIs.

This is a read-only engineering tool. It does not parse, modify, or write AEDT
project files directly. Geometry is collected from PyAEDT primitive wrappers and
the AEDT layout editor property APIs.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.common import json_default
from simads.hfss.aedt_startup import OperationLifecycle
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session


_UNIT_TO_MM = {
    "mm": 1.0,
    "mil": 0.0254,
    "in": 25.4,
    "inch": 25.4,
    "um": 0.001,
    "micron": 0.001,
    "m": 1000.0,
}
_NUMBER_UNIT_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*([A-Za-z]*)\s*$")
_MISSING = object()


def _safe(call, default: Any = _MISSING) -> Any:
    try:
        return call()
    except Exception as exc:  # pragma: no cover - AEDT API dependent.
        if default is not _MISSING:
            return default
        return {"error": f"{type(exc).__name__}: {exc}"}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    try:
        return list(value)
    except Exception:
        return [value]


def _parse_mm(value: Any, *, default_unit: str = "mm", numeric_unit: str | None = None) -> float | None:
    raw = getattr(value, "value", value)
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        unit = (numeric_unit or default_unit).lower()
        scale = _UNIT_TO_MM.get(unit)
        if scale is None:
            return None
        return float(raw) * scale
    text = str(raw).strip()
    if not text:
        return None
    match = _NUMBER_UNIT_RE.match(text)
    if not match:
        return None
    number = float(match.group(1))
    unit = (match.group(2) or default_unit).lower()
    scale = _UNIT_TO_MM.get(unit)
    if scale is None:
        return None
    return number * scale


def _point_mm(value: Any, *, default_unit: str = "mm", numeric_unit: str | None = None) -> list[float | None]:
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
    else:
        parts = _as_list(value)
    return [_parse_mm(part, default_unit=default_unit, numeric_unit=numeric_unit) for part in parts]


def _bbox_mm(value: Any, *, numeric_unit: str = "m", default_unit: str = "mm") -> list[float] | None:
    items = _as_list(value)
    if len(items) < 4:
        return None
    values = [_parse_mm(item, default_unit=default_unit, numeric_unit=numeric_unit) for item in items[:4]]
    if any(item is None for item in values):
        return None
    return [float(item) for item in values if item is not None]


def _bbox_from_points(points: list[list[float | None]]) -> list[float] | None:
    xs = [float(point[0]) for point in points if len(point) >= 2 and point[0] is not None and point[1] is not None]
    ys = [float(point[1]) for point in points if len(point) >= 2 and point[0] is not None and point[1] is not None]
    if not xs or not ys:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def _bbox_size(bbox: list[float] | None) -> dict[str, float] | None:
    if not bbox or len(bbox) < 4:
        return None
    return {"w_mm": bbox[2] - bbox[0], "h_mm": bbox[3] - bbox[1]}


def _center_from_bbox(bbox: list[float] | None) -> list[float] | None:
    if not bbox or len(bbox) < 4:
        return None
    return [(bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0]


def _polyline_length(points: list[list[float | None]]) -> float | None:
    clean = [
        (float(point[0]), float(point[1]))
        for point in points
        if len(point) >= 2 and point[0] is not None and point[1] is not None
    ]
    if len(clean) < 2:
        return None
    total = 0.0
    for (x0, y0), (x1, y1) in zip(clean, clean[1:]):
        total += math.hypot(x1 - x0, y1 - y0)
    return total


def _read_properties(editor: Any, server: str, *, tab: str = "BaseElementTab") -> dict[str, Any]:
    props = _safe(lambda: list(editor.GetProperties(tab, server)), default=[])
    values: dict[str, Any] = {}
    for prop in props:
        name = str(prop)
        values[name] = _safe(lambda name=name: editor.GetPropertyValue(tab, server, name))
    return values


def _property_subset(props: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "Name",
        "Type",
        "Net",
        "Layer",
        "PlacementLayer",
        "Location",
        "Pt",
        "Pt A",
        "Pt B",
        "Center",
        "Width",
        "Height",
        "LineWidth",
        "TotalLength",
        "HoleDiameter",
        "Padstack",
        "Start Layer",
        "Stop Layer",
        "Angle",
        "Rotation Angle",
        "Component Name",
    )
    return {key: value for key, value in props.items() if key in keep or key.startswith("Pt") or key.startswith("ArcHeight")}


def _property_value_mm(props: dict[str, Any], key: str, *, default_unit: str) -> list[float] | None:
    value = props.get(key)
    if value is None:
        return None
    parsed = _point_mm(value, default_unit=default_unit)
    if len(parsed) < 2 or parsed[0] is None or parsed[1] is None:
        return None
    return [float(parsed[0]), float(parsed[1])]


def _read_primitive(app: Any, editor: Any, name: str, layer_query: str | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"name": name}
    if layer_query is not None:
        record["layer_query"] = layer_query
    primitive = _safe(lambda: app.modeler[name], default=None)
    record["primitive_found"] = primitive is not None
    props = _read_properties(editor, name)
    if props:
        record["properties"] = _property_subset(props)
    model_units = str(_safe(lambda: app.modeler.model_units, default="mm") or "mm")
    if primitive is None:
        record["type"] = props.get("Type")
        record["net"] = props.get("Net")
        record["layer"] = props.get("PlacementLayer") or props.get("Start Layer") or layer_query
        location_mm = _property_value_mm(props, "Location", default_unit=model_units)
        if location_mm is not None:
            record["location_mm"] = location_mm
        return record

    for attr in ("prim_type", "name", "net_name", "placement_layer", "layer_name", "is_void", "negative"):
        value = _safe(lambda attr=attr: getattr(primitive, attr))
        if isinstance(value, dict) and "error" in value:
            continue
        record[attr] = value() if callable(value) else value

    object_units = str(_safe(lambda: primitive.object_units, default=model_units) or model_units)
    record["object_units"] = object_units
    record["type"] = str(record.get("prim_type") or props.get("Type") or "").strip() or None
    record["net"] = str(record.get("net_name") or props.get("Net") or "").strip() or None
    record["layer"] = str(record.get("placement_layer") or props.get("Layer") or layer_query or "").strip() or None
    location_mm = _property_value_mm(props, "Location", default_unit=object_units)
    if location_mm is not None:
        record["location_mm"] = location_mm

    point_records: list[list[float | None]] = []
    raw_points = _safe(lambda: primitive.points, default=[])
    for point in _as_list(raw_points):
        position = _safe(lambda point=point: point.position, default=None)
        if position is not None:
            point_records.append(_point_mm(position, numeric_unit="m"))
    if point_records:
        record["points_mm"] = point_records

    center_line = _safe(lambda: primitive.center_line, default=None)
    if isinstance(center_line, dict):
        record["center_line"] = center_line
        line_points = [
            _point_mm(value, default_unit=object_units)
            for key, value in sorted(center_line.items())
            if str(key).startswith("Pt")
        ]
        if line_points:
            record["center_line_points_mm"] = line_points

    for attr in (
        "width",
        "height",
        "length",
        "center",
        "point_a",
        "point_b",
        "corner_radius",
        "bend_type",
        "start_cap_type",
        "end_cap_type",
        "obounding_box",
    ):
        value = _safe(lambda attr=attr: getattr(primitive, attr), default=None)
        if value is not None:
            record[attr] = value

    if record.get("width") is not None:
        record["width_mm"] = _parse_mm(record["width"])
    if record.get("height") is not None:
        record["height_mm"] = _parse_mm(record["height"])
    if record.get("length") is not None:
        record["length_mm"] = _parse_mm(record["length"])
    if record.get("center") is not None:
        record["center_mm"] = _point_mm(record["center"], default_unit=object_units)
    if record.get("point_a") is not None:
        record["point_a_mm"] = _point_mm(record["point_a"], default_unit=object_units)
    if record.get("point_b") is not None:
        record["point_b_mm"] = _point_mm(record["point_b"], default_unit=object_units)
    if record.get("center_mm") is None and record.get("location_mm") is not None:
        record["center_mm"] = record["location_mm"]

    bbox = _bbox_mm(record.get("obounding_box"), numeric_unit="m")
    if bbox is None:
        bbox = _bbox_from_points(record.get("points_mm", []))
    if bbox is None:
        bbox = _bbox_from_points(record.get("center_line_points_mm", []))
    if bbox is None and record.get("point_a_mm") and record.get("point_b_mm"):
        bbox = _bbox_from_points([record["point_a_mm"], record["point_b_mm"]])
    if bbox is None and record.get("center_mm") and record.get("width_mm") is not None and record.get("height_mm") is not None:
        cx, cy = record["center_mm"][:2]
        if cx is not None and cy is not None:
            w = float(record["width_mm"])
            h = float(record["height_mm"])
            bbox = [float(cx) - w / 2.0, float(cy) - h / 2.0, float(cx) + w / 2.0, float(cy) + h / 2.0]
    record["bbox_mm"] = bbox
    record["center_from_bbox_mm"] = _center_from_bbox(bbox)
    record["size_from_bbox_mm"] = _bbox_size(bbox)
    if "center_line_points_mm" in record and record.get("length_mm") is None:
        record["length_from_points_mm"] = _polyline_length(record["center_line_points_mm"])
    return record


def _read_component(editor: Any, comp_id_or_name: str) -> dict[str, Any]:
    record: dict[str, Any] = {"id_or_name": comp_id_or_name}
    record["properties"] = {
        "BaseElementTab": _property_subset(_read_properties(editor, comp_id_or_name, tab="BaseElementTab")),
        "ComponentTab": _property_subset(_read_properties(editor, comp_id_or_name, tab="ComponentTab")),
    }
    record["component_info"] = _safe(lambda: [str(item) for item in editor.GetComponentInfo(comp_id_or_name)], default=[])
    record["pins"] = _safe(lambda: [str(item) for item in editor.GetComponentPins(comp_id_or_name)], default=[])
    pin_info: dict[str, Any] = {}
    for pin in record["pins"]:
        pin_info[pin] = _safe(lambda pin=pin: [str(item) for item in editor.GetComponentPinInfo(comp_id_or_name, pin)])
    if pin_info:
        record["pin_info"] = pin_info
    return record


def _read_modeler_components(app: Any) -> dict[str, Any]:
    model_units = str(_safe(lambda: app.modeler.model_units, default="mm") or "mm")
    components = _safe(lambda: app.modeler.components, default={})
    if not isinstance(components, dict):
        return {}
    records: dict[str, Any] = {}
    for name, component in components.items():
        record: dict[str, Any] = {
            "name": str(name),
            "part": _safe(lambda component=component: getattr(component, "part"), default=None),
            "part_type": _safe(lambda component=component: getattr(component, "part_type"), default=None),
            "placement_layer": _safe(lambda component=component: getattr(component, "placement_layer"), default=None),
            "net_name": _safe(lambda component=component: getattr(component, "net_name"), default=None),
        }
        location = _safe(lambda component=component: getattr(component, "location"), default=None)
        record["location"] = location
        record["location_mm"] = _point_mm(location, default_unit=model_units)
        bbox = _safe(lambda component=component: getattr(component, "bounding_box"), default=None)
        record["bounding_box"] = bbox
        record["bbox_mm"] = _bbox_mm(bbox, numeric_unit=model_units, default_unit=model_units)
        pins = _safe(lambda component=component: getattr(component, "pins"), default={})
        pin_records: dict[str, Any] = {}
        if isinstance(pins, dict):
            for pin_name, pin in pins.items():
                pin_record: dict[str, Any] = {
                    "name": str(pin_name),
                    "net": _safe(lambda pin=pin: getattr(pin, "net_name"), default=None),
                    "start_layer": _safe(lambda pin=pin: getattr(pin, "start_layer"), default=None),
                    "stop_layer": _safe(lambda pin=pin: getattr(pin, "stop_layer"), default=None),
                    "placement_layer": _safe(lambda pin=pin: getattr(pin, "placement_layer"), default=None),
                    "hole_diameter": _safe(lambda pin=pin: getattr(pin, "holediam"), default=None),
                    "component_name": _safe(lambda pin=pin: getattr(pin, "componentname"), default=None),
                }
                pin_location = _safe(lambda pin=pin: getattr(pin, "location"), default=None)
                pin_record["location"] = pin_location
                pin_record["location_mm"] = _point_mm(pin_location, default_unit=model_units)
                pin_bbox = _safe(lambda pin=pin: getattr(pin, "bounding_box"), default=None)
                pin_record["bounding_box"] = pin_bbox
                pin_record["bbox_mm"] = _bbox_mm(pin_bbox, numeric_unit=model_units, default_unit=model_units)
                pin_records[str(pin_name)] = pin_record
        record["pins"] = pin_records
        records[str(name)] = record
    return records


def _component_names_by_id(editor: Any, *, limit: int = 3000) -> dict[str, list[str]]:
    components: dict[str, list[str]] = {}
    for idx in range(1, limit):
        comp_id = str(idx)
        info = _safe(lambda comp_id=comp_id: editor.GetComponentInfo(comp_id), default=[])
        if not info:
            continue
        component_name = None
        for item in info:
            text = str(item)
            if text.startswith("ComponentName="):
                component_name = text.split("=", 1)[1]
                break
        components.setdefault(component_name or "<unknown>", []).append(comp_id)
    return components


def _read_layers(app: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for owner in ("modeler",):
        layers = _safe(lambda owner=owner: getattr(getattr(app, owner), "layers"), default=None)
        if layers is None:
            continue
        payload[f"{owner}.all_layers"] = _safe(lambda layers=layers: list(layers.all_layers), default=[])
        layer_map = {}
        raw_layers = _safe(lambda layers=layers: dict(getattr(layers, "layers")), default={})
        for key, layer in raw_layers.items():
            layer_map[str(key)] = {
                "name": _safe(lambda layer=layer: getattr(layer, "name"), default=None),
                "type": _safe(lambda layer=layer: getattr(layer, "type"), default=None),
                "thickness": _safe(lambda layer=layer: getattr(layer, "thickness"), default=None),
                "elevation": _safe(lambda layer=layer: getattr(layer, "elevation"), default=None),
                "material": _safe(lambda layer=layer: getattr(layer, "material"), default=None),
            }
        payload[f"{owner}.layers"] = layer_map
    return payload


def _read_variables(app: Any) -> dict[str, Any]:
    manager = _safe(lambda: app.variable_manager, default=None)
    if manager is None:
        return {"available": False, "reason": "variable_manager_unavailable"}
    payload: dict[str, Any] = {"available": True}
    for attr in ("variables", "project_variables", "design_variables"):
        values = _safe(lambda attr=attr: getattr(manager, attr), default=None)
        if values is None:
            continue
        if isinstance(values, dict):
            records: dict[str, Any] = {}
            for name, variable in values.items():
                records[str(name)] = {
                    "expression": _safe(lambda variable=variable: variable.expression, default=None),
                    "evaluated_value": _safe(lambda variable=variable: variable.evaluated_value, default=None),
                    "is_independent": _safe(lambda variable=variable: variable.is_independent, default=None),
                    "post_processing": _safe(lambda variable=variable: variable.post_processing, default=None),
                }
            payload[attr] = records
        else:
            payload[attr] = values
    return payload


def _names_by_layer(app: Any, layers: list[str]) -> dict[str, list[str]]:
    by_layer: dict[str, list[str]] = {}
    for layer in layers:
        names = _safe(lambda layer=layer: [str(item) for item in app.modeler.objects_by_layer(layer, include_voids=True)], default=[])
        if not names:
            names = _safe(lambda layer=layer: [str(item) for item in app.modeler.objects_by_layer(layer)], default=[])
        by_layer[layer] = names
    return by_layer


def _distill(payload: dict[str, Any], *, signal_nets: list[str]) -> dict[str, Any]:
    objects = payload.get("objects", [])
    signal_set = {net.lower() for net in signal_nets}
    signal_objects = [obj for obj in objects if str(obj.get("net") or "").lower() in signal_set]
    gnd_objects = [obj for obj in objects if str(obj.get("net") or "").lower() == "gnd"]
    void_objects = [
        obj
        for obj in objects
        if bool(obj.get("is_void")) or "void" in str(obj.get("type") or "").lower() or str(obj.get("negative")).lower() == "true"
    ]
    signal_bbox = _merge_bboxes([obj.get("bbox_mm") for obj in signal_objects])
    void_bbox = _merge_bboxes([obj.get("bbox_mm") for obj in void_objects])
    unique_gnd: dict[str, dict[str, Any]] = {}
    for obj in gnd_objects:
        unique_gnd.setdefault(str(obj.get("name")), obj)
    via_objects = [
        obj
        for obj in unique_gnd.values()
        if str(obj.get("type") or obj.get("name") or "").lower().startswith("via")
        or str(obj.get("name") or "").lower().startswith("via")
    ]
    if signal_bbox:
        for obj in via_objects:
            location = obj.get("location_mm") or obj.get("center_mm")
            if isinstance(location, list) and len(location) >= 2:
                obj["_distance_to_signal_bbox_mm"] = _distance_to_bbox(location, signal_bbox)
        via_objects.sort(key=lambda obj: float(obj.get("_distance_to_signal_bbox_mm", float("inf"))))
    return {
        "project": payload.get("project"),
        "design": payload.get("design"),
        "ports": payload.get("ports"),
        "signal_nets": signal_nets,
        "signal_object_count": len(signal_objects),
        "signal_bbox_mm": signal_bbox,
        "signal_bbox_size_mm": _bbox_size(signal_bbox),
        "void_object_count": len(void_objects),
        "void_bbox_mm": void_bbox,
        "gnd_via_count": len(via_objects),
        "components": payload.get("components", {}),
        "signal_objects": _compact_objects(signal_objects),
        "void_objects": _compact_objects(void_objects),
        "nearby_gnd_via_candidates": _compact_objects(via_objects[:80]),
        "api_limits": payload.get("api_limits", []),
    }


def _merge_bboxes(bboxes: list[Any]) -> list[float] | None:
    valid = [bbox for bbox in bboxes if isinstance(bbox, list) and len(bbox) >= 4 and all(isinstance(v, (int, float)) for v in bbox[:4])]
    if not valid:
        return None
    return [
        min(float(bbox[0]) for bbox in valid),
        min(float(bbox[1]) for bbox in valid),
        max(float(bbox[2]) for bbox in valid),
        max(float(bbox[3]) for bbox in valid),
    ]


def _compact_objects(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact = []
    for obj in objects:
        compact.append(
            {
                "name": obj.get("name"),
                "type": obj.get("type"),
                "layer": obj.get("layer"),
                "net": obj.get("net"),
                "bbox_mm": obj.get("bbox_mm"),
                "size_from_bbox_mm": obj.get("size_from_bbox_mm"),
                "center_from_bbox_mm": obj.get("center_from_bbox_mm"),
                "location_mm": obj.get("location_mm") or obj.get("center_mm"),
                "distance_to_signal_bbox_mm": obj.get("_distance_to_signal_bbox_mm"),
                "width_mm": obj.get("width_mm"),
                "length_mm": obj.get("length_mm") or obj.get("length_from_points_mm"),
                "points_mm": obj.get("points_mm"),
                "center_line_points_mm": obj.get("center_line_points_mm"),
            }
        )
    return compact


def _distance_to_bbox(point: list[float], bbox: list[float]) -> float:
    x, y = float(point[0]), float(point[1])
    dx = max(bbox[0] - x, 0.0, x - bbox[2])
    dy = max(bbox[1] - y, 0.0, y - bbox[3])
    return math.hypot(dx, dy)


def extract(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle("extract_hfss3dlayout_parameterized_layout", output=args.events)
    config = Hfss3dLayoutSessionConfig(
        label="extract_hfss3dlayout_parameterized_layout",
        project=args.project,
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        remove_lock=args.remove_lock,
        close_projects=args.close_projects,
        close_desktop=args.close_desktop,
        keep_open=args.keep_open,
        ready_setup=args.setup,
        ready_sweep=args.sweep,
        ready_timeout_s=args.ready_timeout_s,
        force_remove_project_lock=args.force_remove_project_lock,
    )
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "api_contract": "AEDT/PyAEDT read-only; no direct .aedt/.aedb parsing or editing",
        "layers_requested": args.layer,
        "signal_nets": args.signal_net,
    }
    status = "ok"
    try:
        with open_hfss3dlayout_session(config, lifecycle) as session:
            app = session.app
            editor = app.odesign.SetActiveEditor("Layout")
            payload.update(session.metadata())
            payload["model_units"] = _safe(lambda: app.modeler.model_units, default=None)
            payload["variables"] = _read_variables(app)
            payload["ports"] = _safe(lambda: list(getattr(app, "port_list", [])), default=[])
            payload["layers"] = _read_layers(app)
            layer_names = args.layer or ["TOP", "L2_GND", "L3_SIG", "BOTTOM"]
            names_by_layer = _names_by_layer(app, layer_names)
            payload["names_by_layer"] = names_by_layer
            seen: set[str] = set()
            objects: list[dict[str, Any]] = []
            for layer, names in names_by_layer.items():
                for name in names:
                    key = f"{layer}:{name}"
                    if key in seen:
                        continue
                    seen.add(key)
                    if args.focus_name and not any(token.lower() in name.lower() for token in args.focus_name):
                        primitive = _safe(lambda name=name: app.modeler[name], default=None)
                        net = _safe(lambda primitive=primitive: getattr(primitive, "net_name"), default=None) if primitive else None
                        if str(net or "").lower() not in {item.lower() for item in args.signal_net}:
                            continue
                    objects.append(_read_primitive(app, editor, name, layer))
            payload["objects"] = objects
            payload["modeler_components"] = _read_modeler_components(app)
            components_by_name = _component_names_by_id(editor)
            payload["components_by_name"] = components_by_name
            selected_component_ids: list[str] = []
            for comp_name in args.component_name:
                selected_component_ids.extend(components_by_name.get(comp_name, []))
            for comp_id in args.component_id:
                selected_component_ids.append(comp_id)
            if not args.component_name and not args.component_id:
                for comp_name, ids in components_by_name.items():
                    if comp_name.startswith("RF") or comp_name.startswith("U"):
                        selected_component_ids.extend(ids)
            selected_component_ids = list(dict.fromkeys(selected_component_ids))
            if not selected_component_ids:
                selected_component_ids = [comp_id for ids in components_by_name.values() for comp_id in ids]
            payload["components"] = {comp_id: _read_component(editor, comp_id) for comp_id in selected_component_ids}
            if not any(obj.get("bbox_mm") for obj in objects):
                payload.setdefault("api_limits", []).append(
                    "No primitive point/bbox geometry was exposed by the current 3D Layout gRPC API for selected objects."
                )
            payload["distilled"] = _distill(payload, signal_nets=args.signal_net)
    except Exception as exc:
        status = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        raise
    finally:
        payload["lifecycle"] = lifecycle.finish(status=status)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract HFSS 3D Layout layout primitives through AEDT/PyAEDT APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--setup", default=None)
    parser.add_argument("--sweep", default=None)
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--signal-net", action="append", default=[])
    parser.add_argument("--focus-name", action="append", default=[])
    parser.add_argument("--component-name", action="append", default=[])
    parser.add_argument("--component-id", action="append", default=[])
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--force-remove-project-lock", action="store_true")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--close-projects", action="store_true", default=True)
    parser.add_argument("--keep-projects-open", action="store_false", dest="close_projects")
    parser.add_argument("--close-desktop", action="store_true", default=True)
    parser.add_argument("--keep-desktop-open", action="store_false", dest="close_desktop")
    parser.add_argument("--ready-timeout-s", type=float, default=180.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--distilled-output", type=Path, default=None)
    parser.add_argument("--events", type=Path, default=Path(".simads/sp8t/extract_hfss3dlayout_parameterized_layout_events.jsonl"))
    parser.add_argument("--print-mode", choices=("full", "distilled", "none"), default="distilled")
    args = parser.parse_args()
    if not args.signal_net:
        args.signal_net = ["N00061"]
    return args


def main() -> int:
    args = parse_args()
    payload = extract(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + "\n", encoding="utf-8")
    if args.distilled_output is not None:
        args.distilled_output.parent.mkdir(parents=True, exist_ok=True)
        distilled = json.dumps(payload.get("distilled", {}), ensure_ascii=False, indent=2, default=json_default)
        args.distilled_output.write_text(distilled + "\n", encoding="utf-8")
    if args.print_mode == "full":
        print(text)
    elif args.print_mode == "distilled":
        print(json.dumps(payload.get("distilled", {}), ensure_ascii=False, indent=2, default=json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
