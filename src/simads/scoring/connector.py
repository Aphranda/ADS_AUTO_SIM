"""Full-band scoring for SMA connector launch simulations."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any


CONNECTOR_SCORE_VERSION = "connector_fullband_v1"
CONNECTOR_BASELINE_SCORE_VERSION = "connector_fullband_v2_baseline_relative"
S2P_ORDER = ("s11", "s21", "s12", "s22")
UNIT_SCALE = {"HZ": 1e-9, "KHZ": 1e-6, "MHZ": 1e-3, "GHZ": 1.0}


@dataclass(frozen=True)
class ConnectorScoreProfile:
    profile_id: str = "sma_launch_fullband_0p5_10g_v1"
    score_version: str = CONNECTOR_SCORE_VERSION
    baseline_relative: bool = False
    baseline_required: bool = False
    band_min_ghz: float = 0.5
    band_max_ghz: float = 10.0
    target_worst_return_db: float = -10.0
    target_s21_min_db: float = -1.5
    target_s21_avg_db: float = -0.75
    target_s21_ripple_db: float = 1.0
    target_balance_db: float = 1.5
    good_return_db: float = -20.0
    return_weight_target_return_db: float = -10.0
    score_return_db: float = -15.0
    target_max_extra_il_db: float = 0.5
    target_avg_extra_il_db: float = 0.25
    target_extra_il_ripple_db: float = 0.5
    target_weighted_balance_db: float = 1.0
    pass_worst_return_db: float = -15.0
    pass_s21_min_db: float = -1.0
    pass_s21_avg_db: float = -0.5
    pass_s21_ripple_db: float = 0.75
    pass_balance_db: float = 1.0
    pass_max_extra_il_db: float = 0.35
    pass_avg_extra_il_db: float = 0.15
    pass_extra_il_ripple_db: float = 0.35
    pass_weighted_balance_db: float = 1.0
    weight_return_excess: float = 12.0
    weight_s21_min_shortfall: float = 10.0
    weight_s21_avg_shortfall: float = 8.0
    weight_s21_ripple_excess: float = 7.0
    weight_balance_excess: float = 4.0
    weight_max_extra_il: float = 8.0
    weight_avg_extra_il: float = 12.0
    weight_extra_il_ripple: float = 4.0
    weight_weighted_balance_excess: float = 4.0

    @classmethod
    def from_config(cls, data: dict[str, Any]) -> "ConnectorScoreProfile":
        frequency = _section(data, "frequency_ghz")
        mode = _section(data, "mode")
        targets = _section(data, "targets")
        pass_targets = _section(data, "pass_targets")
        return_weight = _section(data, "return_weight")
        weights = _section(data, "weights")

        profile = cls()
        return cls(
            profile_id=str(data.get("profile_id", profile.profile_id)),
            score_version=str(data.get("score_version", profile.score_version)),
            baseline_relative=bool(mode.get("baseline_relative", profile.baseline_relative)),
            baseline_required=bool(mode.get("baseline_required", profile.baseline_required)),
            band_min_ghz=_float(frequency, "band_min", profile.band_min_ghz),
            band_max_ghz=_float(frequency, "band_max", profile.band_max_ghz),
            target_worst_return_db=_float(targets, "worst_return_db", profile.target_worst_return_db),
            target_s21_min_db=_float(targets, "s21_min_db", profile.target_s21_min_db),
            target_s21_avg_db=_float(targets, "s21_avg_db", profile.target_s21_avg_db),
            target_s21_ripple_db=_float(targets, "s21_ripple_db", profile.target_s21_ripple_db),
            target_balance_db=_float(targets, "balance_db", profile.target_balance_db),
            good_return_db=_float(return_weight, "good_return_db", profile.good_return_db),
            return_weight_target_return_db=_float(
                return_weight,
                "target_return_db",
                profile.return_weight_target_return_db,
            ),
            score_return_db=_float(targets, "score_return_db", profile.score_return_db),
            target_max_extra_il_db=_float(targets, "max_extra_il_db", profile.target_max_extra_il_db),
            target_avg_extra_il_db=_float(targets, "avg_extra_il_db", profile.target_avg_extra_il_db),
            target_extra_il_ripple_db=_float(targets, "extra_il_ripple_db", profile.target_extra_il_ripple_db),
            target_weighted_balance_db=_float(targets, "weighted_balance_db", profile.target_weighted_balance_db),
            pass_worst_return_db=_float(pass_targets, "worst_return_db", profile.pass_worst_return_db),
            pass_s21_min_db=_float(pass_targets, "s21_min_db", profile.pass_s21_min_db),
            pass_s21_avg_db=_float(pass_targets, "s21_avg_db", profile.pass_s21_avg_db),
            pass_s21_ripple_db=_float(pass_targets, "s21_ripple_db", profile.pass_s21_ripple_db),
            pass_balance_db=_float(pass_targets, "balance_db", profile.pass_balance_db),
            pass_max_extra_il_db=_float(pass_targets, "max_extra_il_db", profile.pass_max_extra_il_db),
            pass_avg_extra_il_db=_float(pass_targets, "avg_extra_il_db", profile.pass_avg_extra_il_db),
            pass_extra_il_ripple_db=_float(pass_targets, "extra_il_ripple_db", profile.pass_extra_il_ripple_db),
            pass_weighted_balance_db=_float(
                pass_targets,
                "weighted_balance_db",
                _float(pass_targets, "balance_db", profile.pass_weighted_balance_db),
            ),
            weight_return_excess=_float(weights, "return_excess", profile.weight_return_excess),
            weight_s21_min_shortfall=_float(
                weights,
                "s21_min_shortfall",
                profile.weight_s21_min_shortfall,
            ),
            weight_s21_avg_shortfall=_float(
                weights,
                "s21_avg_shortfall",
                profile.weight_s21_avg_shortfall,
            ),
            weight_s21_ripple_excess=_float(
                weights,
                "s21_ripple_excess",
                profile.weight_s21_ripple_excess,
            ),
            weight_balance_excess=_float(weights, "balance_excess", profile.weight_balance_excess),
            weight_max_extra_il=_float(weights, "max_extra_il", profile.weight_max_extra_il),
            weight_avg_extra_il=_float(weights, "avg_extra_il", profile.weight_avg_extra_il),
            weight_extra_il_ripple=_float(
                weights,
                "extra_il_ripple",
                profile.weight_extra_il_ripple,
            ),
            weight_weighted_balance_excess=_float(
                weights,
                "weighted_balance_excess",
                profile.weight_weighted_balance_excess,
            ),
        )


DEFAULT_CONNECTOR_SCORE_PROFILE = ConnectorScoreProfile()


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def _float(data: dict[str, Any], name: str, default: float) -> float:
    value = data.get(name, default)
    return default if value is None else float(value)


def complex_from_pair(a: float, b: float, fmt: str) -> complex:
    if fmt == "DB":
        mag = 10.0 ** (a / 20.0)
        angle = math.radians(b)
        return complex(mag * math.cos(angle), mag * math.sin(angle))
    if fmt == "MA":
        angle = math.radians(b)
        return complex(a * math.cos(angle), a * math.sin(angle))
    if fmt == "RI":
        return complex(a, b)
    raise ValueError(f"unsupported Touchstone data format: {fmt}")


def db(value: complex) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-30))


def fmt(value: float) -> str:
    return "nan" if math.isnan(value) else f"{value:.2f}"


def normalized_z(gamma: complex) -> complex | None:
    denominator = 1.0 - gamma
    if abs(denominator) < 1e-12:
        return None
    return (1.0 + gamma) / denominator


def read_s2p(path: Path) -> list[dict[str, complex | float]]:
    unit_scale = 1e-9
    data_fmt = "MA"
    samples: list[dict[str, complex | float]] = []

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            parts = line[1:].upper().split()
            for part in parts:
                if part in UNIT_SCALE:
                    unit_scale = UNIT_SCALE[part]
                if part in {"DB", "MA", "RI"}:
                    data_fmt = part
            continue
        values = [float(item) for item in line.split()]
        if len(values) < 9:
            continue
        row: dict[str, complex | float] = {"freq_ghz": values[0] * unit_scale}
        for index, name in enumerate(S2P_ORDER):
            row[name] = complex_from_pair(values[1 + index * 2], values[2 + index * 2], data_fmt)
        samples.append(row)
    return samples


def read_s2p_db(path: Path) -> list[tuple[float, float, float, float, float]]:
    return [
        (
            float(sample["freq_ghz"]),
            db(complex(sample["s11"])),
            db(complex(sample["s21"])),
            db(complex(sample["s12"])),
            db(complex(sample["s22"])),
        )
        for sample in read_s2p(path)
    ]


def interp_db(samples: list[dict[str, complex | float]], freq_ghz: float, name: str) -> float:
    ordered = sorted(samples, key=lambda row: float(row["freq_ghz"]))
    if freq_ghz <= float(ordered[0]["freq_ghz"]):
        return db(complex(ordered[0][name]))
    if freq_ghz >= float(ordered[-1]["freq_ghz"]):
        return db(complex(ordered[-1][name]))
    for left, right in zip(ordered, ordered[1:]):
        left_f = float(left["freq_ghz"])
        right_f = float(right["freq_ghz"])
        if left_f <= freq_ghz <= right_f:
            ratio = (freq_ghz - left_f) / (right_f - left_f)
            left_db = db(complex(left[name]))
            right_db = db(complex(right[name]))
            return left_db + ratio * (right_db - left_db)
    return db(complex(ordered[-1][name]))


def _penalty_shortfall(target: float, value: float, weight: float) -> float:
    return max(0.0, target - value) * weight


def _penalty_excess(value: float, target: float, weight: float) -> float:
    return max(0.0, value - target) * weight


def _return_weight(worst_return: float, profile: ConnectorScoreProfile) -> float:
    span = profile.return_weight_target_return_db - profile.good_return_db
    if span <= 0.0:
        return 1.0
    return min(1.0, max(0.0, (worst_return - profile.good_return_db) / span))


def _weighted_return_balance(s11: list[float], s22: list[float], profile: ConnectorScoreProfile) -> float:
    values = []
    for left, right in zip(s11, s22):
        worst_return = max(left, right)
        values.append(abs(left - right) * _return_weight(worst_return, profile))
    return max(values) if values else float("nan")


def _baseline_s21_at_freqs(
    baseline_samples: list[dict[str, complex | float]],
    freqs_ghz: list[float],
) -> list[float]:
    return [interp_db(baseline_samples, freq, "s21") for freq in freqs_ghz]


def _same_file(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    try:
        return Path(left).resolve() == Path(right).resolve()
    except OSError:
        return left == right


def _smith_hint(z_values: list[complex]) -> str:
    if not z_values:
        return "smith_data_missing"
    quadrants = {
        "low_cap": sum(1 for z in z_values if z.real < 1.0 and z.imag < 0.0),
        "low_ind": sum(1 for z in z_values if z.real < 1.0 and z.imag >= 0.0),
        "high_ind": sum(1 for z in z_values if z.real >= 1.0 and z.imag >= 0.0),
        "high_cap": sum(1 for z in z_values if z.real >= 1.0 and z.imag < 0.0),
    }
    dominant = max(quadrants, key=quadrants.get)
    if quadrants[dominant] / len(z_values) < 0.35:
        return "mixed_impedance_track_check_local_resonance"
    return {
        "low_cap": "reduce_pad_capacitance_or_add_short_series_inductance",
        "low_ind": "reduce_series_inductance_or_recover_local_capacitance",
        "high_ind": "reduce_cutout_or_shorten_high_z_section",
        "high_cap": "adjust_taper_width_or_check_return_path",
    }[dominant]


def score_samples(
    samples: list[dict[str, complex | float]],
    source: str,
    profile: ConnectorScoreProfile = DEFAULT_CONNECTOR_SCORE_PROFILE,
    baseline_samples: list[dict[str, complex | float]] | None = None,
    baseline_source: str | None = None,
) -> dict[str, str]:
    if not samples:
        raise ValueError(f"no S-parameter samples found in {source}")
    band = [row for row in samples if profile.band_min_ghz <= float(row["freq_ghz"]) <= profile.band_max_ghz]
    if not band:
        raise ValueError(f"no samples in {profile.band_min_ghz:g}-{profile.band_max_ghz:g} GHz for {source}")

    s21 = [db(complex(row["s21"])) for row in band]
    s11 = [db(complex(row["s11"])) for row in band]
    s22 = [db(complex(row["s22"])) for row in band]
    freqs = [float(row["freq_ghz"]) for row in band]
    s21_min = min(s21)
    s21_avg = sum(s21) / len(s21)
    s21_ripple = max(s21) - s21_min
    worst_s11 = max(s11)
    worst_s22 = max(s22)
    worst_return_param = "s11" if worst_s11 >= worst_s22 else "s22"
    worst_return = max(worst_s11, worst_s22)
    worst_return_freq = float(max(band, key=lambda row: db(complex(row[worst_return_param])))["freq_ghz"])
    balance = max(abs(left - right) for left, right in zip(s11, s22))
    weighted_balance = _weighted_return_balance(s11, s22, profile)

    zin_values = [normalized_z(complex(row["s11"])) for row in band]
    zout_values = [normalized_z(complex(row["s22"])) for row in band]
    z_values = [value for value in [*zin_values, *zout_values] if value is not None]
    r_values = [value.real for value in z_values]
    x_values = [value.imag for value in z_values]

    baseline_s21: list[float] | None = None
    extra_il: list[float] = []
    max_extra_il = float("nan")
    avg_extra_il = float("nan")
    extra_il_ripple = float("nan")
    if baseline_samples is not None:
        baseline_s21 = _baseline_s21_at_freqs(baseline_samples, freqs)
        extra_il = [base - candidate for base, candidate in zip(baseline_s21, s21)]
        max_extra_il = max(extra_il)
        avg_extra_il = sum(extra_il) / len(extra_il)
        extra_il_ripple = max(extra_il) - min(extra_il)

    baseline_reference = _same_file(source, baseline_source)
    if baseline_samples is None:
        score_version = profile.score_version
        optimization_cost = (
            _penalty_excess(worst_return, profile.target_worst_return_db, profile.weight_return_excess)
            + _penalty_shortfall(profile.target_s21_min_db, s21_min, profile.weight_s21_min_shortfall)
            + _penalty_shortfall(profile.target_s21_avg_db, s21_avg, profile.weight_s21_avg_shortfall)
            + _penalty_excess(s21_ripple, profile.target_s21_ripple_db, profile.weight_s21_ripple_excess)
            + _penalty_excess(balance, profile.target_balance_db, profile.weight_balance_excess)
        )
    elif baseline_reference:
        score_version = profile.score_version
        optimization_cost = 0.0
    else:
        score_version = profile.score_version
        optimization_cost = (
            _penalty_excess(worst_return, profile.score_return_db, profile.weight_return_excess)
            + max(0.0, max_extra_il) * profile.weight_max_extra_il
            + max(0.0, avg_extra_il) * profile.weight_avg_extra_il
            + max(0.0, extra_il_ripple) * profile.weight_extra_il_ripple
            + _penalty_excess(
                weighted_balance,
                profile.target_weighted_balance_db,
                profile.weight_weighted_balance_excess,
            )
        )
    connector_score = max(0.0, 100.0 - optimization_cost)

    if baseline_reference:
        passed = True
        tune_ready = True
    elif baseline_samples is None:
        passed = (
            worst_return <= profile.pass_worst_return_db
            and s21_min >= profile.pass_s21_min_db
            and s21_avg >= profile.pass_s21_avg_db
            and s21_ripple <= profile.pass_s21_ripple_db
            and balance <= profile.pass_balance_db
        )
        tune_ready = (
            worst_return <= profile.target_worst_return_db
            and s21_min >= profile.target_s21_min_db
            and s21_ripple <= profile.target_s21_ripple_db
        )
    else:
        passed = (
            worst_return <= profile.pass_worst_return_db
            and max_extra_il <= profile.pass_max_extra_il_db
            and avg_extra_il <= profile.pass_avg_extra_il_db
            and extra_il_ripple <= profile.pass_extra_il_ripple_db
            and weighted_balance <= profile.pass_weighted_balance_db
        )
        tune_ready = (
            worst_return <= profile.target_worst_return_db
            and max_extra_il <= profile.target_max_extra_il_db
            and avg_extra_il <= profile.target_avg_extra_il_db
            and extra_il_ripple <= profile.target_extra_il_ripple_db
            and weighted_balance <= profile.target_weighted_balance_db
        )
    status = "PASS_CANDIDATE" if passed else ("CANDIDATE" if tune_ready else "TUNE")

    return {
        "file": source,
        "baseline_file": baseline_source or "",
        "score_version": score_version,
        "score_profile_id": profile.profile_id,
        "status": status,
        "connector_score": f"{connector_score:.3f}",
        "optimization_cost": f"{optimization_cost:.3f}",
        "band_min_ghz": f"{profile.band_min_ghz:g}",
        "band_max_ghz": f"{profile.band_max_ghz:g}",
        "s21_0p5g_db": fmt(interp_db(samples, 0.5, "s21")),
        "s21_1g_db": fmt(interp_db(samples, 1.0, "s21")),
        "s21_2g_db": fmt(interp_db(samples, 2.0, "s21")),
        "s21_3g_db": fmt(interp_db(samples, 3.0, "s21")),
        "s21_4g_db": fmt(interp_db(samples, 4.0, "s21")),
        "s21_5g_db": fmt(interp_db(samples, 5.0, "s21")),
        "s21_6g_db": fmt(interp_db(samples, 6.0, "s21")),
        "s21_7g_db": fmt(interp_db(samples, 7.0, "s21")),
        "s21_8g_db": fmt(interp_db(samples, 8.0, "s21")),
        "s21_9g_db": fmt(interp_db(samples, 9.0, "s21")),
        "s21_10g_db": fmt(interp_db(samples, 10.0, "s21")),
        "s21_min_0p5_10g_db": fmt(s21_min),
        "s21_avg_0p5_10g_db": fmt(s21_avg),
        "s21_ripple_0p5_10g_db": fmt(s21_ripple),
        "max_extra_il_0p5_10g_db": fmt(max_extra_il),
        "avg_extra_il_0p5_10g_db": fmt(avg_extra_il),
        "extra_il_ripple_0p5_10g_db": fmt(extra_il_ripple),
        "worst_s11_0p5_10g_db": fmt(worst_s11),
        "worst_s22_0p5_10g_db": fmt(worst_s22),
        "worst_return_0p5_10g_db": fmt(worst_return),
        "worst_return_param": worst_return_param,
        "worst_return_freq_ghz": f"{worst_return_freq:.3g}",
        "s11_s22_balance_max_0p5_10g_db": fmt(balance),
        "s11_s22_weighted_balance_max_0p5_10g_db": fmt(weighted_balance),
        "margin_worst_return_db": fmt(profile.target_worst_return_db - worst_return),
        "margin_s21_min_db": fmt(s21_min - profile.target_s21_min_db),
        "margin_s21_avg_db": fmt(s21_avg - profile.target_s21_avg_db),
        "margin_s21_ripple_db": fmt(profile.target_s21_ripple_db - s21_ripple),
        "margin_balance_db": fmt(profile.target_balance_db - balance),
        "margin_max_extra_il_db": fmt(profile.target_max_extra_il_db - max_extra_il),
        "margin_avg_extra_il_db": fmt(profile.target_avg_extra_il_db - avg_extra_il),
        "margin_extra_il_ripple_db": fmt(profile.target_extra_il_ripple_db - extra_il_ripple),
        "margin_weighted_balance_db": fmt(profile.target_weighted_balance_db - weighted_balance),
        "smith_z_r_min_0p5_10g": fmt(min(r_values)) if r_values else "nan",
        "smith_z_r_max_0p5_10g": fmt(max(r_values)) if r_values else "nan",
        "smith_z_x_min_0p5_10g": fmt(min(x_values)) if x_values else "nan",
        "smith_z_x_max_0p5_10g": fmt(max(x_values)) if x_values else "nan",
        "smith_tuning_hint": _smith_hint(z_values),
        "note": make_note(
            worst_return,
            s21_min,
            s21_avg,
            s21_ripple,
            balance,
            profile,
            max_extra_il=max_extra_il,
            avg_extra_il=avg_extra_il,
            extra_il_ripple=extra_il_ripple,
            weighted_balance=weighted_balance,
            baseline_relative=baseline_samples is not None,
        ),
    }


def make_note(
    worst_return: float,
    s21_min: float,
    s21_avg: float,
    s21_ripple: float,
    balance: float,
    profile: ConnectorScoreProfile,
    *,
    max_extra_il: float = float("nan"),
    avg_extra_il: float = float("nan"),
    extra_il_ripple: float = float("nan"),
    weighted_balance: float = float("nan"),
    baseline_relative: bool = False,
) -> str:
    issues = []
    if worst_return > profile.target_worst_return_db:
        issues.append("full-band return loss is weak")
    if baseline_relative:
        if max_extra_il > profile.target_max_extra_il_db:
            issues.append("maximum extra insertion loss versus baseline is high")
        if avg_extra_il > profile.target_avg_extra_il_db:
            issues.append("average extra insertion loss versus baseline is high")
        if extra_il_ripple > profile.target_extra_il_ripple_db:
            issues.append("extra insertion-loss ripple versus baseline is high")
        if weighted_balance > profile.target_weighted_balance_db:
            issues.append("return-loss-weighted S11/S22 balance is weak")
    else:
        if s21_min < profile.target_s21_min_db:
            issues.append("full-band minimum insertion loss is high")
        if s21_avg < profile.target_s21_avg_db:
            issues.append("full-band average insertion loss is high")
        if s21_ripple > profile.target_s21_ripple_db:
            issues.append("full-band S21 ripple is high")
        if balance > profile.target_balance_db:
            issues.append("S11/S22 balance is weak")
    if issues:
        return "; ".join(issues) + "."
    return "Connector launch meets full-band tuning targets; verify ports, mesh, and manufacturing constraints."


def score_s2p(
    path: Path,
    profile: ConnectorScoreProfile = DEFAULT_CONNECTOR_SCORE_PROFILE,
    baseline_path: Path | None = None,
) -> dict[str, str]:
    if profile.baseline_required and baseline_path is None:
        raise ValueError(f"connector scoring profile requires a baseline S2P: {profile.profile_id}")
    baseline_samples = read_s2p(baseline_path) if baseline_path is not None else None
    return score_samples(
        read_s2p(path),
        str(path),
        profile,
        baseline_samples=baseline_samples,
        baseline_source=str(baseline_path) if baseline_path is not None else None,
    )


__all__ = [
    "CONNECTOR_SCORE_VERSION",
    "CONNECTOR_BASELINE_SCORE_VERSION",
    "ConnectorScoreProfile",
    "DEFAULT_CONNECTOR_SCORE_PROFILE",
    "complex_from_pair",
    "db",
    "read_s2p",
    "read_s2p_db",
    "score_s2p",
    "score_samples",
]
