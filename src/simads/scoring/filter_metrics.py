"""Detailed S2P metrics for band-pass filter optimization."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from .touchstone import SParameterNetwork, db, read_sparameter_network


DEFAULT_MARKERS_GHZ = (5.0, 6.0, 6.3, 7.0, 8.0, 9.0, 10.0)


@dataclass(frozen=True)
class BandWindow:
    start_ghz: float = 6.0
    stop_ghz: float = 8.0


def _interp_complex(network: SParameterNetwork, freq_ghz: float, name: str) -> complex:
    key = name.strip().lower()
    ordered = sorted(network.samples, key=lambda row: float(row["freq_ghz"]))
    if not ordered:
        raise ValueError(f"no samples in network: {network.path}")
    if freq_ghz <= float(ordered[0]["freq_ghz"]):
        return complex(ordered[0][key])
    if freq_ghz >= float(ordered[-1]["freq_ghz"]):
        return complex(ordered[-1][key])
    for left, right in zip(ordered, ordered[1:]):
        left_f = float(left["freq_ghz"])
        right_f = float(right["freq_ghz"])
        if left_f <= freq_ghz <= right_f:
            ratio = (freq_ghz - left_f) / (right_f - left_f)
            return complex(left[key]) + ratio * (complex(right[key]) - complex(left[key]))
    return complex(ordered[-1][key])


def _impedance_from_gamma(gamma: complex, z0_ohm: float) -> dict[str, float]:
    denominator = 1.0 - gamma
    if abs(denominator) < 1e-12:
        return {"real_ohm": math.inf, "imag_ohm": math.inf, "mag_ohm": math.inf}
    impedance = z0_ohm * (1.0 + gamma) / denominator
    return {
        "real_ohm": impedance.real,
        "imag_ohm": impedance.imag,
        "mag_ohm": abs(impedance),
    }


def _vswr(gamma: complex) -> float:
    mag = min(abs(gamma), 0.999999)
    return (1.0 + mag) / (1.0 - mag)


def _unwrap(phases: list[float]) -> list[float]:
    if not phases:
        return []
    unwrapped = [phases[0]]
    offset = 0.0
    previous = phases[0]
    for phase in phases[1:]:
        delta = phase - previous
        if delta > math.pi:
            offset -= 2.0 * math.pi
        elif delta < -math.pi:
            offset += 2.0 * math.pi
        unwrapped.append(phase + offset)
        previous = phase
    return unwrapped


def _group_delay_ns(network: SParameterNetwork, name: str) -> list[tuple[float, float]]:
    freqs = network.frequency_ghz
    values = network.s(name)
    if len(freqs) < 3:
        return []
    phases = _unwrap([math.atan2(value.imag, value.real) for value in values])
    result: list[tuple[float, float]] = []
    for index in range(1, len(freqs) - 1):
        left_f_hz = freqs[index - 1] * 1e9
        right_f_hz = freqs[index + 1] * 1e9
        delta_omega = 2.0 * math.pi * (right_f_hz - left_f_hz)
        if delta_omega == 0.0:
            continue
        gd_s = -(phases[index + 1] - phases[index - 1]) / delta_omega
        result.append((freqs[index], gd_s * 1e9))
    return result


def _band_values(network: SParameterNetwork, window: BandWindow, name: str) -> list[tuple[float, float]]:
    return [
        (float(row["freq_ghz"]), db(complex(row[name])))
        for row in network.samples
        if window.start_ghz <= float(row["freq_ghz"]) <= window.stop_ghz
    ]


def _extreme(values: list[tuple[float, float]], *, choose_max: bool) -> dict[str, float]:
    if not values:
        return {"freq_ghz": math.nan, "db": math.nan}
    freq, value = (max if choose_max else min)(values, key=lambda item: item[1])
    return {"freq_ghz": freq, "db": value}


def _minus3db_band(network: SParameterNetwork, peak_db: float, name: str) -> list[float | None]:
    threshold = peak_db - 3.0
    above = [(float(row["freq_ghz"]), db(complex(row[name]))) for row in network.samples if db(complex(row[name])) >= threshold]
    if not above:
        return [None, None]
    return [above[0][0], above[-1][0]]


def _read_tdr_summary(path: Path, early_max_ns: float) -> dict[str, Any]:
    rows: list[dict[str, float]] = []
    with path.open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            rows.append({key: float(value) for key, value in row.items()})
    if not rows:
        return {}

    def point(column: str, *, choose_max: bool, selected: list[dict[str, float]]) -> dict[str, float]:
        row = (max if choose_max else min)(selected, key=lambda item: item[column])
        return {"time_ns": row["time_ns"], "z_ohm": row[column]}

    early = [row for row in rows if row["time_ns"] <= early_max_ns]
    payload: dict[str, Any] = {}
    for port, column in (("s11", "s11_z_ohm"), ("s22", "s22_z_ohm")):
        payload[f"{port}_min"] = point(column, choose_max=False, selected=rows)
        payload[f"{port}_max"] = point(column, choose_max=True, selected=rows)
        if early:
            payload[f"{port}_early_min"] = point(column, choose_max=False, selected=early)
    return payload


def summarize_filter_s2p(
    s2p: Path,
    *,
    passband: BandWindow = BandWindow(),
    markers_ghz: tuple[float, ...] = DEFAULT_MARKERS_GHZ,
    tdr_csv: Path | None = None,
    tdr_early_max_ns: float = 0.20,
    z0_ohm: float = 50.0,
) -> dict[str, Any]:
    network = read_sparameter_network(s2p).require_nports(2, system="filter")
    s21_band = _band_values(network, passband, "s21")
    s11_band = _band_values(network, passband, "s11")
    s22_band = _band_values(network, passband, "s22")
    if not s21_band:
        raise ValueError(f"no passband samples in {passband.start_ghz:g}-{passband.stop_ghz:g} GHz: {s2p}")

    all_s21 = [(float(row["freq_ghz"]), db(complex(row["s21"]))) for row in network.samples]
    peak = _extreme(all_s21, choose_max=True)
    pass_min = _extreme(s21_band, choose_max=False)
    pass_max = _extreme(s21_band, choose_max=True)
    worst_s11 = _extreme(s11_band, choose_max=True)
    worst_s22 = _extreme(s22_band, choose_max=True)
    group_delay = [
        item for item in _group_delay_ns(network, "s21") if passband.start_ghz <= item[0] <= passband.stop_ghz
    ]
    gd_values = [value for _, value in group_delay]

    markers: dict[str, Any] = {}
    for freq in markers_ghz:
        s11 = _interp_complex(network, freq, "s11")
        s21 = _interp_complex(network, freq, "s21")
        s12 = _interp_complex(network, freq, "s12")
        s22 = _interp_complex(network, freq, "s22")
        label = f"{freq:g}G"
        markers[label] = {
            "freq_ghz": freq,
            "s11_db": db(s11),
            "s21_db": db(s21),
            "s12_db": db(s12),
            "s22_db": db(s22),
            "s11_vswr": _vswr(s11),
            "s22_vswr": _vswr(s22),
            "zin_from_s11": _impedance_from_gamma(s11, z0_ohm),
            "zout_from_s22": _impedance_from_gamma(s22, z0_ohm),
        }

    payload: dict[str, Any] = {
        "source_s2p": str(s2p),
        "sample_count": len(network.samples),
        "frequency_range_ghz": [min(network.frequency_ghz), max(network.frequency_ghz)],
        "markers": markers,
        "s21_peak": peak,
        "minus3db_threshold_db": peak["db"] - 3.0,
        "minus3db_band_ghz": _minus3db_band(network, peak["db"], "s21"),
        "passband_ghz": [passband.start_ghz, passband.stop_ghz],
        "passband_s21_min": pass_min,
        "passband_s21_max": pass_max,
        "passband_s21_avg_db": sum(value for _, value in s21_band) / len(s21_band),
        "passband_s21_ripple_db": pass_max["db"] - pass_min["db"],
        "passband_worst_s11": worst_s11,
        "passband_worst_s22": worst_s22,
        "passband_worst_return_db": max(worst_s11["db"], worst_s22["db"]),
        "passband_group_delay_ns": {
            "min": min(gd_values) if gd_values else math.nan,
            "max": max(gd_values) if gd_values else math.nan,
            "avg": sum(gd_values) / len(gd_values) if gd_values else math.nan,
            "pkpk": (max(gd_values) - min(gd_values)) if gd_values else math.nan,
        },
        "stopband_s21_db": {
            "5g": network.interp_db(5.0, "s21"),
            "9g": network.interp_db(9.0, "s21"),
            "10g": network.interp_db(10.0, "s21"),
        },
    }
    if tdr_csv is not None and tdr_csv.exists():
        payload["tdr"] = _read_tdr_summary(tdr_csv, tdr_early_max_ns)
    return payload


__all__ = ["BandWindow", "DEFAULT_MARKERS_GHZ", "summarize_filter_s2p"]
