"""Device plugin registry for layout automation.

Device plugins describe topology-specific parameters and adapter entry points.
They must not open ADS workspaces or start simulations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, Iterable

from simads.optimizer import DEFAULT_INTERDIGITAL_FR4_BOUNDS, INTERDIGITAL_FR4_PARAM_COLUMNS


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    unit: str = ""
    required: bool = True
    minimum: float | None = None
    maximum: float | None = None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "required": self.required,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "description": self.description,
        }


@dataclass(frozen=True)
class DevicePlugin:
    device_id: str
    family: str
    parameter_specs: tuple[ParameterSpec, ...]
    port_names: tuple[str, ...] = ("P1", "P2")
    default_layers: dict[str, str] = field(default_factory=dict)
    default_target_profiles: tuple[str, ...] = ()
    optimizer_bounds: dict[str, tuple[float, float]] = field(default_factory=dict)
    builder_module: str | None = None
    params_class: str | None = None
    layout_builder: str | None = None
    outputs_writer: str | None = None

    def parameter_schema(self) -> list[dict[str, Any]]:
        return [spec.to_dict() for spec in self.parameter_specs]

    def required_parameters(self) -> set[str]:
        return {spec.name for spec in self.parameter_specs if spec.required}

    def validate_parameter_row(self, row: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for spec in self.parameter_specs:
            value = row.get(spec.name)
            if value in (None, ""):
                if spec.required:
                    errors.append(f"missing required parameter: {spec.name}")
                continue
            if spec.minimum is None and spec.maximum is None:
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                errors.append(f"parameter is not numeric: {spec.name}")
                continue
            if spec.minimum is not None and number < spec.minimum:
                errors.append(f"parameter below minimum: {spec.name} < {spec.minimum}")
            if spec.maximum is not None and number > spec.maximum:
                errors.append(f"parameter above maximum: {spec.name} > {spec.maximum}")
        return errors

    def resolve_callable(self, name: str) -> Callable[..., Any]:
        if self.builder_module is None:
            raise ValueError(f"device has no builder module: {self.device_id}")
        target_name = getattr(self, name)
        if not target_name:
            raise ValueError(f"device has no {name}: {self.device_id}")
        module = importlib.import_module(self.builder_module)
        return getattr(module, target_name)


class DeviceRegistry:
    def __init__(self, plugins: Iterable[DevicePlugin] = ()) -> None:
        self._plugins: dict[str, DevicePlugin] = {}
        for plugin in plugins:
            self.register(plugin)

    def register(self, plugin: DevicePlugin) -> None:
        if plugin.device_id in self._plugins:
            raise ValueError(f"duplicate device plugin: {plugin.device_id}")
        self._plugins[plugin.device_id] = plugin

    def get(self, device_id: str) -> DevicePlugin:
        try:
            return self._plugins[device_id]
        except KeyError as exc:
            raise KeyError(f"unknown device plugin: {device_id}") from exc

    def list_ids(self) -> list[str]:
        return sorted(self._plugins)


def interdigital_filter_plugin() -> DevicePlugin:
    specs = [
        ParameterSpec(name="name", description="Candidate/layout name."),
        ParameterSpec(name="order", required=False, minimum=1, description="Filter order."),
        ParameterSpec(name="substrate", required=False, description="Substrate material label."),
        ParameterSpec(name="er", required=False, minimum=1.0, description="Relative dielectric constant."),
        ParameterSpec(name="dielectric_height_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="copper_thickness_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="lower_cutoff_ghz", required=False, unit="GHz", minimum=0.0),
        ParameterSpec(name="upper_cutoff_ghz", required=False, unit="GHz", minimum=0.0),
        ParameterSpec(name="passband_ripple_db", required=False, unit="dB", minimum=0.0),
        ParameterSpec(name="z0_ohm", required=False, unit="ohm", minimum=0.0),
        *[ParameterSpec(name=name, unit="mm", minimum=0.0) for name in INTERDIGITAL_FR4_PARAM_COLUMNS],
        ParameterSpec(name="resonator_w_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="resonator_l_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="tap_from_bottom_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="end_gap_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="gaps_mm", required=False, unit="mm", description="Order-1 gap sequence."),
        ParameterSpec(name="boundary_margin_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="min_fab_feature_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="metal_layer", required=False),
        ParameterSpec(name="via_layer", required=False),
        ParameterSpec(name="via_pad_mm", required=False, unit="mm", minimum=0.0),
        ParameterSpec(name="via_half_outside", required=False, description="Boolean geometry option."),
        ParameterSpec(name="via_pad_outside", required=False, description="Boolean geometry option."),
    ]
    return DevicePlugin(
        device_id="filter.interdigital",
        family="filter",
        parameter_specs=tuple(specs),
        port_names=("P1", "P2"),
        default_layers={"metal": "cond", "via": "pcvia1", "boundary": "EM_BOUNDARY"},
        default_target_profiles=("fr4_25db_rl6", "fr4_25db_rl10", "ro4350_strict"),
        optimizer_bounds=dict(DEFAULT_INTERDIGITAL_FR4_BOUNDS),
        builder_module="generate_interdigital_filter_layout",
        params_class="FilterParams",
        layout_builder="build_layout",
        outputs_writer="write_outputs",
    )


def folded_sir_filter_plugin() -> DevicePlugin:
    names = [
        "substrate",
        "er",
        "dielectric_height_mm",
        "copper_thickness_mm",
        "lower_cutoff_ghz",
        "upper_cutoff_ghz",
        "f0_ghz",
        "order",
        "z0_ohm",
        "feed_w_mm",
        "feed_len_mm",
        "feed_gap_t1_mm",
        "feed_tip_w_mm",
        "feed_overlap_mm",
        "lower_w1_mm",
        "lower_arm_l1_mm",
        "lower_span_l2_mm",
        "lower_top_bridge_w_mm",
        "lower_bottom_l2_mm",
        "via_diameter_mm",
        "via_pad_size_mm",
        "via_edge_clearance_mm",
        "via_offset_d1_mm",
        "upper_w1_mm",
        "upper_w2_mm",
        "upper_fold_h_mm",
        "upper_left_l3_mm",
        "upper_right_l4_mm",
        "upper_margin_x_mm",
        "main_gap_s1_mm",
        "side_gap_s2_mm",
        "fold_offset_d2_mm",
        "boundary_margin_mm",
        "min_fab_feature_mm",
        "metal_layer",
        "via_layer",
    ]
    specs = [ParameterSpec(name="name", description="Candidate/layout name.")]
    specs.extend(ParameterSpec(name=name, required=False, unit="mm" if name.endswith("_mm") else "") for name in names)
    return DevicePlugin(
        device_id="filter.folded_sir",
        family="filter",
        parameter_specs=tuple(specs),
        port_names=("P1", "P2"),
        default_layers={"metal": "cond", "via": "pcvia1", "boundary": "EM_BOUNDARY"},
        default_target_profiles=("fr4_25db_rl6", "fr4_25db_rl10", "ro4350_strict"),
        builder_module="generate_folded_sir_bpf_layout",
        params_class="FoldedSirParams",
        layout_builder="build_layout",
        outputs_writer="write_outputs",
    )


def hilo_sir_filter_plugin() -> DevicePlugin:
    names = [
        "substrate",
        "er",
        "dielectric_height_mm",
        "copper_thickness_mm",
        "lower_cutoff_ghz",
        "upper_cutoff_ghz",
        "order",
        "z0_ohm",
        "z_high_ohm",
        "z_low_ohm",
        "feed_w_mm",
        "high_w_mm",
        "low_w_mm",
        "arm_l_mm",
        "bridge_l_mm",
        "inner_gap_mm",
        "coupling_gap_mm",
        "coupling_gaps_mm",
        "feed_gap_mm",
        "feed_overlap_mm",
        "feed_len_mm",
        "boundary_margin_mm",
        "min_fab_feature_mm",
        "metal_layer",
    ]
    specs = [ParameterSpec(name="name", description="Candidate/layout name.")]
    specs.extend(ParameterSpec(name=name, required=False, unit="mm" if name.endswith("_mm") else "") for name in names)
    return DevicePlugin(
        device_id="filter.hilo_sir",
        family="filter",
        parameter_specs=tuple(specs),
        port_names=("P1", "P2"),
        default_layers={"metal": "cond", "boundary": "EM_BOUNDARY"},
        default_target_profiles=("fr4_25db_rl6", "fr4_25db_rl10", "ro4350_strict"),
        builder_module="generate_hilo_sir_bpf_layout",
        params_class="HiloSirParams",
        layout_builder="build_layout",
        outputs_writer="write_outputs",
    )


def stub_filter_plugin() -> DevicePlugin:
    names = [
        "substrate",
        "er",
        "dielectric_height_mm",
        "copper_thickness_mm",
        "lower_cutoff_ghz",
        "upper_cutoff_ghz",
        "z0_ohm",
        "main_segment_count",
        "section_l_mm",
        "stub_l_mm",
        "main_w_mm",
        "top_stub_w_mm",
        "bottom_stub_w_mm",
        "feed_len_mm",
        "boundary_margin_mm",
        "via_diameter_mm",
        "via_edge_clearance_mm",
        "min_fab_feature_mm",
        "metal_layer",
        "via_layer",
    ]
    specs = [ParameterSpec(name="name", description="Candidate/layout name.")]
    specs.extend(ParameterSpec(name=name, required=False, unit="mm" if name.endswith("_mm") else "") for name in names)
    return DevicePlugin(
        device_id="filter.stub",
        family="filter",
        parameter_specs=tuple(specs),
        port_names=("P1", "P2"),
        default_layers={"metal": "cond", "via": "pcvia1", "boundary": "EM_BOUNDARY"},
        default_target_profiles=("fr4_25db_rl6", "fr4_25db_rl10", "ro4350_strict"),
        builder_module="generate_stub_bpf_layout",
        params_class="StubBpfParams",
        layout_builder="build_layout",
        outputs_writer="write_outputs",
    )


def build_default_registry() -> DeviceRegistry:
    return DeviceRegistry(
        [
            interdigital_filter_plugin(),
            folded_sir_filter_plugin(),
            hilo_sir_filter_plugin(),
            stub_filter_plugin(),
        ]
    )


DEFAULT_REGISTRY = build_default_registry()


def get_device(device_id: str) -> DevicePlugin:
    return DEFAULT_REGISTRY.get(device_id)


def list_devices() -> list[str]:
    return DEFAULT_REGISTRY.list_ids()
