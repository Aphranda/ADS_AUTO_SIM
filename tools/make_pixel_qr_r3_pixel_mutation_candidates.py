#!/usr/bin/env python3
"""Create R3 add/remove/toggle pixel mutation candidates for pixel QR BPF."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random


FIELDNAMES = [
    "name",
    "matrix_n",
    "pixel_mm",
    "cell_pitch_mm",
    "pixel_overfill_ratio",
    "gap_mm",
    "feed_w_mm",
    "feed_len_mm",
    "coupling_overlap_mm",
    "pattern",
    "custom_mask_rows",
    "seed",
    "fill_probability",
    "mirror_x",
    "force_edge_coupling",
    "connect_adjacent_pixels",
    "substrate",
    "er",
    "h_mm",
    "copper_mm",
    "min_fab_gap_mm",
    "min_fab_feature_mm",
    "metal_layer",
    "via_layer",
    "boundary_layer",
    "notes",
]

LOCKED_PIXELS = {
    (7, 0),
    (7, 15),
    (8, 0),
    (8, 15),
}


def read_params(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mask_from_rows(rows: list[str]) -> list[list[int]]:
    if len(rows) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in rows):
        raise ValueError("R3 generator currently expects a 16x16 binary mask")
    return [[int(ch) for ch in row] for row in rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def enforce_feed_coupling(mask: list[list[int]]) -> None:
    for row, col in LOCKED_PIXELS:
        mask[row][col] = 1


def mirror_pair(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, col), (row, other))


def selectable_pairs(mask: list[list[int]], mode: str) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for row in range(16):
        for col in range(8):
            pair = mirror_pair(row, col)
            if any(pixel in LOCKED_PIXELS for pixel in pair):
                continue
            values = [mask[r][c] for r, c in pair]
            if mode == "add" and any(values):
                continue
            if mode == "remove" and not all(values):
                continue
            pairs.append((row, col))
    return pairs


def mutate(mask: list[list[int]], mode: str, pair_count: int, rng: random.Random) -> list[list[int]]:
    out = [row[:] for row in mask]
    candidates = selectable_pairs(out, mode)
    if len(candidates) < pair_count:
        raise ValueError(f"not enough selectable {mode} pairs: requested {pair_count}, available {len(candidates)}")
    for row, col in rng.sample(candidates, pair_count):
        for rr, cc in mirror_pair(row, col):
            if mode == "add":
                out[rr][cc] = 1
            elif mode == "remove":
                out[rr][cc] = 0
            elif mode == "toggle":
                out[rr][cc] = 1 - out[rr][cc]
            else:
                raise ValueError(f"unsupported mutation mode: {mode}")
    enforce_feed_coupling(out)
    return out


def make_row(base_params: dict[str, object], name: str, rows: list[str], notes: str, seed: int) -> dict[str, str]:
    params = base_params["parameters"]  # type: ignore[index]
    return {
        "name": name,
        "matrix_n": str(params["matrix_n"]),  # type: ignore[index]
        "pixel_mm": f"{float(params['pixel_mm']):.6g}",  # type: ignore[index]
        "cell_pitch_mm": f"{float(params['cell_pitch_mm']):.6g}",  # type: ignore[index]
        "pixel_overfill_ratio": f"{float(params['pixel_overfill_ratio']):.6g}",  # type: ignore[index]
        "gap_mm": f"{float(params['gap_mm']):.6g}",  # type: ignore[index]
        "feed_w_mm": f"{float(params['feed_w_mm']):.6g}",  # type: ignore[index]
        "feed_len_mm": f"{float(params['feed_len_mm']):.6g}",  # type: ignore[index]
        "coupling_overlap_mm": f"{float(params['coupling_overlap_mm']):.6g}",  # type: ignore[index]
        "pattern": "custom",
        "custom_mask_rows": ";".join(rows),
        "seed": str(seed),
        "fill_probability": f"{float(params['fill_probability']):.6g}",  # type: ignore[index]
        "mirror_x": "true",
        "force_edge_coupling": "true",
        "connect_adjacent_pixels": "true",
        "substrate": str(params["substrate"]),  # type: ignore[index]
        "er": f"{float(params['er']):.6g}",  # type: ignore[index]
        "h_mm": f"{float(params['dielectric_height_mm']):.6g}",  # type: ignore[index]
        "copper_mm": f"{float(params['copper_thickness_mm']):.6g}",  # type: ignore[index]
        "min_fab_gap_mm": f"{float(params['min_fab_gap_mm']):.6g}",  # type: ignore[index]
        "min_fab_feature_mm": f"{float(params['min_fab_feature_mm']):.6g}",  # type: ignore[index]
        "metal_layer": str(params["metal_layer"]),  # type: ignore[index]
        "via_layer": str(params["via_layer"]),  # type: ignore[index]
        "boundary_layer": str(params["boundary_layer"]),  # type: ignore[index]
        "notes": notes,
    }


def build_rows(base_path: Path, count_per_mode: int, seed: int) -> list[dict[str, str]]:
    base = read_params(base_path)
    base_mask = mask_from_rows([str(row) for row in base["mask_rows"]])  # type: ignore[index]
    enforce_feed_coupling(base_mask)
    rows: list[dict[str, str]] = []
    schedule = [
        ("add", 2),
        ("add", 4),
        ("remove", 2),
        ("remove", 4),
        ("toggle", 2),
        ("toggle", 4),
    ]
    idx = 0
    for mode, pair_count in schedule:
        for local_idx in range(count_per_mode):
            idx += 1
            local_seed = seed + idx * 101
            rng = random.Random(local_seed)
            mutated = mutate(base_mask, mode, pair_count, rng)
            name = f"pixel_qr16_fr4_210um_r3_{mode}{pair_count:02d}_{local_idx:02d}"
            filled = sum(sum(row) for row in mutated)
            notes = (
                "R3 mirrored pixel mutation from p035_fw038_ol045; "
                f"mode={mode}, pair_count={pair_count}, filled_pixels={filled}/256. "
                "Used for S21 surrogate data collection and 6-8 GHz BPF feedback."
            )
            rows.append(make_row(base, name, mask_rows(mutated), notes, local_seed))
    return rows


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Write R3 pixel mutation candidate plan.")
    parser.add_argument(
        "--base-params",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "layouts"
        / "pixel_qr_bpf_fr4_210um_r1"
        / "pixel_qr16_fr4_210um_seed0_p035_ov10_fw038_ol045_params.json",
    )
    parser.add_argument("--count-per-mode", type=int, default=4)
    parser.add_argument("--seed", type=int, default=3100)
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.base_params, args.count_per_mode, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R3 pixel mutation candidates: {args.out}")


if __name__ == "__main__":
    main()
