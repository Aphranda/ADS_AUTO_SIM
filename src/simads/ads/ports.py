"""ADS layout port specification and pin placement helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from simads.ads.layout import load_p1_p2_locations


@dataclass(frozen=True)
class AdsPortReference:
    net_name: str = ""
    layer: str = "cond2"
    point: tuple[float, float] | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AdsLayoutPort:
    name: str
    signal_net: str
    signal_layer: str
    signal_point: tuple[float, float]
    angle_deg: float
    reference: AdsPortReference

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["reference"] = self.reference.to_dict()
        return data


def build_two_port_reference_specs(
    p1: tuple[float, float],
    p2: tuple[float, float],
    *,
    signal_layer: str,
    reference_layer: str,
    reference_net: str = "",
) -> tuple[AdsLayoutPort, AdsLayoutPort]:
    """Build the canonical ADS two-port spec used by layout and EM setup code."""
    return (
        AdsLayoutPort(
            name="P1",
            signal_net="P1",
            signal_layer=signal_layer,
            signal_point=p1,
            angle_deg=180.0,
            reference=AdsPortReference(net_name=reference_net, layer=reference_layer, point=p1),
        ),
        AdsLayoutPort(
            name="P2",
            signal_net="P2",
            signal_layer=signal_layer,
            signal_point=p2,
            angle_deg=0.0,
            reference=AdsPortReference(net_name=reference_net, layer=reference_layer, point=p2),
        ),
    )


def resolve_next_reference_layer(signal_layer: str, ground_layers: tuple[str, ...]) -> str:
    """Resolve the ADS port reference layer as the first GND layer below signal."""
    for layer in ground_layers:
        if layer != signal_layer:
            return layer
    return signal_layer


def load_two_port_reference_specs(
    params_path: Path,
    *,
    signal_layer: str,
    reference_layer: str,
    reference_net: str = "",
) -> tuple[AdsLayoutPort, AdsLayoutPort]:
    p1, p2 = load_p1_p2_locations(params_path)
    return build_two_port_reference_specs(
        p1,
        p2,
        signal_layer=signal_layer,
        reference_layer=reference_layer,
        reference_net=reference_net,
    )


def _add_port_pin_with_reference(
    design: Any,
    term: Any,
    port: AdsLayoutPort,
) -> None:
    signal_layer_id = design.create_layer_id(port.signal_layer)
    signal_dot = design.add_dot(signal_layer_id, port.signal_point)
    try:
        design.add_pin(term, [signal_dot], angle=port.angle_deg)
    except TypeError:
        design.add_pin(term, [signal_dot])


def place_layout_pins(
    design: Any,
    db_uu: Any,
    ports: tuple[AdsLayoutPort, ...],
    *,
    log: Callable[[str], None] | None = None,
) -> list[dict[str, object]]:
    """Place ADS layout pins on the signal layer; EM setup owns the reference layer."""
    term_type = getattr(getattr(db_uu, "TermType", object), "INPUT_OUTPUT", None)
    placed: list[dict[str, object]] = []

    for port in ports:
        if log:
            reference_label = f"{port.reference.layer}:{port.reference.point}"
            if port.reference.net_name:
                reference_label = f"{port.reference.net_name}@{reference_label}"
            log(
                "Adding ADS layout pin "
                f"{port.name} at {port.signal_point} angle={port.angle_deg}; "
                f"reference={reference_label}"
            )
        net = design.find_or_add_net(port.signal_net)
        if term_type is None:
            try:
                term = design.add_term(net, port.name)
            except RuntimeError as exc:
                if "already exists" not in str(exc):
                    raise
                if log:
                    log(f"Pin/terminal {port.name} already exists; skipping")
                placed.append({**port.to_dict(), "status": "already_exists"})
                continue
        else:
            try:
                term = design.add_term(net, port.name, term_type)
            except RuntimeError as exc:
                if "already exists" not in str(exc):
                    raise
                if log:
                    log(f"Pin/terminal {port.name} already exists; skipping")
                placed.append({**port.to_dict(), "status": "already_exists"})
                continue

        _add_port_pin_with_reference(design, term, port)
        placed.append({**port.to_dict(), "status": "created"})

    return placed


__all__ = [
    "AdsLayoutPort",
    "AdsPortReference",
    "build_two_port_reference_specs",
    "load_two_port_reference_specs",
    "place_layout_pins",
    "resolve_next_reference_layer",
]
