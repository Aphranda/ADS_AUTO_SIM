"""Layout import planning helpers for ADS automation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from simads.ads.workspace import AdsCellRef, AdsCommandPlan
from simads.config import AdsProfile


@dataclass(frozen=True)
class LayoutImportPlan:
    profile_id: str
    target: AdsCellRef
    dxf_path: Path
    params_path: Path | None = None
    layout_json_path: Path | None = None
    layer_map_path: Path | None = None
    metal_layer: str = "cond"
    via_layer: str = "pcvia1"
    force_generated_dxf_subset: bool = False

    def to_manifest(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "workspace": str(self.target.workspace),
            "library": self.target.library,
            "cell": self.target.cell,
            "view": self.target.view,
            "dxf_path": str(self.dxf_path),
            "params_path": str(self.params_path) if self.params_path else None,
            "layout_json_path": str(self.layout_json_path) if self.layout_json_path else None,
            "layer_map_path": str(self.layer_map_path) if self.layer_map_path else None,
            "metal_layer": self.metal_layer,
            "via_layer": self.via_layer,
            "force_generated_dxf_subset": self.force_generated_dxf_subset,
        }


def build_layout_import_plan(
    profile: AdsProfile,
    *,
    dxf_path: Path,
    target_cell: str,
    params_path: Path | None = None,
    layout_json_path: Path | None = None,
    layer_map_path: Path | None = None,
    metal_layer: str = "cond",
    via_layer: str = "pcvia1",
    force_generated_dxf_subset: bool = False,
) -> LayoutImportPlan:
    return LayoutImportPlan(
        profile_id=profile.name,
        target=AdsCellRef(profile.workspace, profile.library, target_cell, "layout"),
        dxf_path=dxf_path,
        params_path=params_path,
        layout_json_path=layout_json_path,
        layer_map_path=layer_map_path or profile.layer_map,
        metal_layer=metal_layer,
        via_layer=via_layer,
        force_generated_dxf_subset=force_generated_dxf_subset,
    )


def load_layout_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dxf_group_pairs(dxf_path: Path | str) -> list[tuple[str, str]]:
    lines = Path(dxf_path).read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) % 2:
        raise ValueError(f"DXF group-code stream has an odd line count: {dxf_path}")
    return [(lines[idx].strip(), lines[idx + 1].strip()) for idx in range(0, len(lines), 2)]


def parse_generated_dxf_subset(dxf_path: Path | str) -> list[dict[str, Any]]:
    """Parse the DXF subset emitted by the local layout generators."""
    pairs = dxf_group_pairs(dxf_path)
    shapes: list[dict[str, Any]] = []
    idx = 0

    while idx < len(pairs):
        code, value = pairs[idx]
        if code != "0" or value not in {"SOLID", "CIRCLE", "LINE"}:
            idx += 1
            continue

        entity_type = value
        idx += 1
        groups: dict[str, list[str]] = {}
        while idx < len(pairs):
            next_code, next_value = pairs[idx]
            if next_code == "0":
                break
            groups.setdefault(next_code, []).append(next_value)
            idx += 1

        layer = groups.get("8", [""])[0]
        if not layer:
            raise ValueError(f"{entity_type} entity has no layer in {dxf_path}")

        if entity_type == "SOLID":
            points = []
            for x_code, y_code in (("10", "20"), ("11", "21"), ("12", "22"), ("13", "23")):
                points.append((float(groups[x_code][0]), float(groups[y_code][0])))
            shapes.append({"type": "solid", "layer": layer, "points": points})
        elif entity_type == "CIRCLE":
            center = (float(groups["10"][0]), float(groups["20"][0]))
            radius = float(groups["40"][0])
            shapes.append({"type": "circle", "layer": layer, "center": center, "radius": radius})
        elif entity_type == "LINE":
            start = (float(groups["10"][0]), float(groups["20"][0]))
            end = (float(groups["11"][0]), float(groups["21"][0]))
            shapes.append({"type": "line", "layer": layer, "points": [start, end]})

    return shapes


def load_port_locations(path: Path) -> dict[str, tuple[float, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    ports = data.get("ports")
    if isinstance(ports, list):
        return {
            str(port["name"]): (float(port["x"]), float(port["y"]))
            for port in ports
            if isinstance(port, dict) and "name" in port and "x" in port and "y" in port
        }
    if isinstance(ports, dict):
        return {
            str(name): (float(value[0]), float(value[1]))
            for name, value in ports.items()
            if isinstance(value, list | tuple) and len(value) >= 2
        }

    params = data["parameters"]
    derived = data["derived"]
    feed_len = float(params["feed_len_mm"])
    tap_y = float(params["tap_from_bottom_mm"])
    field_w = float(derived["field_width_mm"])
    return {"P1": (-feed_len, tap_y), "P2": (field_w + feed_len, tap_y)}


def load_p1_p2_locations(path: Path) -> tuple[tuple[float, float], tuple[float, float]]:
    ports = load_port_locations(path)
    if "P1" not in ports or "P2" not in ports:
        raise ValueError(f"port file does not contain both P1 and P2: {path}")
    return ports["P1"], ports["P2"]


def build_import_command(
    plan: LayoutImportPlan,
    *,
    ads_python: Path,
    script: Path,
) -> AdsCommandPlan:
    if plan.params_path is None:
        raise ValueError("ads_import_dxf_add_ports.py currently requires --params")
    args = [
        "--workspace",
        str(plan.target.workspace),
        "--library",
        plan.target.library,
        "--cell",
        plan.target.cell,
        "--dxf",
        str(plan.dxf_path),
        "--metal-layer",
        plan.metal_layer,
        "--via-layer",
        plan.via_layer,
    ]
    args.extend(["--params", str(plan.params_path)])
    if plan.layer_map_path:
        args.extend(["--layer-map", str(plan.layer_map_path)])
    if plan.force_generated_dxf_subset:
        args.append("--force-generated-dxf-subset")
    return AdsCommandPlan("ads_import_dxf_add_ports", ads_python, script, tuple(args), cwd=script.parents[1])
