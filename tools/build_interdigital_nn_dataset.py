#!/usr/bin/env python3
"""Build a refined-parameter NN dataset for the FR4 7th-order interdigital BPF."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.nn.interdigital_features import (
    AUX_FEATURES,
    DELTA_FEATURES,
    DERIVED_FEATURES,
    FEED_FEATURES,
    GAP_FEATURES,
    PARAM_COLUMNS,
    RESONATOR_FEATURES,
    S_PARAM_NAMES,
    SYMMETRIC_FEATURES,
    curve_aux_features,
    feature_bundle,
    normalize_array,
    params_from_layout_json,
)
from simads.scoring import choose_frequency_column, choose_sparam_column, frequency_to_ghz, series_to_db


DEFAULT_FREQ_GHZ = np.arange(1.0, 10.0001, 0.25, dtype=np.float32)
DEFAULT_MIN_SOURCE_POINTS = 20
DEFAULT_MAX_PASSBAND_STEP_GHZ = 0.50


def repo_root() -> Path:
    return _SIM_ROOT


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_freqs(text: str | None) -> np.ndarray:
    if not text:
        return DEFAULT_FREQ_GHZ.copy()
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise ValueError("--freq-ghz did not contain numeric values")
    return np.asarray(values, dtype=np.float32)


def interpolate_with_valid(xs: np.ndarray, ys: np.ndarray, targets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]
    finite = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[finite]
    ys = ys[finite]
    out = np.full(targets.shape, np.nan, dtype=np.float32)
    valid = np.zeros(targets.shape, dtype=bool)
    if len(xs) < 2:
        return out, valid
    valid = (targets >= xs[0]) & (targets <= xs[-1])
    out[valid] = np.interp(targets[valid], xs, ys).astype(np.float32)
    return out, valid


def max_step_in_band(src_freq: np.ndarray, start_ghz: float, stop_ghz: float) -> float:
    values = np.sort(src_freq[np.isfinite(src_freq) & (src_freq >= start_ghz) & (src_freq <= stop_ghz)])
    if values.size < 2:
        return float("inf")
    return float(np.max(np.diff(values)))


def read_sparams(path: Path, freq_ghz: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty RFPro CSV: {path}")
    columns = list(rows[0])
    freq_col = choose_frequency_column(columns)
    if freq_col is None:
        raise ValueError(f"CSV has no frequency column: {path}")
    src_freq = np.asarray(frequency_to_ghz([row[freq_col] for row in rows]), dtype=np.float64)
    source_meta = {
        "source_points": float(len(src_freq)),
        "source_freq_min_ghz": float(np.nanmin(src_freq)) if len(src_freq) else float("nan"),
        "source_freq_max_ghz": float(np.nanmax(src_freq)) if len(src_freq) else float("nan"),
        "source_max_step_ghz": float(np.nanmax(np.diff(np.sort(src_freq)))) if len(src_freq) > 1 else float("inf"),
        "source_max_step_6_8_ghz": max_step_in_band(src_freq, 6.0, 8.0),
    }
    curves: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    for name in S_PARAM_NAMES:
        col = choose_sparam_column(columns, name)
        if col is None:
            curves.append(np.full(freq_ghz.shape, np.nan, dtype=np.float32))
            masks.append(np.zeros(freq_ghz.shape, dtype=bool))
            continue
        values = np.asarray(series_to_db([row[col] for row in rows]), dtype=np.float64)
        curve, mask = interpolate_with_valid(src_freq, values, freq_ghz)
        curves.append(curve)
        masks.append(mask)
    if not np.any(masks[1]):
        raise ValueError(f"CSV has no usable S21 curve: {path}")
    return np.stack(curves, axis=0), np.stack(masks, axis=0), source_meta


def candidate_name_from_params(path: Path) -> str:
    return path.name.removesuffix("_params.json")


def rfpro_index(results_glob: str) -> dict[str, Path]:
    root = repo_root()
    index: dict[str, Path] = {}
    for path in sorted(root.glob(results_glob)):
        if path.name.endswith("_rfpro.csv"):
            name = path.name.removesuffix("_mm_coords_rfpro.csv").removesuffix("_rfpro.csv")
            index[name] = path
    for summary in sorted(root.glob("projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/sweep_summary.csv")):
        for row in read_csv(summary):
            name = row.get("candidate", "").strip()
            source = row.get("source", "").strip()
            if not name or not source:
                continue
            source_path = Path(source)
            if source_path.exists():
                index[name] = source_path
            else:
                fallback = summary.parent / f"{name}_mm_coords_rfpro.csv"
                if fallback.exists():
                    index[name] = fallback
    return index


def collect_rows(
    layout_glob: str,
    results_glob: str,
    freq_ghz: np.ndarray,
    min_source_points: int,
    max_passband_step_ghz: float,
) -> tuple[dict[str, np.ndarray], list[dict[str, str]]]:
    root = repo_root()
    rfpros = rfpro_index(results_glob)
    arrays: dict[str, list[np.ndarray]] = {
        "x_raw": [],
        "x_sym": [],
        "x_delta": [],
        "x_derived": [],
        "x_resonator": [],
        "x_gap": [],
        "x_feed": [],
        "y_s_db": [],
        "valid_s_mask": [],
        "y_aux": [],
    }
    manifest: list[dict[str, str]] = []
    seen: set[str] = set()
    for params_path in sorted(root.glob(layout_glob)):
        candidate = candidate_name_from_params(params_path)
        if candidate in seen or candidate not in rfpros:
            continue
        try:
            params = params_from_layout_json(read_json(params_path))
            curves, mask, source_meta = read_sparams(rfpros[candidate], freq_ghz)
            source_points = int(source_meta["source_points"])
            passband_step = float(source_meta["source_max_step_6_8_ghz"])
            if source_points < min_source_points:
                raise ValueError(f"only {source_points} source points, need >= {min_source_points}")
            if passband_step > max_passband_step_ghz:
                raise ValueError(
                    f"6-8 GHz source step {passband_step:.6g} GHz exceeds {max_passband_step_ghz:.6g} GHz"
                )
        except Exception as exc:
            print(f"skip {candidate}: {exc}")
            continue
        bundle = feature_bundle(params)
        arrays["x_raw"].append(bundle.x_raw)
        arrays["x_sym"].append(bundle.x_sym)
        arrays["x_delta"].append(bundle.x_delta)
        arrays["x_derived"].append(bundle.x_derived)
        arrays["x_resonator"].append(bundle.x_resonator)
        arrays["x_gap"].append(bundle.x_gap)
        arrays["x_feed"].append(bundle.x_feed)
        arrays["y_s_db"].append(curves)
        arrays["valid_s_mask"].append(mask)
        arrays["y_aux"].append(curve_aux_features(freq_ghz, curves))
        manifest.append(
            {
                "candidate": candidate,
                "params": str(params_path),
                "rfpro": str(rfpros[candidate]),
                "source_points": str(int(source_meta["source_points"])),
                "source_freq_min_ghz": f"{source_meta['source_freq_min_ghz']:.6g}",
                "source_freq_max_ghz": f"{source_meta['source_freq_max_ghz']:.6g}",
                "source_max_step_ghz": f"{source_meta['source_max_step_ghz']:.6g}",
                "source_max_step_6_8_ghz": f"{source_meta['source_max_step_6_8_ghz']:.6g}",
                "freq_min_ghz": f"{float(np.nanmin(freq_ghz[mask[1]])):.6g}" if np.any(mask[1]) else "",
                "freq_max_ghz": f"{float(np.nanmax(freq_ghz[mask[1]])):.6g}" if np.any(mask[1]) else "",
            }
        )
        seen.add(candidate)
    if not arrays["y_s_db"]:
        raise SystemExit("No interdigital RFPro samples found.")
    out = {key: np.stack(value, axis=0).astype(np.float32) for key, value in arrays.items()}
    out["valid_s_mask"] = out["valid_s_mask"].astype(bool)
    return out, manifest


def add_normalized(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    output = dict(arrays)
    for key in ("x_raw", "x_sym", "x_delta", "x_derived", "x_resonator", "x_gap", "x_feed", "y_aux"):
        norm, mean, std = normalize_array(arrays[key])
        output[f"{key}_norm"] = norm
        output[f"{key}_mean"] = mean
        output[f"{key}_std"] = std
    return output


def write_manifest(path: Path, manifest: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Build interdigital refined-parameter NN dataset.")
    parser.add_argument("--layout-glob", default="projects/bfp_6_8g_i7_fr4/layouts/interdigital_7o_fr4_210um_round*/i7_fr4_*_params.json")
    parser.add_argument("--results-glob", default="projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/*_rfpro.csv")
    parser.add_argument("--freq-ghz", default=None, help="Comma-separated target frequency grid. Default: 1:0.25:10 GHz.")
    parser.add_argument("--min-source-points", type=int, default=DEFAULT_MIN_SOURCE_POINTS)
    parser.add_argument("--max-passband-step-ghz", type=float, default=DEFAULT_MAX_PASSBAND_STEP_GHZ)
    parser.add_argument("--out", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_refined_nn_dataset.npz")
    parser.add_argument("--manifest-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    freq_ghz = parse_freqs(args.freq_ghz)
    arrays, manifest = collect_rows(
        args.layout_glob,
        args.results_glob,
        freq_ghz,
        args.min_source_points,
        args.max_passband_step_ghz,
    )
    arrays = add_normalized(arrays)
    metadata = {
        "schema": "interdigital_refined_nn_dataset_v1",
        "param_columns": PARAM_COLUMNS,
        "symmetric_features": SYMMETRIC_FEATURES,
        "delta_features": DELTA_FEATURES,
        "resonator_features": RESONATOR_FEATURES,
        "gap_features": GAP_FEATURES,
        "feed_features": FEED_FEATURES,
        "derived_features": DERIVED_FEATURES,
        "sparam_names": S_PARAM_NAMES,
        "aux_features": AUX_FEATURES,
        "min_source_points": args.min_source_points,
        "max_passband_step_ghz": args.max_passband_step_ghz,
        "samples": len(manifest),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out,
        **arrays,
        freq_ghz=freq_ghz.astype(np.float32),
        candidate_names=np.asarray([row["candidate"] for row in manifest]),
        metadata_json=json.dumps(metadata, ensure_ascii=False),
    )
    manifest_out = args.manifest_out or args.out.with_suffix(".manifest.csv")
    write_manifest(manifest_out, manifest)
    print(f"Wrote {len(manifest)} samples: {args.out}")
    print(f"Wrote manifest: {manifest_out}")


if __name__ == "__main__":
    main()
