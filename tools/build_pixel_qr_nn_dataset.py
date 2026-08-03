#!/usr/bin/env python3
"""Build a neural-network dataset for pixel QR BPF S-parameter candidates."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import load_project
from simads.nn.pixel_qr_surrogate import s21_bandpass_features


DEFAULT_FREQ_GHZ = np.linspace(1.0, 10.0, 19, dtype=np.float32)
VIA_DIAMETER_NORM_MM = 0.18
GEOM_FEATURES = [
    "pixel_mm_norm_0p35",
    "cell_pitch_mm_norm_0p35",
    "pixel_overfill_ratio_norm_0p10",
    "gap_mm_norm_0p1016",
    "feed_w_mm_norm_0p38",
    "coupling_overlap_mm_norm_0p45",
    "via_diameter_mm_norm_0p18",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


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
        raise ValueError("--freq-ghz did not contain any numeric values")
    return np.asarray(values, dtype=np.float32)


def mask_to_array(rows: Iterable[str]) -> np.ndarray:
    clean_rows = [str(row).strip() for row in rows]
    if not clean_rows:
        raise ValueError("missing mask_rows")
    width = len(clean_rows[0])
    if any(len(row) != width or set(row) - {"0", "1"} for row in clean_rows):
        raise ValueError(f"invalid mask rows: {clean_rows}")
    return np.asarray([[float(ch) for ch in row] for row in clean_rows], dtype=np.float32)


def diameter_rows_to_array(rows: Iterable[str], shape: tuple[int, int]) -> np.ndarray:
    clean_rows = [str(row).strip() for row in rows if str(row).strip()]
    if not clean_rows:
        return np.zeros(shape, dtype=np.float32)
    values: list[list[float]] = []
    for row in clean_rows:
        parts = [part.strip() for part in row.split(",")]
        values.append([float(part) for part in parts])
    out = np.asarray(values, dtype=np.float32)
    if out.shape != shape:
        raise ValueError(f"via_diameter_rows shape {out.shape} differs from mask shape {shape}")
    if np.any(out < 0.0):
        raise ValueError("via_diameter_rows may not contain negative diameters")
    return out


def optional_float_map(params: dict[str, object], key: str, shape: tuple[int, int]) -> np.ndarray:
    rows = params.get(key, [])
    if not rows:
        return np.zeros(shape, dtype=np.float32)
    return diameter_rows_to_array(rows, shape)  # type: ignore[arg-type]


def interpolate_with_valid(xs: np.ndarray, ys: np.ndarray, targets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]
    valid = (targets >= xs[0]) & (targets <= xs[-1])
    out = np.full(targets.shape, np.nan, dtype=np.float32)
    if np.any(valid):
        out[valid] = np.interp(targets[valid], xs, ys).astype(np.float32)
    return out, valid


def read_sparam_trace(
    path: Path,
    freq_ghz: np.ndarray,
    name: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"empty RFPro CSV: {path}")
    required = {"frequency_hz", f"{name}_db", f"{name}_mag", f"{name}_phase_deg"}
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(f"{path} missing columns: {', '.join(missing)}")

    src_freq = np.asarray([float(row["frequency_hz"]) / 1e9 for row in rows], dtype=np.float64)
    sparam_db = np.asarray([float(row[f"{name}_db"]) for row in rows], dtype=np.float64)
    sparam_mag = np.asarray([float(row[f"{name}_mag"]) for row in rows], dtype=np.float64)
    phase_rad = np.deg2rad(np.asarray([float(row[f"{name}_phase_deg"]) for row in rows], dtype=np.float64))
    real = sparam_mag * np.cos(phase_rad)
    imag = sparam_mag * np.sin(phase_rad)

    y_db, valid = interpolate_with_valid(src_freq, sparam_db, freq_ghz)
    y_real, valid_real = interpolate_with_valid(src_freq, real, freq_ghz)
    y_imag, valid_imag = interpolate_with_valid(src_freq, imag, freq_ghz)
    return y_db, np.stack([y_real, y_imag], axis=-1).astype(np.float32), valid, valid_real & valid_imag


def candidate_rfpro_path(summary: dict[str, str], results_dir: Path, candidate: str) -> Path:
    source = summary.get("source", "").strip()
    if source:
        path = Path(source)
        if path.exists():
            return path
    return results_dir / f"{candidate}_mm_coords_rfpro.csv"


def fmt(value: float) -> str:
    return "" if not math.isfinite(value) else f"{value:.6g}"


def float_param(parameters: dict[str, object], key: str, default: float) -> float:
    value = parameters.get(key, default)
    if value in {"", None}:
        return default
    return float(value)


def geom_vector(parameters: dict[str, object], via_diameter_mm: float) -> np.ndarray:
    pixel_mm = float_param(parameters, "pixel_mm", 0.35)
    cell_pitch_mm = float_param(parameters, "cell_pitch_mm", pixel_mm)
    if cell_pitch_mm <= 0:
        cell_pitch_mm = pixel_mm
    overfill_ratio = float_param(parameters, "pixel_overfill_ratio", 0.1)
    gap_mm = float_param(parameters, "gap_mm", 0.0)
    feed_w_mm = float_param(parameters, "feed_w_mm", 0.38)
    overlap_mm = float_param(parameters, "coupling_overlap_mm", 0.45)
    return np.asarray(
        [
            pixel_mm / 0.35,
            cell_pitch_mm / 0.35,
            overfill_ratio / 0.1,
            gap_mm / 0.1016,
            feed_w_mm / 0.38,
            overlap_mm / 0.45,
            via_diameter_mm / VIA_DIAMETER_NORM_MM,
        ],
        dtype=np.float32,
    )


def build_dataset(project_id: str, sweep_ids: list[str], freq_ghz: np.ndarray) -> tuple[dict[str, np.ndarray], list[dict[str, str]], dict[str, object]]:
    root = repo_root()
    project = load_project(project_id, root=root)
    x_masks: list[np.ndarray] = []
    y_s_db: list[np.ndarray] = []
    y_s_complex: list[np.ndarray] = []
    y_s21_db: list[np.ndarray] = []
    y_s21_complex: list[np.ndarray] = []
    valid_db: list[np.ndarray] = []
    valid_complex: list[np.ndarray] = []
    x_geom: list[np.ndarray] = []
    names: list[str] = []
    mask_rows_out: list[str] = []
    via_mask_rows_out: list[str] = []
    via_diameter_rows_out: list[str] = []
    manifest: list[dict[str, str]] = []
    matrix_n: int | None = None

    for sweep_id in sweep_ids:
        sweep = project.get_sweep(sweep_id)
        if sweep is None or sweep.summary is None or sweep.layouts_dir is None or sweep.results_dir is None:
            raise ValueError(f"sweep {sweep_id!r} is missing summary/layout/results config")
        summaries = read_csv(sweep.summary)
        for summary in summaries:
            if summary.get("status", "").strip().upper() not in {"TUNE", "PASS_CANDIDATE", "PASS"}:
                continue
            candidate = summary["candidate"].strip()
            params_path = sweep.layouts_dir / f"{candidate}_params.json"
            rfpro_path = candidate_rfpro_path(summary, sweep.results_dir, candidate)
            if not params_path.exists() or not rfpro_path.exists():
                continue
            params = read_json(params_path)
            rows = [str(row) for row in params["mask_rows"]]  # type: ignore[index]
            mask = mask_to_array(rows)
            via_rows = [str(row) for row in params.get("via_mask_rows", [])]  # type: ignore[arg-type]
            if via_rows:
                via_mask = mask_to_array(via_rows)
            else:
                via_rows = ["0" * len(rows[0]) for _ in rows]
                via_mask = np.zeros_like(mask, dtype=np.float32)
            parameters = params.get("parameters", {})  # type: ignore[assignment]
            via_diameter_mm = float_param(parameters, "via_diameter_mm", VIA_DIAMETER_NORM_MM)  # type: ignore[arg-type]
            via_diameter_rows = params.get("via_diameter_rows", [])  # type: ignore[assignment]
            via_diameter_map = diameter_rows_to_array(via_diameter_rows, mask.shape)  # type: ignore[arg-type]
            if not np.any(via_diameter_map):
                via_diameter_map = via_mask * via_diameter_mm
            else:
                via_mask = (via_diameter_map > 0.0).astype(np.float32)
                via_rows = ["".join("1" if value > 0.0 else "0" for value in row) for row in via_diameter_map]
            effective_via_diameter_mm = float(np.max(via_diameter_map)) if np.any(via_diameter_map) else via_diameter_mm
            via_channel = via_diameter_map / VIA_DIAMETER_NORM_MM
            stub_len_channel = optional_float_map(params, "sub_stub_len_rows", mask.shape) / 0.35
            stub_w_channel = optional_float_map(params, "sub_stub_w_rows", mask.shape) / 0.35
            pad_channel = optional_float_map(params, "sub_pad_rows", mask.shape) / 0.35
            slot_gap_channel = optional_float_map(params, "sub_slot_gap_rows", mask.shape) / 0.1016
            geom = geom_vector(parameters, effective_via_diameter_mm)  # type: ignore[arg-type]
            via_diameter_rows_text = ";".join(",".join(fmt(float(value)) for value in row) for row in via_diameter_map)
            if matrix_n is None:
                matrix_n = int(mask.shape[0])
            if mask.shape != (matrix_n, matrix_n):
                raise ValueError(f"{candidate} mask shape {mask.shape} differs from first mask {(matrix_n, matrix_n)}")
            if via_mask.shape != (matrix_n, matrix_n):
                raise ValueError(f"{candidate} via mask shape {via_mask.shape} differs from first mask {(matrix_n, matrix_n)}")
            s11_db, s11_complex, s11_db_mask, s11_complex_mask = read_sparam_trace(rfpro_path, freq_ghz, "s11")
            s21_db, s21_complex, s21_db_mask, s21_complex_mask = read_sparam_trace(rfpro_path, freq_ghz, "s21")
            s22_db, s22_complex, s22_db_mask, s22_complex_mask = read_sparam_trace(rfpro_path, freq_ghz, "s22")
            db = s21_db
            db_mask = s21_db_mask
            s_db = np.stack([s11_db, s21_db, s22_db], axis=0)
            s_complex = np.stack([s11_complex, s21_complex, s22_complex], axis=0)
            s_db_mask = np.stack([s11_db_mask, s21_db_mask, s22_db_mask], axis=0)
            s_complex_mask = np.stack([s11_complex_mask, s21_complex_mask, s22_complex_mask], axis=0)
            features = s21_bandpass_features(freq_ghz.tolist(), s21_db.tolist())

            names.append(candidate)
            mask_rows_out.append(";".join(rows))
            via_mask_rows_out.append(";".join(via_rows))
            via_diameter_rows_out.append(via_diameter_rows_text)
            x_masks.append(np.stack([mask, via_channel, stub_len_channel, stub_w_channel, pad_channel, slot_gap_channel], axis=0))
            x_geom.append(geom)
            y_s_db.append(s_db)
            y_s_complex.append(s_complex)
            y_s21_db.append(s21_db)
            y_s21_complex.append(s21_complex)
            valid_db.append(s_db_mask)
            valid_complex.append(s_complex_mask)
            manifest.append(
                {
                    "candidate": candidate,
                    "sweep_id": sweep_id,
                    "params_json": str(params_path),
                    "rfpro_csv": str(rfpro_path),
                    "freq_min_ghz": fmt(float(np.nanmin(freq_ghz[db_mask])) if np.any(db_mask) else float("nan")),
                    "freq_max_ghz": fmt(float(np.nanmax(freq_ghz[db_mask])) if np.any(db_mask) else float("nan")),
                    "valid_freq_count": str(int(np.sum(db_mask))),
                    "via_count": str(int(np.sum(via_mask))),
                    "via_diameter_mm": fmt(effective_via_diameter_mm if np.any(via_mask) else 0.0),
                    "pixel_mm": fmt(float_param(parameters, "pixel_mm", 0.35)),  # type: ignore[arg-type]
                    "cell_pitch_mm": fmt(float_param(parameters, "cell_pitch_mm", float_param(parameters, "pixel_mm", 0.35))),  # type: ignore[arg-type]
                    "pixel_overfill_ratio": fmt(float_param(parameters, "pixel_overfill_ratio", 0.1)),  # type: ignore[arg-type]
                    "gap_mm": fmt(float_param(parameters, "gap_mm", 0.0)),  # type: ignore[arg-type]
                    "feed_w_mm": fmt(float_param(parameters, "feed_w_mm", 0.38)),  # type: ignore[arg-type]
                    "coupling_overlap_mm": fmt(float_param(parameters, "coupling_overlap_mm", 0.45)),  # type: ignore[arg-type]
                    "passband_min_s21_db": fmt(features.passband_min_db),
                    "passband_avg_s21_db": fmt(features.passband_avg_db),
                    "passband_ripple_db": fmt(features.passband_ripple_db),
                    "s21_5g_db": fmt(features.s21_5g_db),
                    "low_stop_max_s21_db": fmt(features.low_stop_max_db),
                    "high_stop_max_s21_db": fmt(features.high_stop_max_db),
                    "bandpass_score_s21": fmt(features.bandpass_score),
                }
            )

    if not x_masks:
        raise ValueError("no usable candidates found for the requested sweeps")

    arrays = {
        "x_mask": np.stack(x_masks, axis=0).astype(np.float32),
        "x_geom": np.stack(x_geom, axis=0).astype(np.float32),
        "freq_ghz": freq_ghz.astype(np.float32),
        "y_s_db": np.stack(y_s_db, axis=0).astype(np.float32),
        "y_s_complex": np.stack(y_s_complex, axis=0).astype(np.float32),
        "y_s21_db": np.stack(y_s21_db, axis=0).astype(np.float32),
        "y_s21_complex": np.stack(y_s21_complex, axis=0).astype(np.float32),
        "valid_s_mask": np.stack(valid_db, axis=0).astype(bool),
        "valid_s_complex_mask": np.stack(valid_complex, axis=0).astype(bool),
        "valid_freq_mask": np.stack([mask[1] for mask in valid_db], axis=0).astype(bool),
        "valid_complex_mask": np.stack([mask[1] for mask in valid_complex], axis=0).astype(bool),
        "candidate_names": np.asarray(names),
        "mask_rows": np.asarray(mask_rows_out),
        "via_mask_rows": np.asarray(via_mask_rows_out),
        "via_diameter_rows": np.asarray(via_diameter_rows_out),
    }
    metadata = {
        "project_id": project_id,
        "sweep_ids": sweep_ids,
        "target": "S-parameter surrogate with S21-primary feedback and low-weight S11/S22 reflection supervision",
        "x_mask_shape": list(arrays["x_mask"].shape),
        "x_mask_channels": [
            "metal",
            f"ground_via_diameter_norm_{VIA_DIAMETER_NORM_MM:g}mm",
            "sub_stub_len_norm_0p35mm",
            "sub_stub_w_norm_0p35mm",
            "sub_pad_side_norm_0p35mm",
            "sub_slot_gap_norm_0p1016mm",
        ],
        "x_geom_shape": list(arrays["x_geom"].shape),
        "x_geom_features": GEOM_FEATURES,
        "y_s21_db_shape": list(arrays["y_s21_db"].shape),
        "y_s_db_shape": list(arrays["y_s_db"].shape),
        "sparam_names": ["s11", "s21", "s22"],
        "sparam_training_weights": {"s11": 0.1, "s21": 1.0, "s22": 0.1},
        "freq_ghz": [float(value) for value in freq_ghz],
        "missing_frequency_policy": "valid_freq_mask marks unavailable frequencies; training loss must ignore them",
    }
    return arrays, manifest, metadata


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pixel QR S21 neural-network dataset from RFPro CSV results.")
    parser.add_argument("--project-id", default="pixel_qr_bpf_fr4_210um")
    parser.add_argument("--sweep-id", action="append", required=True, help="May be repeated.")
    parser.add_argument("--freq-ghz", default=None, help="Comma-separated output frequencies. Default: 1.0,1.5,...,10.0")
    parser.add_argument(
        "--out",
        type=Path,
        default=repo_root() / "projects" / "pixel_qr_bpf_fr4_210um" / "results" / "pixel_qr_s21_nn_dataset.npz",
    )
    parser.add_argument("--manifest-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    freq_ghz = parse_freqs(args.freq_ghz)
    arrays, manifest, metadata = build_dataset(args.project_id, args.sweep_id, freq_ghz)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, **arrays, metadata_json=json.dumps(metadata, ensure_ascii=False))
    manifest_out = args.manifest_out or args.out.with_suffix(".manifest.csv")
    write_manifest(manifest, manifest_out)
    print(f"Wrote {arrays['x_mask'].shape[0]} candidates: {args.out}")
    print(f"Wrote manifest: {manifest_out}")
    print(f"Target frequencies: {', '.join(f'{float(value):.2g}' for value in freq_ghz)} GHz")


if __name__ == "__main__":
    main()
