"""S-parameter scoring helpers for filter optimization."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Iterable


TARGET_PROFILES = {
    "ro4350_strict": {
        "s21_5g_max_db": -45.0,
        "s21_6g_min_db": -3.0,
        "s21_8g_min_db": -3.0,
        "passband_min_s21_db": -3.5,
        "passband_max_ripple_db": 3.0,
        "passband_worst_return_loss_db": -10.0,
    },
    "fr4_25db": {
        "s21_5g_max_db": -25.0,
        "s21_6g_min_db": -5.0,
        "s21_8g_min_db": -5.0,
        "passband_min_s21_db": -5.0,
        "passband_max_ripple_db": 4.0,
        "passband_worst_return_loss_db": -5.0,
    },
    "fr4_25db_rl6": {
        "s21_5g_max_db": -25.0,
        "s21_6g_min_db": -5.0,
        "s21_8g_min_db": -5.0,
        "passband_min_s21_db": -5.0,
        "passband_max_ripple_db": 4.0,
        "passband_worst_return_loss_db": -6.0,
    },
    "fr4_25db_rl10": {
        "s21_5g_max_db": -25.0,
        "s21_6g_min_db": -5.0,
        "s21_8g_min_db": -5.0,
        "passband_min_s21_db": -5.0,
        "passband_max_ripple_db": 4.0,
        "passband_worst_return_loss_db": -10.0,
    },
}
DEFAULT_TARGET_PROFILE = "ro4350_strict"
TARGET_SCORE_VERSIONS = {
    "ro4350_strict": "ro4350_strict_v1",
    "fr4_25db": "fr4_i7_score_v1",
    "fr4_25db_rl6": "fr4_i7_score_v1",
    "fr4_25db_rl10": "fr4_i7_score_v1",
}


def db_from_mag(value: float) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-30))


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def is_complex_value(value: object) -> bool:
    return isinstance(value, complex) or hasattr(value, "real") and hasattr(value, "imag")


def choose_frequency_column(columns: Iterable[str]) -> str | None:
    candidates = list(columns)
    for name in candidates:
        norm = normalize_name(name)
        if norm in {"freq", "frequency", "frequencyhz"} or "freq" in norm:
            return name
    return candidates[0] if candidates else None


def choose_sparam_column(columns: Iterable[str], param: str) -> str | None:
    wanted = {
        "s11": ["s11", "s1p1", "s0101", "src00", "src0000"],
        "s21": ["s21", "s2p1", "s0201", "src10", "src1000"],
        "s12": ["s12", "s1p2", "s0102", "src01", "src0001"],
        "s22": ["s22", "s2p2", "s0202", "src11", "src1001"],
    }[param]
    for name in columns:
        norm = normalize_name(name)
        if norm in wanted:
            return name
    for name in columns:
        norm = normalize_name(name)
        if any(token in norm for token in wanted):
            return name
    return None


def series_to_db(values: list[object]) -> list[float]:
    if not values:
        return []
    first = next((value for value in values if value is not None), None)
    if first is None:
        return [float("nan") for _ in values]
    if is_complex_value(first):
        return [db_from_mag(abs(complex(value))) for value in values]
    numeric = [float(value) for value in values]
    if max(numeric) <= 2.0 and min(numeric) >= 0.0:
        return [db_from_mag(value) for value in numeric]
    return numeric


def frequency_to_ghz(values: list[object]) -> list[float]:
    numeric = [float(value) for value in values]
    max_freq = max(abs(value) for value in numeric)
    if max_freq > 1e6:
        return [value / 1e9 for value in numeric]
    if max_freq > 1000.0:
        return [value / 1000.0 for value in numeric]
    return numeric


def interp(xs: list[float], ys: list[float], x: float) -> float:
    pairs = sorted(zip(xs, ys, strict=False))
    if x <= pairs[0][0]:
        return pairs[0][1]
    if x >= pairs[-1][0]:
        return pairs[-1][1]
    for left, right in zip(pairs, pairs[1:], strict=False):
        x0, y0 = left
        x1, y1 = right
        if x0 <= x <= x1:
            ratio = (x - x0) / (x1 - x0)
            return y0 + ratio * (y1 - y0)
    return pairs[-1][1]


def fmt_db(value: float) -> str:
    return "nan" if math.isnan(value) else f"{value:.2f}"


def score_vectors(
    freq_ghz: list[float],
    traces: dict[str, list[float]],
    source: str,
    targets: dict[str, float],
    target_profile: str,
) -> dict[str, str]:
    s21 = traces["s21"]
    pass_indices = [idx for idx, freq in enumerate(freq_ghz) if 6.0 <= freq <= 8.0]
    pass_s21 = [s21[idx] for idx in pass_indices]
    pass_s11 = [traces["s11"][idx] for idx in pass_indices] if "s11" in traces else []
    pass_s22 = [traces["s22"][idx] for idx in pass_indices] if "s22" in traces else []

    s21_5 = interp(freq_ghz, s21, 5.0)
    s21_6 = interp(freq_ghz, s21, 6.0)
    s21_7 = interp(freq_ghz, s21, 7.0)
    s21_8 = interp(freq_ghz, s21, 8.0)
    s21_9 = interp(freq_ghz, s21, 9.0)
    pass_min = min(pass_s21) if pass_s21 else float("nan")
    pass_max = max(pass_s21) if pass_s21 else float("nan")
    ripple = pass_max - pass_min if pass_s21 else float("nan")
    worst_s11 = max(pass_s11) if pass_s11 else float("nan")
    worst_s22 = max(pass_s22) if pass_s22 else float("nan")

    ok = (
        s21_5 <= targets["s21_5g_max_db"]
        and s21_6 >= targets["s21_6g_min_db"]
        and s21_8 >= targets["s21_8g_min_db"]
        and pass_min >= targets["passband_min_s21_db"]
        and ripple <= targets["passband_max_ripple_db"]
    )
    if not math.isnan(worst_s11):
        ok = ok and worst_s11 <= targets["passband_worst_return_loss_db"]
    if not math.isnan(worst_s22):
        ok = ok and worst_s22 <= targets["passband_worst_return_loss_db"]

    return {
        "source": source,
        "target_profile": target_profile,
        "target_profile_id": target_profile,
        "status": "PASS_CANDIDATE" if ok else "TUNE",
        "s21_5g_db": fmt_db(s21_5),
        "s21_6g_db": fmt_db(s21_6),
        "s21_7g_db": fmt_db(s21_7),
        "s21_8g_db": fmt_db(s21_8),
        "s21_9g_db": fmt_db(s21_9),
        "passband_min_s21_db": fmt_db(pass_min),
        "passband_ripple_db": fmt_db(ripple),
        "worst_s11_6_8_db": fmt_db(worst_s11),
        "worst_s22_6_8_db": fmt_db(worst_s22),
        "margin_s21_5g_db": fmt_db(targets["s21_5g_max_db"] - s21_5),
        "margin_s21_6g_db": fmt_db(s21_6 - targets["s21_6g_min_db"]),
        "margin_s21_8g_db": fmt_db(s21_8 - targets["s21_8g_min_db"]),
        "margin_passband_min_s21_db": fmt_db(pass_min - targets["passband_min_s21_db"]),
        "margin_passband_ripple_db": fmt_db(targets["passband_max_ripple_db"] - ripple),
        "margin_worst_s11_6_8_db": fmt_db(targets["passband_worst_return_loss_db"] - worst_s11),
        "margin_worst_s22_6_8_db": fmt_db(targets["passband_worst_return_loss_db"] - worst_s22),
    }


def score_rfpro_rows(rows: list[dict[str, str]], targets: dict[str, float], target_profile: str, source: str) -> dict[str, str]:
    if not rows:
        raise ValueError(f"empty CSV: {source}")
    columns = list(rows[0].keys())
    freq_col = choose_frequency_column(columns)
    s_cols = {name: choose_sparam_column(columns, name) for name in ("s11", "s21", "s12", "s22")}
    if freq_col is None:
        raise ValueError(f"CSV has no frequency column: {source}")
    if s_cols["s21"] is None:
        raise ValueError(f"CSV has no s21 column: {source}")

    freq_ghz = frequency_to_ghz([row[freq_col] for row in rows])
    traces = {
        name: series_to_db([row[col] for row in rows])
        for name in ("s11", "s21", "s12", "s22")
        if (col := s_cols[name]) is not None
    }
    return score_vectors(freq_ghz, traces, source, targets, target_profile)


def score_rfpro_csv(path: Path, targets: dict[str, float], target_profile: str) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    return score_rfpro_rows(rows, targets, target_profile, str(path))
