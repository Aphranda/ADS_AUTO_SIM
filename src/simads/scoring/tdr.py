"""Band-limited TDR helpers derived from Touchstone reflection data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np

from simads.scoring.connector import read_s2p


@dataclass(frozen=True)
class TdrPoint:
    time_ns: float
    s11_rho: float
    s11_z_ohm: float
    s22_rho: float
    s22_z_ohm: float


def _next_power_of_two(value: int) -> int:
    if value <= 1:
        return 1
    return 1 << (value - 1).bit_length()


def _median_step(values: list[float]) -> float:
    steps = [right - left for left, right in zip(values, values[1:]) if right > left]
    if not steps:
        raise ValueError("Touchstone data must contain at least two increasing frequency points")
    return float(np.median(np.array(steps, dtype=float)))


def _reflection_step_response(
    freqs_ghz: list[float],
    gamma: list[complex],
    *,
    n_fft: int | None = None,
    low_frequency_fill: str = "hold",
) -> tuple[np.ndarray, np.ndarray]:
    if len(freqs_ghz) != len(gamma):
        raise ValueError("frequency and gamma arrays must have the same length")
    if len(freqs_ghz) < 2:
        raise ValueError("TDR needs at least two Touchstone samples")

    df_ghz = _median_step(freqs_ghz)
    if df_ghz <= 0.0:
        raise ValueError(f"invalid frequency step: {df_ghz:g} GHz")

    max_bin = max(1, int(round(max(freqs_ghz) / df_ghz)))
    size = n_fft or max(2048, _next_power_of_two(2 * (max_bin + 1)))
    if size // 2 < max_bin:
        raise ValueError(f"n_fft={size} is too small for {max(freqs_ghz):g} GHz with df={df_ghz:g} GHz")

    spectrum = np.zeros(size // 2 + 1, dtype=complex)
    first_bin = max(0, int(round(min(freqs_ghz) / df_ghz)))
    if low_frequency_fill == "hold":
        spectrum[:first_bin] = gamma[0]
    elif low_frequency_fill == "zero":
        pass
    else:
        raise ValueError(f"unsupported low_frequency_fill: {low_frequency_fill}")

    for freq, value in zip(freqs_ghz, gamma):
        index = int(round(freq / df_ghz))
        if 0 <= index < len(spectrum):
            spectrum[index] = value

    impulse = np.fft.irfft(spectrum, n=size)
    step = np.cumsum(impulse).real
    time_ns = np.arange(size, dtype=float) / (size * df_ghz)
    return time_ns, step


def _rho_to_impedance(rho: np.ndarray, z0_ohm: float) -> np.ndarray:
    clipped = np.clip(rho, -0.995, 0.995)
    return z0_ohm * (1.0 + clipped) / (1.0 - clipped)


def compute_tdr_points(
    s2p: Path,
    *,
    z0_ohm: float = 50.0,
    time_max_ns: float = 5.0,
    n_fft: int | None = None,
    low_frequency_fill: str = "hold",
) -> list[TdrPoint]:
    samples = sorted(read_s2p(s2p), key=lambda row: float(row["freq_ghz"]))
    if not samples:
        raise ValueError(f"no Touchstone samples in {s2p}")

    freqs = [float(row["freq_ghz"]) for row in samples]
    s11 = [complex(row["s11"]) for row in samples]
    s22 = [complex(row["s22"]) for row in samples]
    time_ns, s11_rho = _reflection_step_response(
        freqs,
        s11,
        n_fft=n_fft,
        low_frequency_fill=low_frequency_fill,
    )
    other_time_ns, s22_rho = _reflection_step_response(
        freqs,
        s22,
        n_fft=n_fft,
        low_frequency_fill=low_frequency_fill,
    )
    if len(time_ns) != len(other_time_ns) or np.max(np.abs(time_ns - other_time_ns)) > 1e-12:
        raise ValueError("S11 and S22 TDR time axes differ")

    s11_z = _rho_to_impedance(s11_rho, z0_ohm)
    s22_z = _rho_to_impedance(s22_rho, z0_ohm)
    mask = time_ns <= time_max_ns
    return [
        TdrPoint(
            time_ns=float(t),
            s11_rho=float(r11),
            s11_z_ohm=float(z11),
            s22_rho=float(r22),
            s22_z_ohm=float(z22),
        )
        for t, r11, z11, r22, z22 in zip(time_ns[mask], s11_rho[mask], s11_z[mask], s22_rho[mask], s22_z[mask])
    ]


def write_tdr_csv(points: list[TdrPoint], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["time_ns", "s11_rho", "s11_z_ohm", "s22_rho", "s22_z_ohm"],
        )
        writer.writeheader()
        for point in points:
            writer.writerow(
                {
                    "time_ns": f"{point.time_ns:.9g}",
                    "s11_rho": f"{point.s11_rho:.9g}",
                    "s11_z_ohm": f"{point.s11_z_ohm:.9g}",
                    "s22_rho": f"{point.s22_rho:.9g}",
                    "s22_z_ohm": f"{point.s22_z_ohm:.9g}",
                }
            )
    return out


def summarize_tdr(points: list[TdrPoint]) -> dict[str, float]:
    if not points:
        return {
            "s11_z_min_ohm": math.nan,
            "s11_z_max_ohm": math.nan,
            "s22_z_min_ohm": math.nan,
            "s22_z_max_ohm": math.nan,
        }
    return {
        "s11_z_min_ohm": min(point.s11_z_ohm for point in points),
        "s11_z_max_ohm": max(point.s11_z_ohm for point in points),
        "s22_z_min_ohm": min(point.s22_z_ohm for point in points),
        "s22_z_max_ohm": max(point.s22_z_ohm for point in points),
    }


__all__ = ["TdrPoint", "compute_tdr_points", "summarize_tdr", "write_tdr_csv"]
