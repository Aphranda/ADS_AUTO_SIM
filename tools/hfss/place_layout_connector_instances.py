#!/usr/bin/env python3
"""Place HFSS connector design instances in an HFSS 3D Layout design.

The current SMA workflow uses a single AEDT project with multiple fixture
designs. Connector models can be copied from an HFSS design and pasted into a
3D Layout design as subcircuit components, then positioned on the CPWG launch
ports. This script keeps that operation explicit and dry-run by default.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any


@dataclass(frozen=True)
class PlacementTarget:
    side: str
    x_mm: float
    y_mm: float
    z_mm: float
    angle_deg: float
    component_name: str | None
    component_id: str | None


def _json_default(value: Any) -> str:
    return str(value)


def _load_layout(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout must be a JSON object: {path}")
    return data


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return data


def _connector_placement_config(args: argparse.Namespace) -> dict[str, Any]:
    if args.project_config is None:
        return {}
    project_config = _load_json_object(args.project_config)
    hfss = project_config.get("hfss", {})
    if not isinstance(hfss, dict):
        return {}
    placement = hfss.get("connector_placement", {})
    if not isinstance(placement, dict):
        return {}
    profiles = placement.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    profile_name = args.connector_placement_profile or placement.get("default_profile")
    if not profile_name:
        return {}
    profile = profiles.get(str(profile_name), {})
    if not isinstance(profile, dict):
        raise ValueError(f"missing connector placement profile {profile_name!r} in {args.project_config}")
    args.connector_placement_profile = str(profile_name)
    return profile


def _apply_connector_placement_config(args: argparse.Namespace) -> None:
    profile = _connector_placement_config(args)
    mapping = {
        "source_project": "source_project",
        "source_design": "source_design",
        "connector_model": "source_design",
        "p1_component_name": "p1_component_name",
        "p2_component_name": "p2_component_name",
        "p1_component_id": "p1_component_id",
        "p2_component_id": "p2_component_id",
        "p1_offset_x_mm": "p1_offset_x_mm",
        "p1_offset_y_mm": "p1_offset_y_mm",
        "p2_offset_x_mm": "p2_offset_x_mm",
        "p2_offset_y_mm": "p2_offset_y_mm",
        "p1_angle_deg": "p1_angle_deg",
        "p2_angle_deg": "p2_angle_deg",
        "p1_solder_offset_x_mm": "p1_solder_offset_x_mm",
        "p1_solder_offset_y_mm": "p1_solder_offset_y_mm",
        "p2_solder_offset_x_mm": "p2_solder_offset_x_mm",
        "p2_solder_offset_y_mm": "p2_solder_offset_y_mm",
        "z_mode": "z_mode",
        "z_mm": "z_mm",
        "pad_top_z_mm": "pad_top_z_mm",
        "solder_bottom_z_mm": "solder_bottom_z_mm",
        "solder_intrusion_mm": "solder_intrusion_mm",
        "solder_intrusion_mil": "solder_intrusion_mil",
        "force_3d_placement": "force_3d_placement",
        "local_origin": "local_origin",
        "rotation_axis": "rotation_axis",
    }
    for config_key, arg_name in mapping.items():
        if getattr(args, arg_name) is None and config_key in profile:
            value = profile[config_key]
            if arg_name in {"source_project"} and value is not None:
                value = Path(str(value))
            setattr(args, arg_name, value)


def _apply_fallback_defaults(args: argparse.Namespace) -> None:
    defaults = {
        "p1_offset_x_mm": 0.0,
        "p1_offset_y_mm": 0.0,
        "p2_offset_x_mm": 0.0,
        "p2_offset_y_mm": 0.0,
        "p1_angle_deg": 180.0,
        "p2_angle_deg": 0.0,
        "p1_solder_offset_x_mm": 0.0,
        "p1_solder_offset_y_mm": 0.0,
        "p2_solder_offset_x_mm": 0.0,
        "p2_solder_offset_y_mm": 0.0,
        "z_mode": "fixed",
        "z_mm": 0.0,
        "pad_top_z_mm": 0.0,
        "solder_bottom_z_mm": -0.5,
        "solder_intrusion_mm": 0.0,
        "solder_intrusion_mil": 5.0,
        "force_3d_placement": False,
        "source_design": "SMA_KE_Unite_solder",
    }
    for name, value in defaults.items():
        if getattr(args, name) is None:
            setattr(args, name, value)


def _load_layout_ports(data: dict[str, Any], path: Path) -> dict[str, tuple[float, float]]:
    ports = data.get("ports", [])
    if not isinstance(ports, list):
        raise ValueError(f"layout.ports must be a list: {path}")
    output: dict[str, tuple[float, float]] = {}
    for port in ports:
        if not isinstance(port, dict):
            continue
        name = str(port.get("name", "")).upper()
        if name in {"P1", "P2"}:
            output[name] = (float(port["x"]), float(port["y"]))
    missing = {"P1", "P2"} - set(output)
    if missing:
        raise ValueError(f"layout is missing ports {sorted(missing)}: {path}")
    return output


def _layout_parameters(data: dict[str, Any]) -> dict[str, Any]:
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        return {}
    params = metadata.get("parameters", {})
    return params if isinstance(params, dict) else {}


def _layout_total_len(data: dict[str, Any], ports: dict[str, tuple[float, float]]) -> float:
    metadata = data.get("metadata", {})
    if isinstance(metadata, dict) and metadata.get("total_len_mm") is not None:
        return float(metadata["total_len_mm"])
    return float(ports["P2"][0])


def _pad_centers_from_layout(data: dict[str, Any], path: Path) -> dict[str, tuple[float, float]]:
    ports = _load_layout_ports(data, path)
    params = _layout_parameters(data)
    pad_to_edge = float(params.get("pad_to_edge_mm", 0.0) or 0.0)
    pad_l = float(params.get("pin_pad_l_mm", 0.0) or 0.0)
    if pad_l <= 0.0:
        return ports
    total_len = _layout_total_len(data, ports)
    return {
        "P1": (pad_to_edge + pad_l / 2.0, ports["P1"][1]),
        "P2": (total_len - pad_to_edge - pad_l / 2.0, ports["P2"][1]),
    }


def _rotate_offset(x: float, y: float, angle_deg: float) -> tuple[float, float]:
    import math

    theta = math.radians(angle_deg)
    return x * math.cos(theta) - y * math.sin(theta), x * math.sin(theta) + y * math.cos(theta)


def _mil_to_mm(value: float) -> float:
    return value * 0.0254


def _placement_z_mm(args: argparse.Namespace) -> float:
    if args.z_mode == "fixed":
        return args.z_mm
    intrusion_mm = args.solder_intrusion_mm
    if args.solder_intrusion_mil is not None:
        intrusion_mm = _mil_to_mm(args.solder_intrusion_mil)
    # AEDT 3D Layout component placement uses the opposite sign from the
    # source HFSS model bbox for this pasted connector. A positive intrusion
    # should move the solder bottom slightly below the pad top.
    return args.pad_top_z_mm + intrusion_mm + args.solder_bottom_z_mm


def _targets_from_args(args: argparse.Namespace) -> list[PlacementTarget]:
    if args.layout:
        layout = _load_layout(args.layout)
        anchors = _pad_centers_from_layout(layout, args.layout) if args.anchor == "pad-center" else _load_layout_ports(layout, args.layout)
        p1_x, p1_y = anchors["P1"]
        p2_x, p2_y = anchors["P2"]
    else:
        p1_x, p1_y = args.p1_x_mm, args.p1_y_mm
        p2_x, p2_y = args.p2_x_mm, args.p2_y_mm

    p1_solder_dx, p1_solder_dy = _rotate_offset(args.p1_solder_offset_x_mm, args.p1_solder_offset_y_mm, args.p1_angle_deg)
    p2_solder_dx, p2_solder_dy = _rotate_offset(args.p2_solder_offset_x_mm, args.p2_solder_offset_y_mm, args.p2_angle_deg)
    z_mm = _placement_z_mm(args)

    p1 = PlacementTarget(
        side="P1",
        x_mm=p1_x + args.p1_offset_x_mm - p1_solder_dx,
        y_mm=p1_y + args.p1_offset_y_mm - p1_solder_dy,
        z_mm=z_mm,
        angle_deg=args.p1_angle_deg,
        component_name=args.p1_component_name,
        component_id=args.p1_component_id,
    )
    p2 = PlacementTarget(
        side="P2",
        x_mm=p2_x + args.p2_offset_x_mm - p2_solder_dx,
        y_mm=p2_y + args.p2_offset_y_mm - p2_solder_dy,
        z_mm=z_mm,
        angle_deg=args.p2_angle_deg,
        component_name=args.p2_component_name,
        component_id=args.p2_component_id,
    )
    if args.placement == "single":
        return [p1 if args.single_side == "P1" else p2]
    if args.placement == "dual":
        return [p1, p2]
    raise ValueError(f"unsupported placement mode: {args.placement}")


def _project_sidecars(project: Path) -> list[Path]:
    paths = [project]
    for suffix in [".aedb", ".aedtresults"]:
        sidecar = project.with_suffix(suffix)
        if sidecar.exists():
            paths.append(sidecar)
    return paths


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime_locks = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in _project_sidecars(project):
        dst = src.with_name(f"{src.stem}.before_connector_place_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _component_ids(editor: Any, *, limit: int = 1000) -> dict[str, list[str]]:
    components: dict[str, list[str]] = {}
    for idx in range(1, limit):
        name = str(idx)
        try:
            info = editor.GetComponentInfo(name)
        except Exception:
            continue
        if not info:
            continue
        component_name = None
        for item in info:
            text = str(item)
            if text.startswith("ComponentName="):
                component_name = text.split("=", 1)[1]
                break
        if component_name:
            components.setdefault(component_name, []).append(name)
    return components


def _read_component_properties(editor: Any, comp_id: str) -> dict[str, Any]:
    props: dict[str, Any] = {"id": comp_id}
    for prop in ["Component Name", "Location", "Angle", "Rotation Angle", "3D Placement", "Local Origin", "Layer"]:
        try:
            props[prop] = editor.GetPropertyValue("BaseElementTab", comp_id, prop)
        except Exception:
            pass
    try:
        props["component_info"] = [str(item) for item in editor.GetComponentInfo(comp_id)]
    except Exception:
        pass
    return props


def _resolve_existing_component(editor: Any, target: PlacementTarget, component_ids: dict[str, list[str]]) -> str:
    if target.component_id:
        return target.component_id
    if target.component_name:
        ids = component_ids.get(target.component_name, [])
        if not ids:
            raise RuntimeError(f"component {target.component_name!r} was not found in Layout")
        return sorted(ids, key=lambda item: int(item))[-1]
    all_ids = [item for ids in component_ids.values() for item in ids]
    if len(all_ids) == 1:
        return all_ids[0]
    raise RuntimeError(f"{target.side} requires --{target.side.lower()}-component-id or --{target.side.lower()}-component-name")


def _copy_source_design(args: argparse.Namespace, target_app: Any) -> Any | None:
    if args.source_project:
        from ansys.aedt.core import Hfss

        source_app = Hfss(
            project=str(args.source_project),
            design=args.source_design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=False,
            close_on_exit=False,
            remove_lock=args.remove_lock,
        )
        source_app.oproject.CopyDesign(args.source_design)
        return source_app

    target_app.oproject.CopyDesign(args.source_design)
    return None


def _paste_connector(args: argparse.Namespace, app: Any, editor: Any) -> str:
    before = _component_ids(editor)
    source_app = _copy_source_design(args, app)
    try:
        app.odesign.PasteDesign(1)
    finally:
        if source_app is not None and not args.keep_source_attached:
            source_app.release_desktop(close_projects=False, close_desktop=False)
    after = _component_ids(editor)
    new_ids: list[str] = []
    for component, ids in after.items():
        old = set(before.get(component, []))
        new_ids.extend([item for item in ids if item not in old])
    if not new_ids:
        raise RuntimeError("PasteDesign did not create a detectable 3D Layout component instance")
    return sorted(new_ids, key=lambda item: int(item))[-1]


def _set_component_placement(app: Any, comp_id: str, target: PlacementTarget, args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core.modeler.pcb.object_3d_layout import ComponentsSubCircuit3DLayout

    comp = ComponentsSubCircuit3DLayout(app.modeler, comp_id)
    if args.force_3d_placement:
        comp.is_3d_placement = True
    if args.local_origin is not None:
        comp.local_origin = args.local_origin
    comp.location = [target.x_mm, target.y_mm, target.z_mm]
    comp.angle = target.angle_deg
    if args.rotation_axis:
        comp.rotation_axis = args.rotation_axis
    return {
        "id": comp_id,
        "side": target.side,
        "requested_location_mm": [target.x_mm, target.y_mm, target.z_mm],
        "requested_angle_deg": target.angle_deg,
        "component_name": target.component_name,
        "after": _read_component_properties(app.modeler.oeditor, comp_id),
    }


def place_connectors(args: argparse.Namespace) -> dict[str, Any]:
    _apply_connector_placement_config(args)
    _apply_fallback_defaults(args)
    targets = _targets_from_args(args)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "project_config": str(args.project_config) if args.project_config else None,
        "connector_placement_profile": args.connector_placement_profile,
        "source_project": str(args.source_project) if args.source_project else None,
        "source_design": args.source_design,
        "operation": args.operation,
        "placement": args.placement,
        "anchor": args.anchor,
        "layout": str(args.layout) if args.layout else None,
        "z_mode": args.z_mode,
        "z_inputs": {
            "z_mm": args.z_mm,
            "pad_top_z_mm": args.pad_top_z_mm,
            "solder_bottom_z_mm": args.solder_bottom_z_mm,
            "solder_intrusion_mm": args.solder_intrusion_mm,
            "solder_intrusion_mil": args.solder_intrusion_mil,
        },
        "targets": [asdict(target) for target in targets],
        "execute": args.execute,
        "save": args.save,
    }
    if not args.execute:
        payload["status"] = "dry_run"
        return payload

    if args.backup:
        payload["backups"] = _backup_project(args.project)

    from ansys.aedt.core import Hfss3dLayout

    app = Hfss3dLayout(
        project=str(args.project),
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=args.new_desktop,
        close_on_exit=False,
        remove_lock=args.remove_lock,
    )
    try:
        app.modeler.model_units = "mm"
        editor = app.odesign.SetActiveEditor("Layout")
        before = _component_ids(editor)
        payload["before_components"] = before
        placed = []
        for target in targets:
            if args.operation == "import-and-place":
                comp_id = _paste_connector(args, app, editor)
            else:
                comp_id = _resolve_existing_component(editor, target, before)
            placed.append(_set_component_placement(app, comp_id, target, args))
        payload["placed"] = placed
        payload["after_components"] = _component_ids(editor)
        if args.save:
            payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
        payload["status"] = "placed"
        return payload
    finally:
        if not args.keep_attached:
            app.release_desktop(close_projects=args.close_projects, close_desktop=args.close_desktop)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Place connector design instances in an HFSS 3D Layout design.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--project-config", type=Path, default=None)
    parser.add_argument("--connector-placement-profile", default=None)
    parser.add_argument("--source-project", type=Path, default=None)
    parser.add_argument("--source-design", default=None)
    parser.add_argument("--operation", choices=["move-existing", "import-and-place"], default="move-existing")
    parser.add_argument("--placement", choices=["single", "dual"], required=True)
    parser.add_argument("--single-side", choices=["P1", "P2"], default="P1")
    parser.add_argument("--layout", type=Path, default=None, help="Layout JSON used to derive P1/P2 coordinates.")
    parser.add_argument("--anchor", choices=["pad-center", "port"], default="pad-center")
    parser.add_argument("--p1-x-mm", type=float, default=0.0)
    parser.add_argument("--p1-y-mm", type=float, default=0.0)
    parser.add_argument("--p2-x-mm", type=float, default=0.0)
    parser.add_argument("--p2-y-mm", type=float, default=0.0)
    parser.add_argument("--p1-offset-x-mm", type=float, default=None)
    parser.add_argument("--p1-offset-y-mm", type=float, default=None)
    parser.add_argument("--p2-offset-x-mm", type=float, default=None)
    parser.add_argument("--p2-offset-y-mm", type=float, default=None)
    parser.add_argument("--p1-angle-deg", type=float, default=None)
    parser.add_argument("--p2-angle-deg", type=float, default=None)
    parser.add_argument("--p1-solder-offset-x-mm", type=float, default=None)
    parser.add_argument("--p1-solder-offset-y-mm", type=float, default=None)
    parser.add_argument("--p2-solder-offset-x-mm", type=float, default=None)
    parser.add_argument("--p2-solder-offset-y-mm", type=float, default=None)
    parser.add_argument("--z-mode", choices=["fixed", "solder-bottom-to-pad-top"], default=None)
    parser.add_argument("--z-mm", type=float, default=None, help="Fixed component Z location when --z-mode=fixed.")
    parser.add_argument("--pad-top-z-mm", type=float, default=None, help="Pad top surface Z used by solder-bottom-to-pad-top.")
    parser.add_argument(
        "--solder-bottom-z-mm",
        type=float,
        default=None,
        help="Connector solder object's local bottom Z. Default matches Pin_solder bbox min Z.",
    )
    parser.add_argument("--solder-intrusion-mm", type=float, default=None, help="Positive solder penetration into pad.")
    parser.add_argument("--solder-intrusion-mil", type=float, default=None, help="Positive solder penetration into pad; overrides mm.")
    parser.add_argument("--local-origin", nargs=3, type=float, default=None, metavar=("X", "Y", "Z"))
    parser.add_argument("--rotation-axis", choices=["X", "Y", "Z"], default=None)
    parser.add_argument("--p1-component-id", default=None)
    parser.add_argument("--p2-component-id", default=None)
    parser.add_argument("--p1-component-name", default=None)
    parser.add_argument("--p2-component-name", default=None)
    parser.add_argument("--force-3d-placement", action="store_true", default=None)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--keep-source-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = place_connectors(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
