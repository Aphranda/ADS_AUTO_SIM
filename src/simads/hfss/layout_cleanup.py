"""HFSS 3D Layout source-layout cleanup helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from simads.hfss.layout_io import load_layout


OPTIONAL_SOURCE_LAYOUT_NAMES: tuple[str, ...] = (
    "input_series_hi_z",
    "output_series_hi_z",
    "p1_l2_cutout_rect_extend_right",
    "p2_l2_cutout_rect_extend_left",
    "p1_l3_cutout_rect_extend_right",
    "p2_l3_cutout_rect_extend_left",
    "clip_frame",
    "clip_box",
    "crop_frame",
    "crop_box",
    "cut_frame",
    "cut_box",
    "cutout_frame",
    "cutout_box",
    "board_clip_frame",
    "board_clip_box",
    "board_cut_frame",
    "board_cut_box",
    "pcb_clip_frame",
    "pcb_clip_box",
    "pcb_cut_frame",
    "pcb_cut_box",
    "simulation_clip_frame",
    "simulation_cut_frame",
)

SOURCE_LAYOUT_PREFIXES: tuple[str, ...] = (
    "ground_via_p1_top_",
    "ground_via_p1_bottom_",
    "ground_via_p2_top_",
    "ground_via_p2_bottom_",
    "gcpw_line_via_top_",
    "gcpw_line_via_bottom_",
    "hfss_ground_plane_part_",
    "l3_ground_plane_part_",
)

TEMPORARY_CLIP_FRAME_PREFIXES: tuple[str, ...] = (
    "clip_frame",
    "clip_box",
    "crop_frame",
    "crop_box",
    "cut_frame",
    "cut_box",
    "cutout_frame",
    "cutout_box",
    "board_clip",
    "board_cut",
    "pcb_clip",
    "pcb_cut",
    "simulation_clip",
    "simulation_cut",
)


def shape_name(shape: dict[str, Any]) -> str:
    return str(shape.get("name", ""))


def selected_shapes(layout: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    shapes = [shape for shape in layout.get("shapes", []) if isinstance(shape, dict)]
    if scope in {"single-p1-pcb-full", "bfp-real-board-full"}:
        return shapes
    raise ValueError(f"unsupported replacement scope: {scope}")


def delete_names_for_shape(shape: dict[str, Any]) -> list[str]:
    name = shape_name(shape)
    if not name:
        return []
    if shape.get("kind") == "via":
        return [f"{name}_pad", name]
    return [name]


def append_unique(output: list[str], names: Iterable[str]) -> None:
    for name in names:
        if name and name not in output:
            output.append(name)


def delete_names_for_shapes(shapes: Iterable[dict[str, Any]]) -> list[str]:
    output: list[str] = []
    for shape in shapes:
        append_unique(output, delete_names_for_shape(shape))
    return output


def sibling_layout_root(layout_path: Path) -> Path | None:
    parent = layout_path.parent
    if parent.parent.name.lower() == "layouts":
        return parent.parent
    return None


def delete_names_for_layout_files(roots: Iterable[Path]) -> list[str]:
    output: list[str] = []
    seen_files: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else sorted(root.rglob("*_layout.json"))
        for path in paths:
            resolved = path.resolve()
            if resolved in seen_files:
                continue
            seen_files.add(resolved)
            try:
                layout = load_layout(path)
            except Exception:
                continue
            append_unique(output, delete_names_for_shapes(selected_shapes(layout, "single-p1-pcb-full")))
    return output


def generated_optional_delete_names(max_via_index: int = 32) -> list[str]:
    output: list[str] = []
    append_unique(output, OPTIONAL_SOURCE_LAYOUT_NAMES)
    for prefix in SOURCE_LAYOUT_PREFIXES:
        if prefix.endswith("_part_"):
            append_unique(output, [f"{prefix}{idx}" for idx in range(1, 17)])
            continue
        for idx in range(1, max_via_index + 1):
            append_unique(output, [f"{prefix}{idx}_pad", f"{prefix}{idx}"])
    return output


def full_rebuild_delete_names(
    layout: dict[str, Any],
    *,
    ground_plane_name: str,
    scope: str = "single-p1-pcb-full",
    stale_layout_roots: Iterable[Path] = (),
) -> list[str]:
    names = [ground_plane_name]
    append_unique(names, delete_names_for_shapes(selected_shapes(layout, scope)))
    append_unique(names, generated_optional_delete_names())
    append_unique(names, delete_names_for_layout_files(stale_layout_roots))
    return names


def matches_aedt_generated_name(actual: str, base: str) -> bool:
    if actual == base:
        return True
    if not actual.startswith(base):
        return False
    suffix = actual[len(base) :]
    if not suffix:
        return True
    return any(ch.isalpha() for ch in suffix)


def resolve_existing_delete_names(existing: set[str], requested: list[str]) -> list[str]:
    output: list[str] = []
    for base in requested:
        for actual in sorted(existing):
            if matches_aedt_generated_name(actual, base) and actual not in output:
                output.append(actual)
    return output


def resolve_existing_delete_names_and_prefixes(
    existing: set[str],
    requested: list[str],
    prefixes: Iterable[str] = (),
) -> list[str]:
    output = resolve_existing_delete_names(existing, requested)
    normalized_prefixes = tuple(prefix for prefix in prefixes if prefix)
    for actual in sorted(existing):
        if any(actual == prefix or actual.startswith(prefix) for prefix in normalized_prefixes):
            if actual not in output:
                output.append(actual)
    return output


def source_like_names(existing: set[str], requested: list[str]) -> list[str]:
    return resolve_existing_delete_names_and_prefixes(existing, requested, TEMPORARY_CLIP_FRAME_PREFIXES)


def existing_layout_objects(modeler: Any, editor: Any) -> set[str]:
    names: set[str] = set()
    for attr in ("polygon_names", "via_names", "line_names", "polygon_voids_names", "line_voids_names"):
        try:
            value = getattr(modeler, attr)
            items = value() if callable(value) else value
            names.update(str(item) for item in items or [])
        except Exception:
            continue
    for net in ("IN", "GND", "SIG", "OUT"):
        try:
            names.update(str(item) for item in modeler.objects_by_net(net))
        except Exception:
            continue
    for layer in ("ETCH_TOP", "ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"):
        try:
            names.update(str(item) for item in modeler.objects_by_layer(layer))
        except Exception:
            continue
    groups = ("Solids", "Sheets", "Lines", "Unclassified", "Non Model", "Planes", "Points")
    for group in groups:
        try:
            names.update(str(item) for item in editor.GetObjectsInGroup(group))
        except Exception:
            continue
    return names


def delete_layout_objects(editor: Any, names: list[str]) -> dict[str, Any]:
    deleted: list[str] = []
    errors: list[dict[str, str]] = []
    for name in names:
        try:
            editor.Delete(["NAME:Selections", "Selections:=", name])
            deleted.append(name)
        except Exception as exc:
            errors.append({"name": name, "error": f"{type(exc).__name__}: {exc}"})
    return {"requested": names, "deleted": deleted, "errors": errors, "ok": not errors}
