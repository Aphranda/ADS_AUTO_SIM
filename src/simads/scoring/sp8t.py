"""Four-port SP8T board launch scoring with isolation metrics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from simads.scoring.touchstone import db, read_touchstone


SP8T_SCORE_VERSION = "sp8t_four_port_connector_isolation_v1"
THROUGH_PAIRS = ("s21", "s43")
RETURN_PARAMS = ("s11", "s22", "s33", "s44")
ISOLATION_PARAMS = ("s31", "s41", "s32", "s42", "s13", "s14", "s23", "s24")


@dataclass(frozen=True)
class Sp8tFourPortScoreProfile:
    profile_id: str = "sp8t_four_port_connector_isolation_0p5_10g_v1"
    score_version: str = SP8T_SCORE_VERSION
    band_min_ghz: float = 0.5
    band_max_ghz: float = 10.0
    target_worst_return_db: float = -10.0
    target_through_min_db: float = -1.5
    target_through_avg_db: float = -0.75
    target_through_ripple_db: float = 1.0
    target_through_balance_db: float = 1.0
    target_worst_isolation_db: float = -30.0
    pass_worst_return_db: float = -10.0
    pass_through_min_db: float = -1.5
    pass_through_avg_db: float = -0.75
    pass_through_ripple_db: float = 1.25
    pass_through_balance_db: float = 1.25
    pass_worst_isolation_db: float = -25.0
    weight_return_excess: float = 8.0
    weight_through_min_shortfall: float = 10.0
    weight_through_avg_shortfall: float = 8.0
    weight_through_ripple_excess: float = 5.0
    weight_through_balance_excess: float = 4.0
    weight_isolation_excess: float = 3.0

    @classmethod
    def from_config(cls, data: dict[str, Any]) -> "Sp8tFourPortScoreProfile":
        profile = cls()
        frequency = _section(data, "frequency_ghz")
        targets = _section(data, "targets")
        pass_targets = _section(data, "pass_targets")
        weights = _section(data, "weights")
        return cls(
            profile_id=str(data.get("profile_id", profile.profile_id)),
            score_version=str(data.get("score_version", profile.score_version)),
            band_min_ghz=_float(frequency, "band_min", profile.band_min_ghz),
            band_max_ghz=_float(frequency, "band_max", profile.band_max_ghz),
            target_worst_return_db=_float(targets, "worst_return_db", profile.target_worst_return_db),
            target_through_min_db=_float(targets, "through_min_db", profile.target_through_min_db),
            target_through_avg_db=_float(targets, "through_avg_db", profile.target_through_avg_db),
            target_through_ripple_db=_float(targets, "through_ripple_db", profile.target_through_ripple_db),
            target_through_balance_db=_float(targets, "through_balance_db", profile.target_through_balance_db),
            target_worst_isolation_db=_float(targets, "worst_isolation_db", profile.target_worst_isolation_db),
            pass_worst_return_db=_float(pass_targets, "worst_return_db", profile.pass_worst_return_db),
            pass_through_min_db=_float(pass_targets, "through_min_db", profile.pass_through_min_db),
            pass_through_avg_db=_float(pass_targets, "through_avg_db", profile.pass_through_avg_db),
            pass_through_ripple_db=_float(pass_targets, "through_ripple_db", profile.pass_through_ripple_db),
            pass_through_balance_db=_float(pass_targets, "through_balance_db", profile.pass_through_balance_db),
            pass_worst_isolation_db=_float(pass_targets, "worst_isolation_db", profile.pass_worst_isolation_db),
            weight_return_excess=_float(weights, "return_excess", profile.weight_return_excess),
            weight_through_min_shortfall=_float(
                weights,
                "through_min_shortfall",
                profile.weight_through_min_shortfall,
            ),
            weight_through_avg_shortfall=_float(
                weights,
                "through_avg_shortfall",
                profile.weight_through_avg_shortfall,
            ),
            weight_through_ripple_excess=_float(
                weights,
                "through_ripple_excess",
                profile.weight_through_ripple_excess,
            ),
            weight_through_balance_excess=_float(
                weights,
                "through_balance_excess",
                profile.weight_through_balance_excess,
            ),
            weight_isolation_excess=_float(weights, "isolation_excess", profile.weight_isolation_excess),
        )


DEFAULT_SP8T_FOUR_PORT_SCORE_PROFILE = Sp8tFourPortScoreProfile()


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def _float(data: dict[str, Any], name: str, default: float) -> float:
    value = data.get(name, default)
    return default if value is None else float(value)


def fmt(value: float) -> str:
    return "nan" if math.isnan(value) else f"{value:.2f}"


def interp_db(samples: list[dict[str, Any]], freq_ghz: float, name: str) -> float:
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


def _db_series(samples: list[dict[str, Any]], name: str) -> list[float]:
    return [db(complex(row[name])) for row in samples]


def _max_item(samples: list[dict[str, Any]], names: tuple[str, ...]) -> tuple[str, float, float]:
    best_name = names[0]
    best_freq = float(samples[0]["freq_ghz"])
    best_value = -math.inf
    for row in samples:
        freq = float(row["freq_ghz"])
        for name in names:
            value = db(complex(row[name]))
            if value > best_value:
                best_name = name
                best_freq = freq
                best_value = value
    return best_name, best_freq, best_value


def score_samples(
    samples: list[dict[str, Any]],
    source: str,
    profile: Sp8tFourPortScoreProfile = DEFAULT_SP8T_FOUR_PORT_SCORE_PROFILE,
) -> dict[str, str]:
    if not samples:
        raise ValueError(f"no Touchstone samples found in {source}")
    required = set(THROUGH_PAIRS) | set(RETURN_PARAMS) | set(ISOLATION_PARAMS)
    missing = sorted(name for name in required if name not in samples[0])
    if missing:
        raise ValueError(f"SP8T four-port scoring needs missing S-parameters in {source}: {', '.join(missing)}")
    band = [row for row in samples if profile.band_min_ghz <= float(row["freq_ghz"]) <= profile.band_max_ghz]
    if not band:
        raise ValueError(f"no samples in {profile.band_min_ghz:g}-{profile.band_max_ghz:g} GHz for {source}")

    s21 = _db_series(band, "s21")
    s43 = _db_series(band, "s43")
    through_values = [*s21, *s43]
    through_min = min(through_values)
    through_avg = sum(through_values) / len(through_values)
    through_ripple = max(through_values) - through_min
    through_balance = max(abs(left - right) for left, right in zip(s21, s43))
    worst_return_param, worst_return_freq, worst_return = _max_item(band, RETURN_PARAMS)
    worst_iso_param, worst_iso_freq, worst_isolation = _max_item(band, ISOLATION_PARAMS)

    optimization_cost = (
        _penalty_excess(worst_return, profile.target_worst_return_db, profile.weight_return_excess)
        + _penalty_shortfall(profile.target_through_min_db, through_min, profile.weight_through_min_shortfall)
        + _penalty_shortfall(profile.target_through_avg_db, through_avg, profile.weight_through_avg_shortfall)
        + _penalty_excess(through_ripple, profile.target_through_ripple_db, profile.weight_through_ripple_excess)
        + _penalty_excess(through_balance, profile.target_through_balance_db, profile.weight_through_balance_excess)
        + _penalty_excess(worst_isolation, profile.target_worst_isolation_db, profile.weight_isolation_excess)
    )
    sp8t_score = max(0.0, 100.0 - optimization_cost)
    passed = (
        worst_return <= profile.pass_worst_return_db
        and through_min >= profile.pass_through_min_db
        and through_avg >= profile.pass_through_avg_db
        and through_ripple <= profile.pass_through_ripple_db
        and through_balance <= profile.pass_through_balance_db
        and worst_isolation <= profile.pass_worst_isolation_db
    )
    tune_ready = (
        worst_return <= profile.target_worst_return_db
        and through_min >= profile.target_through_min_db
        and worst_isolation <= profile.target_worst_isolation_db
    )
    status = "PASS_CANDIDATE" if passed else ("CANDIDATE" if tune_ready else "TUNE")

    return {
        "file": source,
        "score_version": profile.score_version,
        "score_profile_id": profile.profile_id,
        "status": status,
        "sp8t_score": f"{sp8t_score:.3f}",
        "optimization_cost": f"{optimization_cost:.3f}",
        "band_min_ghz": f"{profile.band_min_ghz:g}",
        "band_max_ghz": f"{profile.band_max_ghz:g}",
        "s21_min_0p5_10g_db": fmt(min(s21)),
        "s43_min_0p5_10g_db": fmt(min(s43)),
        "through_min_0p5_10g_db": fmt(through_min),
        "through_avg_0p5_10g_db": fmt(through_avg),
        "through_ripple_0p5_10g_db": fmt(through_ripple),
        "s21_s43_balance_max_0p5_10g_db": fmt(through_balance),
        "s21_3p5g_db": fmt(interp_db(samples, 3.5, "s21")),
        "s43_3p5g_db": fmt(interp_db(samples, 3.5, "s43")),
        "s21_8g_db": fmt(interp_db(samples, 8.0, "s21")),
        "s43_8g_db": fmt(interp_db(samples, 8.0, "s43")),
        "worst_return_0p5_10g_db": fmt(worst_return),
        "worst_return_param": worst_return_param,
        "worst_return_freq_ghz": f"{worst_return_freq:.3g}",
        "worst_isolation_0p5_10g_db": fmt(worst_isolation),
        "worst_isolation_param": worst_iso_param,
        "worst_isolation_freq_ghz": f"{worst_iso_freq:.3g}",
        "margin_worst_return_db": fmt(profile.target_worst_return_db - worst_return),
        "margin_through_min_db": fmt(through_min - profile.target_through_min_db),
        "margin_through_avg_db": fmt(through_avg - profile.target_through_avg_db),
        "margin_through_ripple_db": fmt(profile.target_through_ripple_db - through_ripple),
        "margin_through_balance_db": fmt(profile.target_through_balance_db - through_balance),
        "margin_worst_isolation_db": fmt(profile.target_worst_isolation_db - worst_isolation),
        "note": make_note(worst_return, through_min, through_ripple, through_balance, worst_isolation, profile),
    }


def make_note(
    worst_return: float,
    through_min: float,
    through_ripple: float,
    through_balance: float,
    worst_isolation: float,
    profile: Sp8tFourPortScoreProfile,
) -> str:
    issues = []
    if worst_return > profile.target_worst_return_db:
        issues.append("return loss is weak")
    if through_min < profile.target_through_min_db:
        issues.append("minimum through insertion loss is high")
    if through_ripple > profile.target_through_ripple_db:
        issues.append("through ripple is high")
    if through_balance > profile.target_through_balance_db:
        issues.append("Port1-Port2 and Port3-Port4 through paths are imbalanced")
    if worst_isolation > profile.target_worst_isolation_db:
        issues.append("input/output isolation is weak")
    if issues:
        return "; ".join(issues) + "."
    return "Four-port SP8T connector paths meet current through, return, balance, and isolation targets."


def score_touchstone(
    path: Path,
    profile: Sp8tFourPortScoreProfile = DEFAULT_SP8T_FOUR_PORT_SCORE_PROFILE,
) -> dict[str, str]:
    return score_samples(read_touchstone(path, nports=4), str(path), profile)


def write_trace_csv(samples: list[dict[str, Any]], out_csv: Path) -> Path:
    fields = [
        "freq_ghz",
        "s11_db",
        "s21_db",
        "s22_db",
        "s33_db",
        "s43_db",
        "s44_db",
        "worst_return_db",
        "worst_isolation_db",
        *[f"{name}_db" for name in ISOLATION_PARAMS],
    ]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in samples:
            output: dict[str, str] = {"freq_ghz": f"{float(row['freq_ghz']):.9g}"}
            for name in ("s11", "s21", "s22", "s33", "s43", "s44"):
                output[f"{name}_db"] = f"{db(complex(row[name])):.6g}"
            output["worst_return_db"] = f"{max(db(complex(row[name])) for name in RETURN_PARAMS):.6g}"
            output["worst_isolation_db"] = f"{max(db(complex(row[name])) for name in ISOLATION_PARAMS):.6g}"
            for name in ISOLATION_PARAMS:
                output[f"{name}_db"] = f"{db(complex(row[name])):.6g}"
            writer.writerow(output)
    return out_csv


def read_touchstone4(path: Path) -> list[dict[str, Any]]:
    return read_touchstone(path, nports=4)


__all__ = [
    "DEFAULT_SP8T_FOUR_PORT_SCORE_PROFILE",
    "ISOLATION_PARAMS",
    "RETURN_PARAMS",
    "SP8T_SCORE_VERSION",
    "Sp8tFourPortScoreProfile",
    "THROUGH_PAIRS",
    "read_touchstone4",
    "score_samples",
    "score_touchstone",
    "write_trace_csv",
]
