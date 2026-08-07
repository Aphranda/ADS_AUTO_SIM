"""Touchstone parsing helpers shared by S-parameter scoring modules."""

from __future__ import annotations

from dataclasses import dataclass
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


def normalize_sparam_name(name: str) -> str:
    value = name.strip().lower()
    if value.startswith("s"):
        value = value[1:]
    if not value.isdigit() or len(value) != 2:
        raise ValueError(f"invalid S-parameter name: {name}")
    return f"s{value}"


@dataclass(frozen=True)
class SParameterNetwork:
    path: Path
    nports: int
    samples: list[dict[str, Any]]

    @property
    def frequency_ghz(self) -> list[float]:
        return [float(row["freq_ghz"]) for row in self.samples]

    def require_nports(self, expected: int, *, system: str | None = None) -> "SParameterNetwork":
        if self.nports != expected:
            label = f" for {system}" if system else ""
            raise ValueError(f"expected S{expected}P{label}, got S{self.nports}P: {self.path}")
        return self

    def band(self, band_min_ghz: float, band_max_ghz: float) -> "SParameterNetwork":
        selected = [row for row in self.samples if band_min_ghz <= float(row["freq_ghz"]) <= band_max_ghz]
        return SParameterNetwork(self.path, self.nports, selected)

    def s(self, name: str) -> list[complex]:
        key = normalize_sparam_name(name)
        self._require_param(key)
        return [complex(row[key]) for row in self.samples]

    def db(self, name: str) -> list[float]:
        return [db(value) for value in self.s(name)]

    def interp_db(self, freq_ghz: float, name: str) -> float:
        key = normalize_sparam_name(name)
        self._require_param(key)
        ordered = sorted(self.samples, key=lambda row: float(row["freq_ghz"]))
        if not ordered:
            raise ValueError(f"no samples in network: {self.path}")
        if freq_ghz <= float(ordered[0]["freq_ghz"]):
            return db(complex(ordered[0][key]))
        if freq_ghz >= float(ordered[-1]["freq_ghz"]):
            return db(complex(ordered[-1][key]))
        for left, right in zip(ordered, ordered[1:]):
            left_f = float(left["freq_ghz"])
            right_f = float(right["freq_ghz"])
            if left_f <= freq_ghz <= right_f:
                ratio = (freq_ghz - left_f) / (right_f - left_f)
                return db(complex(left[key])) + ratio * (db(complex(right[key])) - db(complex(left[key])))
        return db(complex(ordered[-1][key]))

    def _require_param(self, key: str) -> None:
        if not self.samples:
            raise ValueError(f"no samples in network: {self.path}")
        if key not in self.samples[0]:
            raise ValueError(f"network S{self.nports}P missing {key.upper()}: {self.path}")


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


def read_sparameter_network(path: Path, *, nports: int | None = None) -> SParameterNetwork:
    inferred_ports = infer_nports(path)
    ports = nports or inferred_ports
    if nports is not None and inferred_ports != nports:
        raise ValueError(f"Touchstone suffix/reader mismatch: expected S{nports}P, got S{inferred_ports}P: {path}")
    if ports < 2 or ports > 6:
        raise ValueError(f"only S2P-S6P networks are supported by the scoring abstraction, got S{ports}P: {path}")
    return SParameterNetwork(path=path, nports=ports, samples=read_touchstone(path, nports=ports))


def _read_fixed_network(path: Path, nports: int) -> SParameterNetwork:
    return read_sparameter_network(path, nports=nports).require_nports(nports)


def read_s2p_network(path: Path) -> SParameterNetwork:
    return _read_fixed_network(path, 2)


def read_s3p_network(path: Path) -> SParameterNetwork:
    return _read_fixed_network(path, 3)


def read_s4p_network(path: Path) -> SParameterNetwork:
    return _read_fixed_network(path, 4)


def read_s5p_network(path: Path) -> SParameterNetwork:
    return _read_fixed_network(path, 5)


def read_s6p_network(path: Path) -> SParameterNetwork:
    return _read_fixed_network(path, 6)


__all__ = [
    "SParameterNetwork",
    "UNIT_SCALE_TO_GHZ",
    "complex_from_pair",
    "db",
    "infer_nports",
    "normalize_sparam_name",
    "read_s2p_network",
    "read_s3p_network",
    "read_s4p_network",
    "read_s5p_network",
    "read_s6p_network",
    "read_sparameter_network",
    "read_touchstone",
]
