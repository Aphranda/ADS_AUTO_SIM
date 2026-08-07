"""Touchstone parsing helpers shared by S-parameter scoring modules."""

from __future__ import annotations

import math
from pathlib import Path
import re
from typing import Any


UNIT_SCALE_TO_GHZ = {"HZ": 1e-9, "KHZ": 1e-6, "MHZ": 1e-3, "GHZ": 1.0}


def complex_from_pair(a: float, b: float, data_format: str) -> complex:
    fmt = data_format.upper()
    if fmt == "DB":
        mag = 10.0 ** (a / 20.0)
        angle = math.radians(b)
        return complex(mag * math.cos(angle), mag * math.sin(angle))
    if fmt == "MA":
        angle = math.radians(b)
        return complex(a * math.cos(angle), a * math.sin(angle))
    if fmt == "RI":
        return complex(a, b)
    raise ValueError(f"unsupported Touchstone data format: {data_format}")


def db(value: complex) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-30))


def infer_nports(path: Path) -> int:
    match = re.search(r"\.s(\d+)p$", path.name, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"cannot infer Touchstone port count from suffix: {path}")
    return int(match.group(1))


def read_touchstone(path: Path, *, nports: int | None = None) -> list[dict[str, Any]]:
    """Read a Touchstone v1/v2 full matrix file.

    Network parameters are returned as lower-case keys such as ``s21``. The
    matrix is interpreted in Touchstone column-major order, which preserves the
    standard S2P order ``S11, S21, S12, S22`` and generalizes to N-port files.
    """

    ports = nports or infer_nports(path)
    if ports < 1:
        raise ValueError(f"invalid Touchstone port count: {ports}")
    unit_scale = 1e-9
    data_format = "MA"
    samples: list[dict[str, Any]] = []
    data_tokens: list[str] = []
    values_per_record = 1 + 2 * ports * ports

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("["):
            lower = line.lower()
            if lower.startswith("[number of ports]"):
                parts = line.replace("]", "] ").split()
                for part in reversed(parts):
                    if part.isdigit():
                        ports = int(part)
                        values_per_record = 1 + 2 * ports * ports
                        break
            continue
        if line.startswith("#"):
            parts = line[1:].upper().split()
            for part in parts:
                if part in UNIT_SCALE_TO_GHZ:
                    unit_scale = UNIT_SCALE_TO_GHZ[part]
                elif part in {"DB", "MA", "RI"}:
                    data_format = part
            continue
        data_tokens.extend(line.split())
        while len(data_tokens) >= values_per_record:
            values = [float(item) for item in data_tokens[:values_per_record]]
            del data_tokens[:values_per_record]
            sample: dict[str, Any] = {"freq_ghz": values[0] * unit_scale}
            index = 1
            for source_port in range(1, ports + 1):
                for response_port in range(1, ports + 1):
                    sample[f"s{response_port}{source_port}"] = complex_from_pair(
                        values[index],
                        values[index + 1],
                        data_format,
                    )
                    index += 2
            samples.append(sample)
    if data_tokens:
        raise ValueError(f"incomplete Touchstone data record in {path}: {len(data_tokens)} trailing values")
    return samples


__all__ = ["UNIT_SCALE_TO_GHZ", "complex_from_pair", "db", "infer_nports", "read_touchstone"]
