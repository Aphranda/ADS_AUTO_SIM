#!/usr/bin/env python3
"""Create R2 architecture exploration candidates for the pixel QR BPF project."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


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

BASE_MASK = [
    "1111010110101111",
    "1110100110010111",
    "1110100110010111",
    "1110001111000111",
    "1001010110101001",
    "1101101111011011",
    "1001110110111001",
    "1000000110000001",
    "1111111111111111",
    "0011000110001100",
    "0001010110101000",
    "0000100110010000",
    "0101001111001010",
    "1101011111101011",
    "1000010110100001",
    "0110110110110110",
]


def assert_mask(rows: list[str]) -> list[str]:
    if len(rows) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in rows):
        raise ValueError(f"invalid mask: {rows}")
    for row in (7, 8):
        chars = list(rows[row])
        chars[0] = "1"
        chars[-1] = "1"
        rows[row] = "".join(chars)
    return rows


def row_from_cols(cols: set[int]) -> str:
    return "".join("1" if idx in cols else "0" for idx in range(16))


def spine_sparse() -> list[str]:
    rows = []
    upper = {2, 5, 8, 11, 14}
    lower = {1, 4, 7, 10, 13}
    for idx in range(16):
        if idx in {7, 8}:
            rows.append("1111111111111111")
        elif idx < 7:
            rows.append(row_from_cols(upper))
        else:
            rows.append(row_from_cols(lower))
    return assert_mask(rows)


def dual_rail_ladder() -> list[str]:
    rung = {0, 2, 5, 10, 13, 15}
    rows = []
    for idx in range(16):
        if idx in {5, 10}:
            rows.append("1111111111111111")
        elif 5 < idx < 10:
            rows.append(row_from_cols(rung))
        else:
            rows.append(row_from_cols({2, 5, 10, 13}))
    return assert_mask(rows)


def comb_teeth() -> list[str]:
    rows = []
    for idx in range(16):
        if idx in {7, 8}:
            rows.append("1111111111111111")
        elif idx < 7:
            cols = {2, 5, 8, 11, 14}
            if idx < 2:
                cols = {2, 8, 14}
            rows.append(row_from_cols(cols))
        else:
            cols = {1, 4, 7, 10, 13}
            if idx > 13:
                cols = {1, 7, 13}
            rows.append(row_from_cols(cols))
    return assert_mask(rows)


def split_ring() -> list[str]:
    rows = []
    for idx in range(16):
        if idx in {0, 15}:
            rows.append("1111111111111111")
        elif idx in {7, 8}:
            rows.append("1111110000111111")
        elif idx in {3, 12}:
            rows.append("1001111111111001")
        else:
            rows.append("1001000000001001")
    return assert_mask(rows)


def capacitive_gap() -> list[str]:
    rows = []
    for idx in range(16):
        if idx in {6, 7, 8, 9}:
            rows.append("1111111001111111")
        elif idx in {4, 5, 10, 11}:
            rows.append("1111000000001111")
        else:
            rows.append("1100000000000011")
    return assert_mask(rows)


def diag_cross() -> list[str]:
    rows = []
    for row in range(16):
        cols = {col for col in range(16) if abs(row - col) <= 1 or abs(row + col - 15) <= 1}
        if row in {7, 8}:
            cols.update(range(16))
        rows.append(row_from_cols(cols))
    return assert_mask(rows)


def edge_stubs() -> list[str]:
    rows = []
    for idx in range(16):
        cols = {0, 15}
        if idx in {7, 8}:
            cols.update(range(16))
        if idx in {2, 3, 12, 13}:
            cols.update({0, 1, 2, 13, 14, 15})
        if idx in {5, 10}:
            cols.update({0, 1, 2, 3, 12, 13, 14, 15})
        rows.append(row_from_cols(cols))
    return assert_mask(rows)


def make_row(name: str, mask: list[str] | None, notes: str, *, pattern: str = "custom", fill_probability: float = 0.5, seed: int = 0) -> dict[str, str]:
    return {
        "name": name,
        "matrix_n": "16",
        "pixel_mm": "0.35",
        "cell_pitch_mm": "0.35",
        "pixel_overfill_ratio": "0.10",
        "gap_mm": "0.00",
        "feed_w_mm": "0.38",
        "feed_len_mm": "2.00",
        "coupling_overlap_mm": "0.45",
        "pattern": pattern,
        "custom_mask_rows": ";".join(mask or []),
        "seed": str(seed),
        "fill_probability": f"{fill_probability:.2f}",
        "mirror_x": "true",
        "force_edge_coupling": "true",
        "connect_adjacent_pixels": "true",
        "substrate": "BFP_lib:substrate4",
        "er": "4.6",
        "h_mm": "0.210",
        "copper_mm": "0.035",
        "min_fab_gap_mm": "0.1016",
        "min_fab_feature_mm": "0.1016",
        "metal_layer": "cond",
        "via_layer": "pcvia1",
        "boundary_layer": "EM_BOUNDARY",
        "notes": notes,
    }


def build_rows() -> list[dict[str, str]]:
    return [
        make_row(
            "pixel_qr16_fr4_210um_r2a_edge_stubs",
            edge_stubs(),
            "Edge-loaded through path with side stubs; tests edge-coupled stopband formation.",
        ),
        make_row(
            "pixel_qr16_fr4_210um_r2a_qr_sparse_s1",
            None,
            "Generated qr_seed with lower fill probability; tests whether lower metal density creates stronger selectivity.",
            pattern="qr_seed",
            fill_probability=0.42,
            seed=1,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write pixel QR R2 architecture candidate plan.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("projects") / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r2_arch_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(build_rows())
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
