"""Microstrip connector launch layout generation for HFSS smoke studies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from typing import Any

from simads.config import StackupConfig, load_stackup_config, stackup_name_token
from simads.exporters.json import write_layout_json
from simads.exporters.svg import write_svg
from simads.geometry import Boundary, LayerMap, Layout, Polygon, Port, Rect, Via, min_feature, to_dict


FIXTURE_TYPE = "microstrip_connector_50r"
BASELINE_FIXTURE_TYPE = "microstrip_50r_through"
SINGLE_CONNECTOR_FIXTURE_TYPE = "microstrip_single_connector_50r"
LOGICAL_SIGNAL_LAYER = "cond"
LOGICAL_VIA_LAYER = "pcvia1"
BOUNDARY_LAYER = "EM_BOUNDARY"


@dataclass(frozen=True)
class ConnectorLaunchParams:
    name: str = "microstrip_connector_50r_smoke"
    connector_type: str = "edge_launch_surrogate"
    connector_model_version: str = "route_a_surrogate_v1"
    connector_route: str = "route_a_2p5d_launch_surrogate"
    stackup_id: str | None = None
    stackup_token: str | None = None
    stackup_config: str | None = None
    line_w_mm: float = 0.3175
    line_l_mm: float = 18.0
    edge_margin_mm: float = 1.5
    pin_pad_w_mm: float = 1.2
    pin_pad_l_mm: float = 4.8
    pad_to_edge_mm: float = 0.0
    taper_l_mm: float = 1.60
    taper_w_start_mm: float = 1.2
    taper_w_end_mm: float = 0.3175
    launch_feed_l_mm: float = 0.50
    gnd_clearance_mm: float = 0.30
    transmission_line_model: str = "grounded_coplanar_waveguide"
    cpw_ground_gap_mm: float = 0.2032
    cpw_ground_enabled: bool = True
    line_via_pitch_mm: float = 2.00
    line_via_enabled: bool = True
    anti_pad_w_mm: float = 1.80
    via_d_mm: float = 0.30
    via_pad_d_mm: float = 0.55
    via_pitch_mm: float = 0.80
    via_count: int = 4
    fence_offset_mm: float = 0.55
    fence_pitch_mm: float = 1.20
    fence_span_mm: float = 4.20
    reference_plane_offset_mm: float = 0.0
    port_deembed_mm: float = 0.0
    board_width_mm: float = 8.0
    min_fab_feature_mm: float = 0.1524
    mirror: bool = True
    signal_layer: str | None = None
    reference_ground_layer: str | None = None
    via_top_layer: str | None = None
    via_bottom_layer: str | None = None
    ground_layers: tuple[str, ...] = ()
    ground_plane_name: str = "hfss_ground_plane"
    metal_layer: str = LOGICAL_SIGNAL_LAYER
    via_layer: str = LOGICAL_VIA_LAYER
    boundary_layer: str = BOUNDARY_LAYER

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ground_layers"] = list(self.ground_layers)
        return data


@dataclass(frozen=True)
class ConnectorLayoutCheck:
    name: str
    ok: bool
    message: str


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def params_with_stackup_config(
    params: ConnectorLaunchParams,
    stackup: StackupConfig,
    *,
    config_path: Path | None = None,
    rename: bool = True,
) -> ConnectorLaunchParams:
    token = stackup_name_token(stackup)
    name = params.name
    if rename and token not in name:
        name = f"{name}_{token}"
    return replace(
        params,
        name=name,
        stackup_id=stackup.stackup_id,
        stackup_token=token,
        stackup_config=str(config_path) if config_path is not None else None,
        signal_layer=stackup.geometry.signal_layer,
        reference_ground_layer=stackup.geometry.reference_ground_layer,
        via_top_layer=stackup.geometry.via_top_layer,
        via_bottom_layer=stackup.geometry.via_bottom_layer,
        ground_layers=stackup.geometry.ground_layers,
        ground_plane_name=stackup.geometry.ground_plane_name,
    )


def params_from_mapping(data: dict[str, Any]) -> ConnectorLaunchParams:
    fields = ConnectorLaunchParams.__dataclass_fields__
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        if key not in fields:
            continue
        if key in {"via_count"}:
            kwargs[key] = int(value)
        elif key in {"mirror", "cpw_ground_enabled", "line_via_enabled"}:
            kwargs[key] = bool(value)
        elif key == "ground_layers" and isinstance(value, list):
            kwargs[key] = tuple(str(item) for item in value)
        elif key.endswith("_mm") or key in {"line_w_mm", "line_l_mm"}:
            kwargs[key] = float(value)
        else:
            kwargs[key] = value
    return ConnectorLaunchParams(**kwargs)


def load_params(path: Path) -> ConnectorLaunchParams:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"connector params must be a JSON object: {path}")
    params_data = data.get("parameters", data)
    if not isinstance(params_data, dict):
        raise ValueError(f"connector params.parameters must be a JSON object: {path}")
    return params_from_mapping(params_data)


def launch_len(params: ConnectorLaunchParams) -> float:
    return params.pad_to_edge_mm + params.pin_pad_l_mm + params.launch_feed_l_mm + params.taper_l_mm


def total_len(params: ConnectorLaunchParams) -> float:
    return 2.0 * launch_len(params) + params.line_l_mm


def params_with_total_len(params: ConnectorLaunchParams, total_l_mm: float) -> ConnectorLaunchParams:
    line_l_mm = float(total_l_mm) - 2.0 * launch_len(params)
    if line_l_mm < params.min_fab_feature_mm:
        raise ValueError(
            f"total_l_mm={fmt(float(total_l_mm))} is too short for connector launch length "
            f"{fmt(launch_len(params))} mm each side"
        )
    return replace(params, line_l_mm=line_l_mm)


def _rect(name: str, x: float, y_center: float, w: float, h: float, *, role: str) -> Rect:
    return Rect(name=name, layer=LOGICAL_SIGNAL_LAYER, x=x, y=y_center - h / 2.0, w=w, h=h, metadata={"role": role})


def _ground_rect(name: str, x: float, y: float, w: float, h: float, *, role: str) -> Rect:
    return Rect(name=name, layer=LOGICAL_SIGNAL_LAYER, x=x, y=y, w=w, h=h, metadata={"role": role, "net": "GND"})


def _taper(name: str, x0: float, x1: float, w0: float, w1: float, *, role: str) -> Polygon:
    return Polygon(
        name=name,
        layer=LOGICAL_SIGNAL_LAYER,
        points=[
            (x0, -w0 / 2.0),
            (x1, -w1 / 2.0),
            (x1, w1 / 2.0),
            (x0, w0 / 2.0),
        ],
        metadata={"role": role},
    )


def _right_taper(name: str, x0: float, x1: float, w0: float, w1: float, *, role: str) -> Polygon:
    return Polygon(
        name=name,
        layer=LOGICAL_SIGNAL_LAYER,
        points=[
            (x0, -w0 / 2.0),
            (x1, -w1 / 2.0),
            (x1, w1 / 2.0),
            (x0, w0 / 2.0),
        ],
        metadata={"role": role},
    )


def board_height(params: ConnectorLaunchParams) -> float:
    return max(params.board_width_mm, params.pin_pad_w_mm + 2.0 * (params.gnd_clearance_mm + params.via_pad_d_mm + params.edge_margin_mm))


def _gcpw_ground_rail_pair(params: ConnectorLaunchParams, *, name: str, x0: float, x1: float, signal_w: float) -> list[Rect]:
    if not params.cpw_ground_enabled:
        return []
    board_h = board_height(params)
    half_board = board_h / 2.0
    y_inner = signal_w / 2.0 + params.cpw_ground_gap_mm
    rail_h = half_board - y_inner
    if x1 <= x0 or rail_h < params.min_fab_feature_mm:
        return []
    return [
        _ground_rect(f"{name}_top_ground", x0, y_inner, x1 - x0, rail_h, role="gcpw_top_ground"),
        _ground_rect(f"{name}_bottom_ground", x0, -half_board, x1 - x0, rail_h, role="gcpw_bottom_ground"),
    ]


def build_gcpw_ground_rails(params: ConnectorLaunchParams, segments: list[tuple[str, float, float, float]]) -> list[Rect]:
    rails: list[Rect] = []
    for name, x0, x1, signal_w in segments:
        rails.extend(_gcpw_ground_rail_pair(params, name=name, x0=x0, x1=x1, signal_w=signal_w))
    return rails


def build_line_via_fence(
    params: ConnectorLaunchParams,
    *,
    prefix: str,
    x0: float,
    x1: float,
    signal_w: float | None = None,
) -> list[Via]:
    if not params.line_via_enabled or params.line_via_pitch_mm <= 0.0 or x1 <= x0:
        return []
    width = params.line_w_mm if signal_w is None else signal_w
    y_abs = width / 2.0 + params.cpw_ground_gap_mm + params.via_pad_d_mm / 2.0
    start = x0 + params.line_via_pitch_mm / 2.0
    stop = x1 - params.line_via_pitch_mm / 2.0
    if start > stop:
        return []
    count = int((stop - start) // params.line_via_pitch_mm) + 1
    rows: list[Via] = []
    rows.extend(_via_row(prefix=f"{prefix}_top", x_start=start, y=y_abs, count=count, pitch=params.line_via_pitch_mm, params=params))
    rows.extend(_via_row(prefix=f"{prefix}_bottom", x_start=start, y=-y_abs, count=count, pitch=params.line_via_pitch_mm, params=params))
    return rows


def connector_region_bboxes(params: ConnectorLaunchParams) -> dict[str, list[float]]:
    left = [0.0, -params.board_width_mm / 2.0, launch_len(params), params.board_width_mm]
    right_x = launch_len(params) + params.line_l_mm
    right = [right_x, -params.board_width_mm / 2.0, launch_len(params), params.board_width_mm]
    return {"P1": left, "P2": right}


def single_connector_region_bboxes(params: ConnectorLaunchParams) -> dict[str, list[float]]:
    return {"P1": [0.0, -params.board_width_mm / 2.0, launch_len(params), params.board_width_mm]}


def port_locations(params: ConnectorLaunchParams) -> tuple[tuple[float, float], tuple[float, float]]:
    return (0.0, 0.0), (total_len(params), 0.0)


def single_connector_port_locations(params: ConnectorLaunchParams) -> tuple[tuple[float, float], tuple[float, float]]:
    return (0.0, 0.0), (launch_len(params) + params.line_l_mm, 0.0)


def build_signal_shapes(params: ConnectorLaunchParams) -> list[Rect | Polygon]:
    left_feed_len = params.pad_to_edge_mm + params.pin_pad_l_mm + params.launch_feed_l_mm
    left_taper_x0 = left_feed_len
    left_taper_x1 = left_taper_x0 + params.taper_l_mm
    line_x0 = left_taper_x1
    line_x1 = line_x0 + params.line_l_mm
    right_taper_x0 = line_x1
    right_taper_x1 = right_taper_x0 + params.taper_l_mm
    right_feed_len = params.pad_to_edge_mm + params.pin_pad_l_mm + params.launch_feed_l_mm

    return [
        _rect("input_feed", 0.0, 0.0, left_feed_len, params.taper_w_start_mm, role="connector_launch_signal"),
        _taper(
            "input_taper",
            left_taper_x0,
            left_taper_x1,
            params.taper_w_start_mm,
            params.taper_w_end_mm,
            role="connector_launch_taper",
        ),
        _rect("through_line", line_x0, 0.0, params.line_l_mm, params.line_w_mm, role="microstrip_50r"),
        _right_taper(
            "output_taper",
            right_taper_x0,
            right_taper_x1,
            params.taper_w_end_mm,
            params.taper_w_start_mm,
            role="connector_launch_taper",
        ),
        _rect("output_feed", right_taper_x1, 0.0, right_feed_len, params.taper_w_start_mm, role="connector_launch_signal"),
    ]


def dual_connector_gcpw_segments(params: ConnectorLaunchParams) -> list[tuple[str, float, float, float]]:
    left_l = launch_len(params)
    line_x0 = left_l
    line_x1 = line_x0 + params.line_l_mm
    return [
        ("p1_launch", 0.0, left_l, params.pin_pad_w_mm),
        ("center_line", line_x0, line_x1, params.line_w_mm),
        ("p2_launch", line_x1, line_x1 + left_l, params.pin_pad_w_mm),
    ]


def single_connector_gcpw_segments(params: ConnectorLaunchParams) -> list[tuple[str, float, float, float]]:
    left_l = launch_len(params)
    total_l = left_l + params.line_l_mm
    return [
        ("p1_launch", 0.0, left_l, params.pin_pad_w_mm),
        ("center_line", left_l, total_l, params.line_w_mm),
    ]


def baseline_gcpw_segments(params: ConnectorLaunchParams) -> list[tuple[str, float, float, float]]:
    return [("line", 0.0, total_len(params), params.line_w_mm)]


def _via_row(
    *,
    prefix: str,
    x_start: float,
    y: float,
    count: int,
    pitch: float,
    params: ConnectorLaunchParams,
) -> list[Via]:
    return [
        Via(
            name=f"{prefix}_{idx + 1}",
            layer=params.via_layer,
            x=x_start + idx * pitch,
            y=y,
            diameter=params.via_d_mm,
            pad_diameter=params.via_pad_d_mm,
            pad_layer=params.metal_layer,
            metadata={"role": "connector_ground_via", "row": prefix, "index": idx},
        )
        for idx in range(count)
    ]


def build_vias(params: ConnectorLaunchParams) -> list[Via]:
    if params.via_count <= 0:
        return []
    y_abs = params.pin_pad_w_mm / 2.0 + params.gnd_clearance_mm + params.via_pad_d_mm / 2.0
    left_x0 = params.fence_offset_mm
    right_x0 = total_len(params) - params.fence_offset_mm - (params.via_count - 1) * params.via_pitch_mm
    rows: list[Via] = []
    rows.extend(_via_row(prefix="ground_via_p1_top", x_start=left_x0, y=y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(_via_row(prefix="ground_via_p1_bottom", x_start=left_x0, y=-y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(_via_row(prefix="ground_via_p2_top", x_start=right_x0, y=y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(_via_row(prefix="ground_via_p2_bottom", x_start=right_x0, y=-y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(build_line_via_fence(params, prefix="gcpw_line_via", x0=launch_len(params), x1=launch_len(params) + params.line_l_mm))
    return rows


def build_single_connector_vias(params: ConnectorLaunchParams) -> list[Via]:
    if params.via_count <= 0:
        return []
    y_abs = params.pin_pad_w_mm / 2.0 + params.gnd_clearance_mm + params.via_pad_d_mm / 2.0
    left_x0 = params.fence_offset_mm
    rows: list[Via] = []
    rows.extend(_via_row(prefix="ground_via_p1_top", x_start=left_x0, y=y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(_via_row(prefix="ground_via_p1_bottom", x_start=left_x0, y=-y_abs, count=params.via_count, pitch=params.via_pitch_mm, params=params))
    rows.extend(build_line_via_fence(params, prefix="gcpw_line_via", x0=launch_len(params), x1=launch_len(params) + params.line_l_mm))
    return rows


def build_layout(params: ConnectorLaunchParams) -> Layout:
    p1, p2 = port_locations(params)
    board_h = board_height(params)
    boundary = Boundary(
        name="em_boundary",
        x=-params.edge_margin_mm,
        y=-board_h / 2.0,
        w=total_len(params) + 2.0 * params.edge_margin_mm,
        h=board_h,
    )
    ports = [
        Port(name="P1", number=1, x=p1[0], y=p1[1], width=params.pin_pad_w_mm, layer=params.metal_layer, orientation_deg=180.0),
        Port(name="P2", number=2, x=p2[0], y=p2[1], width=params.pin_pad_w_mm, layer=params.metal_layer, orientation_deg=0.0),
    ]
    metadata = {
        "generator": "simads.hfss.connector",
        "fixture_type": FIXTURE_TYPE,
        "topology": FIXTURE_TYPE,
        "connector_type": params.connector_type,
        "connector_route": params.connector_route,
        "connector_model_version": params.connector_model_version,
        "transmission_line_model": params.transmission_line_model,
        "cpw_ground_gap_mm": params.cpw_ground_gap_mm,
        "line_via_pitch_mm": params.line_via_pitch_mm,
        "line_w_mm": params.line_w_mm,
        "line_l_mm": params.line_l_mm,
        "reference_plane_offset_mm": params.reference_plane_offset_mm,
        "port_deembed_mm": params.port_deembed_mm,
        "connector_region_bbox_mm": connector_region_bboxes(params),
        "parameters": params.to_dict(),
        "layer_map_version": "microstrip-connector-logical-v1",
        "signal_layer": params.signal_layer,
        "reference_ground_layer": params.reference_ground_layer,
        "via_top_layer": params.via_top_layer,
        "via_bottom_layer": params.via_bottom_layer,
        "ground_layers": list(params.ground_layers),
        "ground_plane_name": params.ground_plane_name,
        "stackup_id": params.stackup_id,
        "stackup_token": params.stackup_token,
        "stackup_config": params.stackup_config,
    }
    return Layout(
        layout_id=params.name,
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name=params.boundary_layer, dxf_layer=params.boundary_layer),
        ],
        shapes=[boundary, *build_gcpw_ground_rails(params, dual_connector_gcpw_segments(params)), *build_signal_shapes(params), *build_vias(params)],
        ports=ports,
        metadata={key: value for key, value in metadata.items() if value is not None},
    )


def build_single_connector_layout(params: ConnectorLaunchParams) -> Layout:
    p1, p2 = single_connector_port_locations(params)
    total_l = p2[0]
    board_h = board_height(params)
    boundary = Boundary(
        name="em_boundary",
        x=-params.edge_margin_mm,
        y=-board_h / 2.0,
        w=total_l + 2.0 * params.edge_margin_mm,
        h=board_h,
    )
    left_feed_len = params.pad_to_edge_mm + params.pin_pad_l_mm + params.launch_feed_l_mm
    left_taper_x0 = left_feed_len
    left_taper_x1 = left_taper_x0 + params.taper_l_mm
    output_feed_l = max(params.launch_feed_l_mm, params.min_fab_feature_mm)
    center_l = params.line_l_mm - output_feed_l
    if center_l < params.min_fab_feature_mm:
        raise ValueError("single connector line_l_mm is too short")
    ports = [
        Port(name="P1", number=1, x=p1[0], y=p1[1], width=params.pin_pad_w_mm, layer=params.metal_layer, orientation_deg=180.0),
        Port(name="P2", number=2, x=p2[0], y=p2[1], width=params.line_w_mm, layer=params.metal_layer, orientation_deg=0.0),
    ]
    metadata = {
        "generator": "simads.hfss.connector",
        "fixture_type": SINGLE_CONNECTOR_FIXTURE_TYPE,
        "baseline_for_fixture_type": FIXTURE_TYPE,
        "topology": SINGLE_CONNECTOR_FIXTURE_TYPE,
        "connector_type": params.connector_type,
        "connector_route": params.connector_route,
        "connector_model_version": params.connector_model_version,
        "connector_side": "P1",
        "transmission_line_model": params.transmission_line_model,
        "cpw_ground_gap_mm": params.cpw_ground_gap_mm,
        "line_via_pitch_mm": params.line_via_pitch_mm,
        "line_w_mm": params.line_w_mm,
        "line_l_mm": params.line_l_mm,
        "total_len_mm": total_l,
        "reference_plane_offset_mm": params.reference_plane_offset_mm,
        "port_deembed_mm": params.port_deembed_mm,
        "connector_region_bbox_mm": single_connector_region_bboxes(params),
        "parameters": params.to_dict(),
        "layer_map_version": "microstrip-connector-logical-v1",
        "signal_layer": params.signal_layer,
        "reference_ground_layer": params.reference_ground_layer,
        "via_top_layer": params.via_top_layer,
        "via_bottom_layer": params.via_bottom_layer,
        "ground_layers": list(params.ground_layers),
        "ground_plane_name": params.ground_plane_name,
        "stackup_id": params.stackup_id,
        "stackup_token": params.stackup_token,
        "stackup_config": params.stackup_config,
    }
    return Layout(
        layout_id=params.name,
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name=params.boundary_layer, dxf_layer=params.boundary_layer),
        ],
        shapes=[
            boundary,
            *build_gcpw_ground_rails(params, single_connector_gcpw_segments(params)),
            _rect("input_feed", 0.0, 0.0, left_feed_len, params.taper_w_start_mm, role="connector_launch_signal"),
            _taper(
                "input_taper",
                left_taper_x0,
                left_taper_x1,
                params.taper_w_start_mm,
                params.taper_w_end_mm,
                role="connector_launch_taper",
            ),
            _rect("through_line", left_taper_x1, 0.0, center_l, params.line_w_mm, role="gcpw_50r"),
            _rect("output_feed", left_taper_x1 + center_l, 0.0, output_feed_l, params.line_w_mm, role="gcpw_50r"),
            *build_single_connector_vias(params),
        ],
        ports=ports,
        metadata={key: value for key, value in metadata.items() if value is not None},
    )


def build_microstrip_baseline_layout(params: ConnectorLaunchParams) -> Layout:
    p1, p2 = port_locations(params)
    board_h = board_height(params)
    boundary = Boundary(
        name="em_boundary",
        x=-params.edge_margin_mm,
        y=-board_h / 2.0,
        w=total_len(params) + 2.0 * params.edge_margin_mm,
        h=board_h,
    )
    lead_l = max(params.launch_feed_l_mm, params.min_fab_feature_mm)
    center_l = total_len(params) - 2.0 * lead_l
    if center_l < params.min_fab_feature_mm:
        raise ValueError("microstrip baseline total length is too short")
    ports = [
        Port(name="P1", number=1, x=p1[0], y=p1[1], width=params.line_w_mm, layer=params.metal_layer, orientation_deg=180.0),
        Port(name="P2", number=2, x=p2[0], y=p2[1], width=params.line_w_mm, layer=params.metal_layer, orientation_deg=0.0),
    ]
    metadata = {
        "generator": "simads.hfss.connector",
        "fixture_type": BASELINE_FIXTURE_TYPE,
        "baseline_for_fixture_type": FIXTURE_TYPE,
        "topology": BASELINE_FIXTURE_TYPE,
        "transmission_line_model": params.transmission_line_model,
        "cpw_ground_gap_mm": params.cpw_ground_gap_mm,
        "line_via_pitch_mm": params.line_via_pitch_mm,
        "line_w_mm": params.line_w_mm,
        "line_l_mm": total_len(params),
        "reference_plane_offset_mm": params.reference_plane_offset_mm,
        "port_deembed_mm": params.port_deembed_mm,
        "parameters": params.to_dict(),
        "layer_map_version": "microstrip-connector-logical-v1",
        "signal_layer": params.signal_layer,
        "reference_ground_layer": params.reference_ground_layer,
        "via_top_layer": params.via_top_layer,
        "via_bottom_layer": params.via_bottom_layer,
        "ground_layers": list(params.ground_layers),
        "ground_plane_name": params.ground_plane_name,
        "stackup_id": params.stackup_id,
        "stackup_token": params.stackup_token,
        "stackup_config": params.stackup_config,
    }
    return Layout(
        layout_id=f"{params.name}_baseline",
        units="mm",
        layers=[
            LayerMap(name=params.metal_layer, dxf_layer=params.metal_layer),
            LayerMap(name=params.via_layer, dxf_layer=params.via_layer),
            LayerMap(name=params.boundary_layer, dxf_layer=params.boundary_layer),
        ],
        shapes=[
            boundary,
            *build_gcpw_ground_rails(params, baseline_gcpw_segments(params)),
            _rect("input_feed", 0.0, 0.0, lead_l, params.line_w_mm, role="gcpw_50r_baseline"),
            _rect("through_line", lead_l, 0.0, center_l, params.line_w_mm, role="gcpw_50r_baseline"),
            _rect("output_feed", lead_l + center_l, 0.0, lead_l, params.line_w_mm, role="gcpw_50r_baseline"),
            *build_line_via_fence(params, prefix="gcpw_line_via", x0=0.0, x1=total_len(params)),
        ],
        ports=ports,
        metadata={key: value for key, value in metadata.items() if value is not None},
    )


def validate_connector_layout(layout: Layout, params: ConnectorLaunchParams) -> list[ConnectorLayoutCheck]:
    checks: list[ConnectorLayoutCheck] = []

    def add(name: str, ok: bool, message: str) -> None:
        checks.append(ConnectorLayoutCheck(name, ok, message))

    numeric = params.to_dict()
    for key, value in numeric.items():
        if key.endswith("_mm") and isinstance(value, (float, int)):
            add(f"params.{key}", float(value) >= 0.0, f"{key} must be non-negative")
    add("params.line_l_mm", params.line_l_mm >= 5.0, "line_l_mm must leave a stable 50R baseline section")
    add("params.line_w_mm", params.line_w_mm >= params.min_fab_feature_mm, "line_w_mm must satisfy min fab feature")
    add("params.taper_l_mm", params.taper_l_mm >= params.min_fab_feature_mm, "taper_l_mm must satisfy min fab feature")
    add("params.gnd_clearance_mm", params.gnd_clearance_mm >= params.min_fab_feature_mm, "gnd_clearance_mm must satisfy min fab feature")
    add("params.via_count", params.via_count >= 0, "via_count must be non-negative")
    if params.via_count > 1:
        add("params.via_pitch_mm", params.via_pitch_mm >= params.via_pad_d_mm + params.min_fab_feature_mm, "via_pitch_mm must separate via pads")
    add(
        "layout.fixture_type",
        layout.metadata.get("fixture_type") in {FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE},
        f"fixture_type must be {FIXTURE_TYPE} or {SINGLE_CONNECTOR_FIXTURE_TYPE}",
    )
    add("layout.ports", [port.name for port in layout.ports] == ["P1", "P2"], "layout must contain P1/P2 ports")
    features = [min_feature(shape) for shape in layout.shapes if not isinstance(shape, Boundary)]
    add("layout.min_feature", min(features) >= params.min_fab_feature_mm if features else False, "all generated shapes must satisfy min fab feature")
    return checks


def assert_connector_layout_valid(layout: Layout, params: ConnectorLaunchParams) -> None:
    failed = [check for check in validate_connector_layout(layout, params) if not check.ok]
    if failed:
        detail = "; ".join(f"{check.name}: {check.message}" for check in failed)
        raise ValueError(detail)


def write_outputs(params: ConnectorLaunchParams, out_dir: Path) -> dict[str, Path]:
    return write_fixture_outputs(params, out_dir, fixture_type=FIXTURE_TYPE)


def write_fixture_outputs(params: ConnectorLaunchParams, out_dir: Path, *, fixture_type: str = FIXTURE_TYPE) -> dict[str, Path]:
    if fixture_type == FIXTURE_TYPE:
        layout = build_layout(params)
        assert_connector_layout_valid(layout, params)
    elif fixture_type == SINGLE_CONNECTOR_FIXTURE_TYPE:
        layout = build_single_connector_layout(params)
        assert_connector_layout_valid(layout, params)
    elif fixture_type == BASELINE_FIXTURE_TYPE:
        layout = build_microstrip_baseline_layout(params)
    else:
        raise ValueError(f"unsupported connector fixture type: {fixture_type}")
    out_dir.mkdir(parents=True, exist_ok=True)
    layout_json = out_dir / f"{layout.layout_id}_layout.json"
    params_json = out_dir / f"{layout.layout_id}_params.json"
    svg = out_dir / f"{layout.layout_id}.svg"
    write_layout_json(layout_json, layout)
    params_json.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "fixture_type": fixture_type,
                "parameters": params.to_dict(),
                "ports": {
                    "P1": list((single_connector_port_locations(params) if fixture_type == SINGLE_CONNECTOR_FIXTURE_TYPE else port_locations(params))[0]),
                    "P2": list((single_connector_port_locations(params) if fixture_type == SINGLE_CONNECTOR_FIXTURE_TYPE else port_locations(params))[1]),
                },
                "derived": {
                    "launch_len_mm": launch_len(params),
                    "total_len_mm": single_connector_port_locations(params)[1][0] if fixture_type == SINGLE_CONNECTOR_FIXTURE_TYPE else total_len(params),
                    "connector_region_bbox_mm": single_connector_region_bboxes(params) if fixture_type == SINGLE_CONNECTOR_FIXTURE_TYPE else connector_region_bboxes(params),
                },
                "layout": to_dict(layout),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_svg(svg, layout, title=params.name)
    return {"layout_json": layout_json, "params": params_json, "svg": svg}


def load_stackup_params(params: ConnectorLaunchParams, stackup_config: Path | None) -> ConnectorLaunchParams:
    if stackup_config is None:
        return params
    return params_with_stackup_config(params, load_stackup_config(stackup_config), config_path=stackup_config)


__all__ = [
    "BOUNDARY_LAYER",
    "BASELINE_FIXTURE_TYPE",
    "FIXTURE_TYPE",
    "SINGLE_CONNECTOR_FIXTURE_TYPE",
    "LOGICAL_SIGNAL_LAYER",
    "LOGICAL_VIA_LAYER",
    "ConnectorLaunchParams",
    "ConnectorLayoutCheck",
    "assert_connector_layout_valid",
    "build_layout",
    "build_microstrip_baseline_layout",
    "build_single_connector_layout",
    "build_gcpw_ground_rails",
    "build_line_via_fence",
    "build_signal_shapes",
    "build_single_connector_vias",
    "build_vias",
    "connector_region_bboxes",
    "dual_connector_gcpw_segments",
    "launch_len",
    "load_params",
    "load_stackup_params",
    "params_from_mapping",
    "params_with_total_len",
    "params_with_stackup_config",
    "port_locations",
    "single_connector_port_locations",
    "single_connector_gcpw_segments",
    "single_connector_region_bboxes",
    "total_len",
    "validate_connector_layout",
    "write_outputs",
    "write_fixture_outputs",
]
