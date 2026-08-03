"""Small serializable specs shared by ADS, HFSS, and NN workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _path_to_str(value: Path | str | None) -> str | None:
    if value is None:
        return None
    return str(value)


@dataclass(frozen=True)
class SweepSpec:
    start_ghz: float
    stop_ghz: float
    points: int
    sweep_type: str = "Interpolating"
    adaptive_frequency_ghz: float | None = None

    def __post_init__(self) -> None:
        if self.points < 2:
            raise ValueError("SweepSpec.points must be >= 2")
        if self.stop_ghz <= self.start_ghz:
            raise ValueError("SweepSpec.stop_ghz must be greater than start_ghz")

    @property
    def spacing_ghz(self) -> float:
        return (self.stop_ghz - self.start_ghz) / (self.points - 1)

    @property
    def spacing_mhz(self) -> float:
        return self.spacing_ghz * 1000.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["spacing_ghz"] = self.spacing_ghz
        data["spacing_mhz"] = self.spacing_mhz
        return data


@dataclass(frozen=True)
class StackupSpec:
    stackup_id: str
    dielectric_material: str
    er: float
    loss_tangent: float
    dielectric_height_mm: float
    copper_thickness_mm: float
    top_layer: str = "TOP"
    dielectric_layer: str = "FR4_CORE"
    bottom_layer: str = "GND"
    config_path: str | None = None
    signal_to_reference_height_mm: float | None = None
    total_thickness_mm: float | None = None
    layers_bottom_to_top: list[dict[str, Any]] = field(default_factory=list)
    geometry: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PortSpec:
    name: str
    port_type: str
    signal_primitive: str | None = None
    signal_edge: int | None = None
    signal_side: str | None = None
    reference_primitive: str | None = None
    reference_edge: int | None = None
    reference_side: str | None = None
    reference_name: str | None = None
    impedance_ohm: float = 50.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SimulationResultSpec:
    simulator: str
    project: Path | str | None = None
    design: str | None = None
    s2p: Path | str | None = None
    trace_csv: Path | str | None = None
    score_csv: Path | str | None = None
    svg: Path | str | None = None
    summary_csv: Path | str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulator": self.simulator,
            "project": _path_to_str(self.project),
            "design": self.design,
            "s2p": _path_to_str(self.s2p),
            "trace_csv": _path_to_str(self.trace_csv),
            "score_csv": _path_to_str(self.score_csv),
            "svg": _path_to_str(self.svg),
            "summary_csv": _path_to_str(self.summary_csv),
        }
