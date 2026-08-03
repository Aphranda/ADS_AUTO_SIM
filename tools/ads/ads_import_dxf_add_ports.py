#!/usr/bin/env python3
r"""Import a generated DXF into an ADS workspace and add layout pins.

Run this with the ADS Python that has ``keysight.edatoolbox`` available, for
example:

    D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe \
        SIM\tools\ads_import_dxf_add_ports.py \
        --dxf SIM\projects\bfp_6_8g_i7_fr4\layouts\sweep\interdigital_9o_ro4350b_508um_v4_more_coupling_mm_coords.dxf \
        --params SIM\projects\bfp_6_8g_i7_fr4\layouts\sweep\interdigital_9o_ro4350b_508um_v4_more_coupling_params.json

The preferred path uses ADS's DXF translator. In ADS automation mode that
translator is not always exposed, so this script can fall back to importing the
small generated DXF subset used by this project: SOLID rectangles, CIRCLE vias,
and the EM_BOUNDARY rectangle.
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

from ads_profiles import profile_names, resolve_layer_map, resolve_library, resolve_workspace
from simads.ads.layout import load_p1_p2_locations, parse_generated_dxf_subset
from simads.ads.ports import build_two_port_reference_specs, place_layout_pins, resolve_next_reference_layer

GROUND_NET_NAME = "GND"


def ensure_hpeesof_dir() -> None:
    if os.environ.get("HPEESOF_DIR"):
        return
    executable = Path(sys.executable).resolve()
    ads_root = executable.parents[2]
    os.environ["HPEESOF_DIR"] = str(ads_root)
    log(f"HPEESOF_DIR was not set; using {ads_root}")


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    log_path = os.environ.get("ADS_FLOW_LOG")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(log_path).open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")


def load_port_locations(params_path: Path) -> tuple[tuple[float, float], tuple[float, float]]:
    log(f"Loading port locations: {params_path}")
    return load_p1_p2_locations(params_path)


def _unique_nonempty(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = value.strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return tuple(result)


def _load_stackup_geometry_from_params(params: dict[str, Any]) -> dict[str, Any]:
    stackup_path_raw = params.get("stackup_config")
    if not stackup_path_raw:
        return {}
    stackup_path = Path(str(stackup_path_raw))
    if not stackup_path.is_absolute():
        stackup_path = _REPO_ROOT / stackup_path
    if not stackup_path.exists():
        log(f"Stackup config referenced by params is missing; skipping ground layer expansion: {stackup_path}")
        return {}
    data = json.loads(stackup_path.read_text(encoding="utf-8-sig"))
    geometry = data.get("geometry", {})
    return geometry if isinstance(geometry, dict) else {}


def load_layout_net_config(params_path: Path) -> tuple[str | None, str | None, tuple[str, ...]]:
    data = json.loads(params_path.read_text(encoding="utf-8"))
    params = data.get("parameters", {})
    if not isinstance(params, dict):
        return None, None, ()
    metal = params.get("metal_layer") or params.get("signal_layer")
    via = params.get("via_layer")
    ground_layers: list[str] = []

    params_ground_layers = params.get("ground_layers")
    if isinstance(params_ground_layers, list):
        ground_layers.extend(str(layer) for layer in params_ground_layers)

    if not ground_layers:
        geometry = _load_stackup_geometry_from_params(params)
        stackup_ground_layers = geometry.get("ground_layers")
        if isinstance(stackup_ground_layers, list):
            ground_layers.extend(str(layer) for layer in stackup_ground_layers)

    if not ground_layers:
        for key in ("reference_ground_layer", "ground_layer"):
            if params.get(key):
                ground_layers.append(str(params[key]))

    metal_name = str(metal) if metal else None
    ground_tuple = _unique_nonempty([layer for layer in ground_layers if layer != metal_name])
    return metal_name, str(via) if via else None, ground_tuple


def load_layout_via_pad_diameter(params_path: Path) -> float | None:
    data = json.loads(params_path.read_text(encoding="utf-8"))
    params = data.get("parameters", {})
    if not isinstance(params, dict):
        return None
    raw_values = [params.get("via_pad_mm"), params.get("via_diameter_mm")]
    values: list[float] = []
    for value in raw_values:
        if value in (None, ""):
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    if not values:
        return None
    return max(values)


def _padstack_name_for_via(via_layer: str, diameter_mm: float) -> str:
    diameter_tag = f"{diameter_mm:.3f}".replace("-", "m").replace(".", "p")
    safe_layer = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in via_layer)
    return f"{safe_layer}_d{diameter_tag}mm"


def _ensure_circular_via_padstack(
    library: Any,
    metal_layer: str,
    via_layer: str,
    diameter_mm: float,
) -> str:
    from keysight.ads.de.tech import Tech, pads

    padstack_name = _padstack_name_for_via(via_layer, diameter_mm)
    padstack_ref = f"{library.name}:{padstack_name}"
    try:
        Tech.get_padstack_from_lib(padstack_ref)
        log(f"Using existing ADS padstack: {padstack_ref}")
        return padstack_ref
    except RuntimeError:
        pass

    tech = library.tech
    if tech is None:
        raise RuntimeError(f'ADS library "{library.name}" has no technology database; cannot create padstack.')

    log(
        "Creating ADS circular via padstack: "
        f"{padstack_ref}, pad_layer={metal_layer}, drill_layer={via_layer}, diameter={diameter_mm:.6g} mm"
    )
    padstack = tech.create_padstack(padstack_name)

    pad_layer = pads.PadLayerEntry()
    pad_layer.layer_matcher = pads.MatchLayerByName(metal_layer)
    pad_layer.pad = pads.CircularPad(f"{diameter_mm:.6g} mm")
    padstack.default_pad_layer = pad_layer

    drill = pads.ViaPadDrill("CIRCLE")
    drill.drill_size = f"{diameter_mm:.6g} mm"
    padstack.drill = drill

    tech.save_padstacks()
    return padstack_ref


def _promote_shape_to_ground_plane(
    db_uu: Any,
    design: Any,
    layer_id: Any,
    shape_obj: Any,
    *,
    layer: str,
    index: int,
    net: Any | None = None,
) -> bool:
    try:
        plane_info = db_uu.PlaneInfo(design)
        plane_info.layer_id = layer_id
        if net is not None:
            _try_assign_object_net(plane_info, net)
        plane = design.add_plane(plane_info, shape_obj, f"PLANE_{layer}_{index}")
        if net is not None:
            _try_assign_object_net(plane, net)
        return True
    except Exception as exc:
        log(f"Could not promote {layer} shape to ADS Plane; keeping plain copper shape: {exc}")
        return False


def _try_assign_object_net(obj: Any, net: Any) -> bool:
    for attr in ("net",):
        try:
            setattr(obj, attr, net)
            return True
        except Exception:
            pass
    for method_name in ("set_net", "setNet"):
        method = getattr(obj, method_name, None)
        if callable(method):
            try:
                method(net)
                return True
            except Exception:
                pass
    return False


def _add_generated_dxf_subset_layout(
    db_uu: Any,
    library: Any,
    cell_name: str,
    dxf_path: str,
    metal_layer: str,
    via_layer: str,
    ground_layers: tuple[str, ...] = (),
    via_pad_diameter_mm: float | None = None,
) -> dict[str, int]:
    log(f"Parsing generated DXF subset: {dxf_path}")
    shapes = parse_generated_dxf_subset(dxf_path)
    library_name = library.name
    log(f"Creating fallback layout {library_name}:{cell_name}:layout with {len(shapes)} DXF entities")
    design = db_uu.create_layout((library_name, cell_name, "layout"))
    ground_layer_set = set(ground_layers)
    gnd_net = design.find_or_add_net(GROUND_NET_NAME) if ground_layer_set else None
    if ground_layer_set:
        log(f"Promoting explicit reference copper layers to ADS GND planes: {', '.join(ground_layers)}")
    counts = {"solid": 0, "circle": 0, "via": 0, "line": 0, "plane": 0, "gnd_label": 0}
    try:
        layer_ids: dict[str, Any] = {}
        via_padstacks: dict[float, str] = {}
        for shape in shapes:
            layer = shape["layer"]
            if layer not in layer_ids:
                layer_ids[layer] = design.create_layer_id(layer)
            layer_id = layer_ids[layer]

            if shape["type"] == "solid":
                points = shape["points"]
                xs = [point[0] for point in points]
                ys = [point[1] for point in points]
                if len(set(xs)) == 2 and len(set(ys)) == 2:
                    shape_obj = design.add_rectangle(layer_id, (min(xs), min(ys)), (max(xs), max(ys)))
                else:
                    shape_obj = design.add_polygon(layer_id, points)
                if layer in ground_layer_set:
                    if gnd_net is not None and not _try_assign_object_net(shape_obj, gnd_net):
                        log(f"Could not assign net {GROUND_NET_NAME} to {layer} copper shape before plane promotion")
                    if _promote_shape_to_ground_plane(
                        db_uu,
                        design,
                        layer_id,
                        shape_obj,
                        layer=layer,
                        index=counts["plane"] + 1,
                        net=gnd_net,
                    ):
                        counts["plane"] += 1
                counts["solid"] += 1
            elif shape["type"] == "circle":
                if layer == via_layer:
                    diameter_mm = 2.0 * float(shape["radius"])
                    diameter_key = round(diameter_mm, 6)
                    if diameter_key not in via_padstacks:
                        via_padstacks[diameter_key] = _ensure_circular_via_padstack(
                            library,
                            metal_layer,
                            via_layer,
                            diameter_mm,
                        )
                    via_name = f"{via_layer}_{counts['via'] + 1}"
                    log(f"Adding ADS via with drill layer: {via_name}, layer={via_layer}")
                    design.add_via_with_drill_layer(
                        via_padstacks[diameter_key],
                        layer_id,
                        shape["center"],
                        name=via_name,
                    )
                    counts["via"] += 1
                else:
                    design.add_circle(layer_id, shape["center"], shape["radius"])
                    counts["circle"] += 1
            elif shape["type"] == "line":
                design.add_line(layer_id, shape["points"])
                counts["line"] += 1

        log(f"Saving fallback layout {library_name}:{cell_name}:layout")
        design.save_design()
    finally:
        close_design = getattr(design, "close_design", None)
        if callable(close_design):
            close_design()

    return counts


def ads_import_and_add_ports(
    workspace_path: str,
    library_name: str,
    dxf_path: str,
    layer_map_path: str,
    cell_name: str,
    metal_layer: str,
    via_layer: str,
    ground_layers: tuple[str, ...],
    p1: tuple[float, float],
    p2: tuple[float, float],
    do_import: bool,
    force_generated_dxf_subset: bool = False,
    via_pad_diameter_mm: float | None = None,
) -> dict[str, object]:
    """Runs inside an ADS Python context."""
    log("ADS callable entered: importing keysight ADS modules")
    import keysight.ads.de as de
    from keysight.ads.de import ael, db_uu

    log(f"Opening ADS workspace: {workspace_path}")
    workspace = de.open_workspace(workspace_path)
    try:
        log(f"Looking up ADS library: {library_name}")
        try:
            library = de.Library.get(library_name)
        except RuntimeError:
            library = None
        if library is None:
            library_path = Path(workspace_path) / library_name
            log(f"ADS library is not open; opening {library_name} from {library_path}")
            library = workspace.open_library(library_name, library_path, mode=de.LibraryMode.SHARED)
        if library is None:
            raise RuntimeError(f"ADS library not found: {library_name}")

        import_method = "skipped"
        native_counts: dict[str, int] | None = None

        if do_import:
            if force_generated_dxf_subset:
                log("Forcing generated-DXF subset fallback importer.")
                native_counts = _add_generated_dxf_subset_layout(
                    db_uu, library, cell_name, dxf_path, metal_layer, via_layer, ground_layers, via_pad_diameter_mm
                )
                import_method = "generated_dxf_subset"
            elif not Path(layer_map_path).exists():
                log(
                    "DXF layer map not found; using generated-DXF fallback "
                    f"({layer_map_path})."
                )
                native_counts = _add_generated_dxf_subset_layout(
                    db_uu, library, cell_name, dxf_path, metal_layer, via_layer, ground_layers, via_pad_diameter_mm
                )
                import_method = "generated_dxf_subset"
            else:
                try:
                    log(f"Using ADS DXF translator with layer map: {layer_map_path}")
                    importer = ael.call.dxf_create_importer()
                    ael.call.dxf_import_set_overwrite(importer, True)
                    ael.call.dxf_import_set_flatten(importer, True)
                    ael.call.dxf_import_set_layermap_path(importer, layer_map_path)
                    ael.call.dxf_import_design(importer, dxf_path, library.name)
                    import_method = "ads_dxf_translator"
                except Exception as exc:
                    log(
                        "ADS DXF translator failed in this Python context; "
                        f"using generated-DXF fallback ({exc})."
                    )
                    native_counts = _add_generated_dxf_subset_layout(
                        db_uu, library, cell_name, dxf_path, metal_layer, via_layer, ground_layers, via_pad_diameter_mm
                    )
                    import_method = "generated_dxf_subset"

        log(f"Opening layout for pin placement: {library_name}:{cell_name}:layout")
        design = db_uu.open_design((library_name, cell_name, "layout"), "Append")
        try:
            reference_layer = resolve_next_reference_layer(metal_layer, ground_layers)
            ports = build_two_port_reference_specs(
                p1,
                p2,
                signal_layer=metal_layer,
                reference_layer=reference_layer,
                reference_net=GROUND_NET_NAME,
            )
            placed_ports = place_layout_pins(design, db_uu, ports, log=log)

            log(f"Saving layout with pins: {library_name}:{cell_name}:layout")
            design.save_design()
        finally:
            close_design = getattr(design, "close_design", None)
            if callable(close_design):
                close_design()
    finally:
        log(f"Closing ADS workspace: {workspace_path}")
        workspace.close()

    return {
        "workspace": workspace_path,
        "library": library_name,
        "cell": cell_name,
        "layout": "layout",
        "p1_mm": p1,
        "p2_mm": p2,
        "ports": placed_ports,
        "imported": do_import,
        "import_method": import_method,
        "native_counts": native_counts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import DXF into ADS and add P1/P2 layout pins.")
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--library", default=None, help="Override profile ADS library.")
    parser.add_argument("--dxf", type=Path, required=True)
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--layer-map", type=Path, default=None, help="Override profile DXF layer map.")
    parser.add_argument("--cell", default=None, help="ADS target cell. Default: DXF file stem.")
    parser.add_argument("--metal-layer", default=None)
    parser.add_argument("--via-layer", default=None)
    parser.add_argument(
        "--force-generated-dxf-subset",
        action="store_true",
        help="Bypass ADS's native DXF translator and import the project-generated SOLID/CIRCLE/LINE subset directly.",
    )
    parser.add_argument("--skip-import", action="store_true", help="Only add pins to an existing layout cell.")
    parser.add_argument(
        "--multipython",
        action="store_true",
        help="Use keysight.edatoolbox.multi_python.ads_context instead of direct ADS Python APIs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log("ads_import_dxf_add_ports.py started")
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    layer_map = resolve_layer_map(args.profile, workspace, args.layer_map)
    cell_name = args.cell or args.dxf.stem
    if not args.skip_import and cell_name != args.dxf.stem and not args.force_generated_dxf_subset:
        raise SystemExit(
            "ADS native DXF import creates a cell from the DXF file stem. "
            f"Use --cell {args.dxf.stem!r}, rename the DXF, pass --skip-import, "
            "or use --force-generated-dxf-subset for a custom ADS cell name."
        )
    p1, p2 = load_port_locations(args.params)
    param_metal_layer, param_via_layer, param_ground_layers = load_layout_net_config(args.params)
    via_pad_diameter_mm = load_layout_via_pad_diameter(args.params)
    metal_layer = args.metal_layer or param_metal_layer or "cond"
    via_layer = args.via_layer or param_via_layer or "pcvia1"
    ground_layers = tuple(layer for layer in param_ground_layers if layer != metal_layer)
    log(
        "Import configuration: "
        f"profile={args.profile}, workspace={workspace}, library={library}, "
        f"cell={cell_name}, dxf={args.dxf}, layer_map={layer_map}, "
        f"metal_layer={metal_layer}, via_layer={via_layer}, "
        f"ground_layers={ground_layers}, "
        f"via_pad_diameter_mm={via_pad_diameter_mm}, "
        f"force_generated_dxf_subset={args.force_generated_dxf_subset}, "
        f"skip_import={args.skip_import}, p1={p1}, p2={p2}"
    )

    worker_args = [
        str(workspace),
        library,
        str(args.dxf.resolve()),
        str(layer_map),
        cell_name,
        metal_layer,
        via_layer,
        ground_layers,
        p1,
        p2,
        not args.skip_import,
        args.force_generated_dxf_subset,
        via_pad_diameter_mm,
    ]
    if args.multipython:
        log("Importing keysight.edatoolbox.multi_python")
        import keysight.edatoolbox.multi_python as multi_python

        log("Entering ADS context")
        with multi_python.ads_context() as ads_ctx:
            log("ADS context ready; calling import worker")
            result = ads_ctx.call(ads_import_and_add_ports, args=worker_args)
        log("ADS context closed")
    else:
        log("Using direct ADS Python APIs")
        ensure_hpeesof_dir()
        result = ads_import_and_add_ports(*worker_args)

    print("ADS import/pin placement complete:", flush=True)
    for key, value in result.items():
        print(f"  {key}: {value}", flush=True)


if __name__ == "__main__":
    main()


