#!/usr/bin/env python3
"""Rank pixel QR candidate masks with a trained S21 surrogate checkpoint."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.nn import PixelQrS21Surrogate, require_torch, s21_bandpass_features

VIA_DIAMETER_NORM_MM = 0.18


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def parse_mask_rows(text: str) -> list[str]:
    rows = [part.strip() for part in text.replace("/", ";").split(";") if part.strip()]
    if not rows:
        raise ValueError("candidate has no custom_mask_rows; generate layout params first or use custom plans")
    width = len(rows[0])
    if any(len(row) != width or set(row) - {"0", "1"} for row in rows):
        raise ValueError(f"invalid mask rows: {rows}")
    return rows


def mask_to_array(rows: list[str]) -> np.ndarray:
    return np.asarray([[float(ch) for ch in row] for row in rows], dtype=np.float32)


def diameter_rows_to_array(text: str, shape: tuple[int, int]) -> np.ndarray:
    if not text.strip():
        return np.zeros(shape, dtype=np.float32)
    rows = [part.strip() for part in text.replace("/", ";").split(";") if part.strip()]
    values = [[float(part.strip()) for part in row.split(",") if part.strip()] for row in rows]
    out = np.asarray(values, dtype=np.float32)
    if out.shape != shape:
        raise ValueError(f"via_diameter_rows shape {out.shape} does not match mask shape {shape}")
    if np.any(out < 0.0):
        raise ValueError("via_diameter_rows may not contain negative diameters")
    return out


def optional_float_map(row: dict[str, str], key: str, shape: tuple[int, int]) -> np.ndarray:
    return diameter_rows_to_array(row.get(key, ""), shape)


def fmt(value: float) -> str:
    return f"{value:.6g}"


def float_field(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key, "").strip()
    return float(value) if value else default


def geom_vector(row: dict[str, str], via_diameter: float, geom_features: int) -> np.ndarray:
    pixel_mm = float_field(row, "pixel_mm", 0.35)
    cell_pitch_mm = float_field(row, "cell_pitch_mm", pixel_mm)
    if cell_pitch_mm <= 0:
        cell_pitch_mm = pixel_mm
    base5 = [
        pixel_mm / 0.35,
        cell_pitch_mm / 0.35,
        float_field(row, "feed_w_mm", 0.38) / 0.38,
        float_field(row, "coupling_overlap_mm", 0.45) / 0.45,
        via_diameter / VIA_DIAMETER_NORM_MM,
    ]
    if geom_features == 5:
        return np.asarray(base5, dtype=np.float32)
    base7 = [
        pixel_mm / 0.35,
        cell_pitch_mm / 0.35,
        float_field(row, "pixel_overfill_ratio", 0.1) / 0.1,
        float_field(row, "gap_mm", 0.0) / 0.1016,
        float_field(row, "feed_w_mm", 0.38) / 0.38,
        float_field(row, "coupling_overlap_mm", 0.45) / 0.45,
        via_diameter / VIA_DIAMETER_NORM_MM,
    ]
    if geom_features == 7:
        return np.asarray(base7, dtype=np.float32)
    raise ValueError(f"unsupported checkpoint geom_features={geom_features}; expected 5 or 7")


def value_at_freq(freq_ghz: np.ndarray, values: np.ndarray, target: float) -> float:
    if freq_ghz.size == 0:
        return float("nan")
    idx = int(np.argmin(np.abs(freq_ghz - target)))
    if abs(float(freq_ghz[idx]) - target) < 1e-6:
        return float(values[idx])
    return float(np.interp(target, freq_ghz.astype(float), values.astype(float)))


def guarded_r4_score(
    *,
    bandpass_score: float,
    passband_min_db: float,
    passband_ripple_db: float,
    s21_5g_db: float,
    s21_6g_db: float,
    s21_8g_db: float,
    high_stop_max_db: float,
    guard_db: float,
) -> float:
    score = bandpass_score
    # The guarded score is used to choose expensive ADS runs. R8 showed that
    # a slightly deeper 5 GHz notch can hide a marginal 6-8 GHz internal dip,
    # so rank by passband margin before rewarding further notch depth.
    score += 45.0 * passband_min_db
    score -= 12.0 * max(0.0, passband_ripple_db)
    score -= 90.0 * max(0.0, guard_db - passband_min_db) ** 2
    score -= 60.0 * max(0.0, guard_db - s21_6g_db) ** 2
    score -= 60.0 * max(0.0, guard_db - s21_8g_db) ** 2
    score -= 55.0 * max(0.0, (guard_db + 1.5) - passband_min_db) ** 2
    score -= 5.0 * max(0.0, passband_ripple_db - 4.5) ** 2
    score -= 0.9 * max(0.0, s21_5g_db + 20.0) ** 2
    score -= 0.8 * max(0.0, high_stop_max_db + 20.0) ** 2
    return score


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Rank pixel QR plan candidates using a trained S21 surrogate.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "results" / "pixel_qr_s21_surrogate.pt",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "results" / "pixel_qr_r3_surrogate_ranking.csv",
    )
    parser.add_argument("--sort-mode", choices=["bandpass", "guarded-r4"], default="bandpass")
    parser.add_argument("--guard-db", type=float, default=-5.5, help="Guard threshold for --sort-mode guarded-r4.")
    return parser.parse_args()


def main() -> None:
    torch = require_torch()
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    config = checkpoint["model_config"]
    freq_ghz = np.asarray(checkpoint["freq_ghz"], dtype=np.float32)
    model = PixelQrS21Surrogate(**config)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    rows = read_csv(args.plan)
    names: list[str] = []
    masks: list[np.ndarray] = []
    geoms: list[np.ndarray] = []
    notes: list[str] = []
    for row in rows:
        candidate = row["name"].strip()
        mask_rows = parse_mask_rows(row.get("custom_mask_rows", ""))
        mask = mask_to_array(mask_rows)
        if mask.shape != (config["matrix_n"], config["matrix_n"]):
            raise ValueError(f"{candidate} mask shape {mask.shape} does not match model matrix_n={config['matrix_n']}")
        mask_channels = int(config.get("mask_channels", 1))
        if mask_channels > 1:
            via_diameter = float(row.get("via_diameter_mm") or VIA_DIAMETER_NORM_MM)
            via_diameter_map = diameter_rows_to_array(row.get("via_diameter_rows", ""), mask.shape)
            if np.any(via_diameter_map):
                via_diameter = float(np.max(via_diameter_map))
                via_channel = via_diameter_map / VIA_DIAMETER_NORM_MM
            else:
                via_text = row.get("via_mask_rows", "")
                if via_text.strip():
                    via_rows = parse_mask_rows(via_text)
                    via_mask = mask_to_array(via_rows)
                else:
                    via_mask = np.zeros_like(mask, dtype=np.float32)
                if via_mask.shape != mask.shape:
                    raise ValueError(f"{candidate} via mask shape {via_mask.shape} does not match metal mask shape {mask.shape}")
                via_channel = via_mask * (via_diameter / VIA_DIAMETER_NORM_MM)
            if mask_channels >= 6:
                stub_len_channel = optional_float_map(row, "sub_stub_len_rows", mask.shape) / 0.35
                stub_w_channel = optional_float_map(row, "sub_stub_w_rows", mask.shape) / 0.35
                pad_channel = optional_float_map(row, "sub_pad_rows", mask.shape) / 0.35
                slot_gap_channel = optional_float_map(row, "sub_slot_gap_rows", mask.shape) / 0.1016
                stacked = np.stack([mask, via_channel, stub_len_channel, stub_w_channel, pad_channel, slot_gap_channel], axis=0)
            else:
                stacked = np.stack([mask, via_channel], axis=0)
        else:
            via_diameter = float(row.get("via_diameter_mm") or VIA_DIAMETER_NORM_MM)
            stacked = mask[None, :, :]
        names.append(candidate)
        masks.append(stacked)
        geom_feature_count = int(config.get("geom_features", 0))
        if geom_feature_count > 0:
            geoms.append(geom_vector(row, via_diameter, geom_feature_count))
        notes.append(row.get("notes", ""))

    x = torch.tensor(np.stack(masks, axis=0), dtype=torch.float32)
    geom = torch.tensor(np.stack(geoms, axis=0), dtype=torch.float32) if geoms else None
    with torch.no_grad():
        pred = model(x, geom).detach().cpu().numpy()
    pred_s21 = pred[:, 1, :] if pred.ndim == 3 else pred

    output_rows: list[dict[str, str]] = []
    for idx, candidate in enumerate(names):
        features = s21_bandpass_features(freq_ghz.tolist(), pred_s21[idx].tolist())
        s21_6g_db = value_at_freq(freq_ghz, pred_s21[idx], 6.0)
        s21_8g_db = value_at_freq(freq_ghz, pred_s21[idx], 8.0)
        guard_pass = (
            features.passband_min_db >= args.guard_db
            and s21_6g_db >= args.guard_db
            and s21_8g_db >= args.guard_db
        )
        r4_score = guarded_r4_score(
            bandpass_score=features.bandpass_score,
            passband_min_db=features.passband_min_db,
            passband_ripple_db=features.passband_ripple_db,
            s21_5g_db=features.s21_5g_db,
            s21_6g_db=s21_6g_db,
            s21_8g_db=s21_8g_db,
            high_stop_max_db=features.high_stop_max_db,
            guard_db=args.guard_db,
        )
        row = {
            "rank": "",
            "candidate": candidate,
            "pred_passband_min_s21_db": fmt(features.passband_min_db),
            "pred_passband_avg_s21_db": fmt(features.passband_avg_db),
            "pred_passband_ripple_db": fmt(features.passband_ripple_db),
            "pred_s21_5g_db": fmt(features.s21_5g_db),
            "pred_s21_6g_db": fmt(s21_6g_db),
            "pred_s21_8g_db": fmt(s21_8g_db),
            "pred_low_stop_max_s21_db": fmt(features.low_stop_max_db),
            "pred_high_stop_max_s21_db": fmt(features.high_stop_max_db),
            "pred_bandpass_score_s21": fmt(features.bandpass_score),
            "pred_guard_pass": "true" if guard_pass else "false",
            "pred_guarded_r4_score": fmt(r4_score),
            "notes": notes[idx],
        }
        for freq_idx, freq in enumerate(freq_ghz):
            label = f"pred_s21_{float(freq):.2f}g_db".replace(".", "p")
            row[label] = fmt(float(pred_s21[idx, freq_idx]))
            if pred.ndim == 3:
                row[f"pred_s11_{float(freq):.2f}g_db".replace(".", "p")] = fmt(float(pred[idx, 0, freq_idx]))
                row[f"pred_s22_{float(freq):.2f}g_db".replace(".", "p")] = fmt(float(pred[idx, 2, freq_idx]))
        output_rows.append(row)

    if args.sort_mode == "guarded-r4":
        output_rows.sort(
            key=lambda row: (row["pred_guard_pass"] == "true", float(row["pred_guarded_r4_score"])),
            reverse=True,
        )
    else:
        output_rows.sort(key=lambda row: float(row["pred_bandpass_score_s21"]), reverse=True)
    for idx, row in enumerate(output_rows, start=1):
        row["rank"] = str(idx)
    write_rows(args.out, output_rows)
    print(f"Wrote surrogate ranking for {len(output_rows)} candidates: {args.out}")
    print("Top candidates:")
    for row in output_rows[:8]:
        print(
            f"  #{row['rank']} {row['candidate']}: score={row['pred_bandpass_score_s21']} "
            f"guarded={row['pred_guarded_r4_score']} "
            f"pass_min={row['pred_passband_min_s21_db']} "
            f"s21_5g={row['pred_s21_5g_db']} "
            f"guard={row['pred_guard_pass']} "
            f"low_stop={row['pred_low_stop_max_s21_db']} high_stop={row['pred_high_stop_max_s21_db']}"
        )


if __name__ == "__main__":
    main()
