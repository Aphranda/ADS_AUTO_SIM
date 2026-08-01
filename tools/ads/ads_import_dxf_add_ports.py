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


def _padstack_name_for_via(via_layer: str, diameter_mm: float) -> str:
    diameter_tag = f"{diameter_mm:.3f}".replace("-", "m").replace(".", "p")
    safe_layer = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in via_layer)
    return f"{safe_layer}_d{diameter_tag}mm"


def _ensure_circular_via_padstack(library: Any, metal_layer: str, via_layer: str, diameter_mm: float) -> str:
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


def _add_generated_dxf_subset_layout(
    db_uu: Any,
    library: Any,
    cell_name: str,
    dxf_path: str,
    metal_layer: str,
    via_layer: str,
) -> dict[str, int]:
    log(f"Parsing generated DXF subset: {dxf_path}")
    shapes = parse_generated_dxf_subset(dxf_path)
    library_name = library.name
    log(f"Creating fallback layout {library_name}:{cell_name}:layout with {len(shapes)} DXF entities")
    design = db_uu.create_layout((library_name, cell_name, "layout"))
    counts = {"solid": 0, "circle": 0, "via": 0, "line": 0}
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
                    design.add_rectangle(layer_id, (min(xs), min(ys)), (max(xs), max(ys)))
                else:
                    design.add_polygon(layer_id, points)
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
                    design.add_via_with_drill_layer(
                        via_padstacks[diameter_key],
                        layer_id,
                        shape["center"],
                        name=f"{via_layer}_{counts['via'] + 1}",
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
    p1: tuple[float, float],
    p2: tuple[float, float],
    do_import: bool,
) -> dict[str, object]:
    """Runs inside an ADS Python context."""
    log("ADS callable entered: importing keysight ADS modules")
    import keysight.ads.de as de
    from keysight.ads.de import ael, db_uu

    log(f"Opening ADS workspace: {workspace_path}")
    workspace = de.open_workspace(workspace_path)
    try:
        log(f"Looking up ADS library: {library_name}")
        library = de.Library.get(library_name)
        if library is None:
            raise RuntimeError(f"ADS library not found: {library_name}")

        import_method = "skipped"
        native_counts: dict[str, int] | None = None

        if do_import:
            if not Path(layer_map_path).exists():
                log(
                    "DXF layer map not found; using generated-DXF fallback "
                    f"({layer_map_path})."
                )
                native_counts = _add_generated_dxf_subset_layout(
                    db_uu, library, cell_name, dxf_path, metal_layer, via_layer
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
                        db_uu, library, cell_name, dxf_path, metal_layer, via_layer
                    )
                    import_method = "generated_dxf_subset"

        log(f"Opening layout for pin placement: {library_name}:{cell_name}:layout")
        design = db_uu.open_design((library_name, cell_name, "layout"), "Append")
        try:
            layer_id = design.create_layer_id(metal_layer)
            term_type = getattr(getattr(db_uu, "TermType", object), "INPUT_OUTPUT", None)

            for pin_name, loc, angle in (("P1", p1, 180.0), ("P2", p2, 0.0)):
                log(f"Adding pin {pin_name} at {loc} angle={angle}")
                net = design.find_or_add_net(pin_name)
                if term_type is None:
                    try:
                        term = design.add_term(net, pin_name)
                    except RuntimeError as exc:
                        if "already exists" not in str(exc):
                            raise
                        log(f"Pin/terminal {pin_name} already exists; skipping")
                        continue
                else:
                    try:
                        term = design.add_term(net, pin_name, term_type)
                    except RuntimeError as exc:
                        if "already exists" not in str(exc):
                            raise
                        log(f"Pin/terminal {pin_name} already exists; skipping")
                        continue
                dot = design.add_dot(layer_id, loc)
                try:
                    design.add_pin(term, dot, angle=angle)
                except TypeError:
                    design.add_pin(term, dot)

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
    parser.add_argument("--metal-layer", default="cond")
    parser.add_argument("--via-layer", default="pcvia1")
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
    if not args.skip_import and cell_name != args.dxf.stem:
        raise SystemExit(
            "DXF import creates a cell from the DXF file stem. "
            f"Use --cell {args.dxf.stem!r}, rename the DXF, or pass --skip-import."
        )
    p1, p2 = load_port_locations(args.params)
    log(
        "Import configuration: "
        f"profile={args.profile}, workspace={workspace}, library={library}, "
        f"cell={cell_name}, dxf={args.dxf}, layer_map={layer_map}, "
        f"metal_layer={args.metal_layer}, via_layer={args.via_layer}, "
        f"skip_import={args.skip_import}, p1={p1}, p2={p2}"
    )

    worker_args = [
        str(workspace),
        library,
        str(args.dxf.resolve()),
        str(layer_map),
        cell_name,
        args.metal_layer,
        args.via_layer,
        p1,
        p2,
        not args.skip_import,
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


