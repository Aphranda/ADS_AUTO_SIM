"""Feature helpers for FR4 7th-order interdigital BPF NN surrogates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import numpy as np


PARAM_COLUMNS = [
    "L_mm",
    "tap_mm",
    "Egap_mm",
    "S1_mm",
    "S2_mm",
    "S3_mm",
    "S4_mm",
    "S5_mm",
    "S6_mm",
    "W0_mm",
    "feed_len_mm",
    "feed_taper_len_mm",
    "feed_tip_w_mm",
    "feed_overlap_mm",
    "via_diameter_mm",
]

SYMMETRIC_FEATURES = ["S1S6_mean", "S2S5_mean", "S3S4_mean"]
DELTA_FEATURES = ["S1S6_delta", "S2S5_delta", "S3S4_delta"]
RESONATOR_FEATURES = ["L_mm", "W0_mm", "via_diameter_mm", "via_pad_mm", "Egap_mm"]
GAP_FEATURES = [
    "S1_mm",
    "S2_mm",
    "S3_mm",
    "S4_mm",
    "S5_mm",
    "S6_mm",
    *SYMMETRIC_FEATURES,
    *DELTA_FEATURES,
]
FEED_FEATURES = [
    "tap_mm",
    "tap_over_L",
    "feed_len_mm",
    "feed_taper_len_mm",
    "feed_tip_w_mm",
    "feed_overlap_mm",
    "feed_tip_over_W0",
    "feed_overlap_over_W0",
]
DERIVED_FEATURES = [
    "L_over_lambda_g_7g",
    "S1_over_W0",
    "S2_over_W0",
    "S3_over_W0",
    "S4_over_W0",
    "S5_over_W0",
    "S6_over_W0",
    "min_gap_over_W0",
    "max_gap_over_W0",
    "gap_gradient_12",
    "gap_gradient_23",
    "gap_gradient_34",
    "gap_gradient_45",
    "gap_gradient_56",
    "coupling_proxy_1",
    "coupling_proxy_2",
    "coupling_proxy_3",
    "coupling_proxy_4",
    "coupling_proxy_5",
    "coupling_proxy_6",
    "feed_external_Q_proxy",
]

S_PARAM_NAMES = ["s11", "s21", "s22"]
AUX_FEATURES = [
    "passband_min_s21_db",
    "passband_ripple_db",
    "s21_5g_db",
    "s21_6g_db",
    "s21_8g_db",
    "s21_9g_db",
    "high_stop_max_s21_db",
    "worst_s11_6_8_db",
    "worst_s22_6_8_db",
]

LEGACY_CENTER = {
    "L_mm": 5.55,
    "tap_mm": 1.95,
    "Egap_mm": 0.4823,
    "S1_mm": 0.1176,
    "S2_mm": 0.1750,
    "S3_mm": 0.1857,
    "S4_mm": 0.1857,
    "S5_mm": 0.1750,
    "S6_mm": 0.1176,
    "W0_mm": 0.3648,
    "feed_len_mm": 3.0,
    "feed_taper_len_mm": 0.60,
    "feed_tip_w_mm": 0.18,
    "feed_overlap_mm": 0.06,
    "via_diameter_mm": 0.254,
    "via_pad_mm": 0.3556,
    "er": 4.6,
    "dielectric_height_mm": 0.21,
}

TRUST_BOUNDS = {
    "L_mm": (5.535, 5.565),
    "tap_mm": (1.93, 1.97),
    "Egap_mm": (0.462, 0.502),
    "S1_mm": (0.112, 0.124),
    "S2_mm": (0.168, 0.182),
    "S3_mm": (0.180, 0.192),
    "S4_mm": (0.180, 0.192),
    "S5_mm": (0.168, 0.182),
    "S6_mm": (0.112, 0.124),
    "W0_mm": (0.350, 0.375),
    "feed_len_mm": (3.0, 3.0),
    "feed_taper_len_mm": (0.45, 0.75),
    "feed_tip_w_mm": (0.17, 0.22),
    "feed_overlap_mm": (0.052, 0.070),
    "via_diameter_mm": (0.254, 0.254),
}


@dataclass(frozen=True)
class InterdigitalFeatureBundle:
    x_raw: np.ndarray
    x_sym: np.ndarray
    x_delta: np.ndarray
    x_derived: np.ndarray
    x_resonator: np.ndarray
    x_gap: np.ndarray
    x_feed: np.ndarray


def parse_float(value: object, default: float = math.nan) -> float:
    if value is None:
        return default
    text = str(value).strip()
    return float(text) if text else default


def params_from_layout_json(data: Mapping[str, object]) -> dict[str, float]:
    parameters = data.get("parameters", {})
    if not isinstance(parameters, Mapping):
        raise ValueError("layout JSON has no parameters object")
    gaps = list(parameters.get("gaps_mm", []))
    if len(gaps) < 6:
        raise ValueError("interdigital parameters must contain six gaps for 7th-order design")
    values = dict(LEGACY_CENTER)
    values.update(
        {
            "L_mm": parse_float(parameters.get("resonator_l_mm"), LEGACY_CENTER["L_mm"]),
            "tap_mm": parse_float(parameters.get("tap_from_bottom_mm"), LEGACY_CENTER["tap_mm"]),
            "Egap_mm": parse_float(parameters.get("end_gap_mm"), LEGACY_CENTER["Egap_mm"]),
            "W0_mm": parse_float(parameters.get("w0_mm"), LEGACY_CENTER["W0_mm"]),
            "feed_len_mm": parse_float(parameters.get("feed_len_mm"), LEGACY_CENTER["feed_len_mm"]),
            "feed_taper_len_mm": parse_float(parameters.get("feed_taper_len_mm"), LEGACY_CENTER["feed_taper_len_mm"]),
            "feed_tip_w_mm": parse_float(parameters.get("feed_tip_w_mm"), LEGACY_CENTER["feed_tip_w_mm"]),
            "feed_overlap_mm": parse_float(parameters.get("feed_overlap_mm"), LEGACY_CENTER["feed_overlap_mm"]),
            "via_diameter_mm": parse_float(parameters.get("via_diameter_mm"), LEGACY_CENTER["via_diameter_mm"]),
            "via_pad_mm": parse_float(parameters.get("via_pad_mm"), LEGACY_CENTER["via_pad_mm"]),
            "er": parse_float(parameters.get("er"), LEGACY_CENTER["er"]),
            "dielectric_height_mm": parse_float(
                parameters.get("dielectric_height_mm"), LEGACY_CENTER["dielectric_height_mm"]
            ),
        }
    )
    for idx, value in enumerate(gaps[:6], start=1):
        values[f"S{idx}_mm"] = float(value)
    return values


def params_from_plan_row(row: Mapping[str, object]) -> dict[str, float]:
    values = dict(LEGACY_CENTER)
    for key in PARAM_COLUMNS:
        values[key] = parse_float(row.get(key), float(values[key]))
    values["via_pad_mm"] = parse_float(row.get("via_pad_mm"), LEGACY_CENTER["via_pad_mm"])
    values["er"] = parse_float(row.get("er"), LEGACY_CENTER["er"])
    values["dielectric_height_mm"] = parse_float(row.get("dielectric_height_mm"), LEGACY_CENTER["dielectric_height_mm"])
    return values


def effective_er(er: float, h_mm: float, w_mm: float) -> float:
    w = max(w_mm, 1e-6)
    h = max(h_mm, 1e-6)
    return (er + 1.0) / 2.0 + (er - 1.0) / 2.0 / math.sqrt(1.0 + 12.0 * h / w)


def lambda_g_mm(freq_ghz: float, er: float, h_mm: float, w_mm: float) -> float:
    return 299.792458 / max(freq_ghz, 1e-9) / math.sqrt(effective_er(er, h_mm, w_mm))


def feature_bundle(params: Mapping[str, float]) -> InterdigitalFeatureBundle:
    p = {key: float(params.get(key, LEGACY_CENTER.get(key, 0.0))) for key in set(PARAM_COLUMNS) | set(LEGACY_CENTER)}
    gaps = np.asarray([p[f"S{idx}_mm"] for idx in range(1, 7)], dtype=np.float32)
    w0 = max(p["W0_mm"], 1e-6)
    length = max(p["L_mm"], 1e-6)
    x_raw = np.asarray([p[key] for key in PARAM_COLUMNS], dtype=np.float32)
    x_sym = np.asarray(
        [
            (p["S1_mm"] + p["S6_mm"]) / 2.0,
            (p["S2_mm"] + p["S5_mm"]) / 2.0,
            (p["S3_mm"] + p["S4_mm"]) / 2.0,
        ],
        dtype=np.float32,
    )
    x_delta = np.asarray(
        [p["S1_mm"] - p["S6_mm"], p["S2_mm"] - p["S5_mm"], p["S3_mm"] - p["S4_mm"]],
        dtype=np.float32,
    )
    gap_over_w0 = gaps / w0
    gap_gradients = np.diff(gaps)
    coupling_proxy = w0 / np.maximum(gaps, 1e-6)
    feed_tip_over_w0 = p["feed_tip_w_mm"] / w0
    feed_overlap_over_w0 = p["feed_overlap_mm"] / w0
    tap_over_l = p["tap_mm"] / length
    feed_proxy = tap_over_l * (1.0 + feed_overlap_over_w0) * max(feed_tip_over_w0, 1e-6)
    x_derived = np.asarray(
        [
            p["L_mm"] / lambda_g_mm(7.0, p["er"], p["dielectric_height_mm"], w0),
            *gap_over_w0.tolist(),
            float(np.min(gap_over_w0)),
            float(np.max(gap_over_w0)),
            *gap_gradients.tolist(),
            *coupling_proxy.tolist(),
            feed_proxy,
        ],
        dtype=np.float32,
    )
    x_resonator = np.asarray([p["L_mm"], p["W0_mm"], p["via_diameter_mm"], p["via_pad_mm"], p["Egap_mm"]], dtype=np.float32)
    x_gap = np.concatenate([gaps, x_sym, x_delta]).astype(np.float32)
    x_feed = np.asarray(
        [
            p["tap_mm"],
            tap_over_l,
            p["feed_len_mm"],
            p["feed_taper_len_mm"],
            p["feed_tip_w_mm"],
            p["feed_overlap_mm"],
            feed_tip_over_w0,
            feed_overlap_over_w0,
        ],
        dtype=np.float32,
    )
    return InterdigitalFeatureBundle(
        x_raw=x_raw,
        x_sym=x_sym,
        x_delta=x_delta,
        x_derived=x_derived,
        x_resonator=x_resonator,
        x_gap=x_gap,
        x_feed=x_feed,
    )


def normalize_array(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.nanmean(x, axis=0).astype(np.float32)
    std = np.nanstd(x, axis=0).astype(np.float32)
    std[std < 1e-8] = 1.0
    return ((x - mean) / std).astype(np.float32), mean, std


def value_at_freq(freq_ghz: np.ndarray, values: np.ndarray, target: float) -> float:
    if freq_ghz.size == 0:
        return float("nan")
    return float(np.interp(target, freq_ghz.astype(float), values.astype(float)))


def curve_aux_features(freq_ghz: np.ndarray, curves: np.ndarray) -> np.ndarray:
    s11 = curves[0]
    s21 = curves[1]
    s22 = curves[2]
    pass_mask = (freq_ghz >= 6.0) & (freq_ghz <= 8.0)
    high_mask = (freq_ghz >= 8.5) & (freq_ghz <= 10.0)
    pass_s21 = s21[pass_mask]
    pass_s11 = s11[pass_mask]
    pass_s22 = s22[pass_mask]
    if pass_s21.size:
        pass_min = float(np.nanmin(pass_s21))
        ripple = float(np.nanmax(pass_s21) - np.nanmin(pass_s21))
    else:
        pass_min = float("nan")
        ripple = float("nan")
    high_max = float(np.nanmax(s21[high_mask])) if np.any(high_mask) else float("nan")
    worst_s11 = float(np.nanmax(pass_s11)) if pass_s11.size else float("nan")
    worst_s22 = float(np.nanmax(pass_s22)) if pass_s22.size else float("nan")
    return np.asarray(
        [
            pass_min,
            ripple,
            value_at_freq(freq_ghz, s21, 5.0),
            value_at_freq(freq_ghz, s21, 6.0),
            value_at_freq(freq_ghz, s21, 8.0),
            value_at_freq(freq_ghz, s21, 9.0),
            high_max,
            worst_s11,
            worst_s22,
        ],
        dtype=np.float32,
    )


def interdigital_score(features: Mapping[str, float]) -> float:
    s21_5 = float(features["s21_5g_db"])
    s21_6 = float(features["s21_6g_db"])
    s21_8 = float(features["s21_8g_db"])
    pass_min = float(features["passband_min_s21_db"])
    ripple = float(features["passband_ripple_db"])
    high_stop = float(features.get("high_stop_max_s21_db", features.get("s21_9g_db", -60.0)))
    worst_s11 = float(features["worst_s11_6_8_db"])
    worst_s22 = float(features["worst_s22_6_8_db"])
    worst_return = max(worst_s11, worst_s22)
    hard_penalty = 0.0
    hard_penalty += 70.0 * max(0.0, s21_5 + 25.0) ** 2
    hard_penalty += 70.0 * max(0.0, -5.0 - s21_6) ** 2
    hard_penalty += 70.0 * max(0.0, -5.0 - s21_8) ** 2
    hard_penalty += 80.0 * max(0.0, -5.0 - pass_min) ** 2
    hard_penalty += 10.0 * max(0.0, ripple - 4.0) ** 2
    hard_penalty += 0.8 * max(0.0, high_stop + 20.0) ** 2
    return 100.0 - hard_penalty + 4.0 * (-worst_return) - 1.0 * ripple + 0.4 * min(-25.0 - s21_5, 8.0)
