#!/usr/bin/env python3
"""Create R5 via-aware notch candidates for the pixel QR BPF.

R5 keeps the useful R4 metal masks and adds small mirrored ground-via sets.
The goal is to test whether shorted local stubs can deepen the 5 GHz notch
without collapsing the 6-8 GHz passband, which ordinary pixel add/remove did.
"""

from __future__ import annotations

import argparse
import csv
import json
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
    "via_mask_rows",
    "via_diameter_mm",
    "via_pad_diameter_mm",
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

BASES = [
    ("r4_03", "pixel_qr16_fr4_210um_r4_03_toggle02_03_add04_02_keep_a03", "balanced passband base"),
    ("r4_02", "pixel_qr16_fr4_210um_r4_02_toggle02_03_add04_02_keep_a02", "best high-side suppression base"),
    ("r4_06", "pixel_qr16_fr4_210um_r4_06_toggle02_03_add04_01_keep_a01", "stable 6-8 GHz base"),
    ("r4_01", "pixel_qr16_fr4_210um_r4_01_toggle02_03_add04_02_keep_a01", "near-r4_02 conservative base"),
]

VIA_SET_SPECS = [
    ("mid_edge", [(8, 2)], "one mirrored pair on the main center row near the side edge"),
    ("mid_inner", [(8, 4)], "one mirrored pair on the main center row inside the side edge"),
    ("center_bridge", [(7, 7)], "one mirrored pair on the center bridge close to the feed axis"),
    ("upper_side", [(4, 2)], "one mirrored pair on upper side-stub metal"),
    ("row6_side", [(6, 2)], "one mirrored pair on dense row-6 side metal"),
    ("row5_stub", [(5, 3)], "one mirrored pair on row-5 stub metal"),
    ("mid_edge_upper", [(8, 2), (4, 2)], "two mirrored pairs: center row plus upper side stub"),
    ("mid_inner_center", [(8, 4), (7, 7)], "two mirrored pairs: center row plus center bridge"),
    ("row6_mid_edge", [(6, 2), (8, 2)], "two mirrored pairs coupling dense side metal to center row"),
    ("upper_lower_stub", [(4, 2), (10, 3)], "two mirrored pairs spanning upper and lower side-stub metal"),
    ("center_upper", [(7, 7), (4, 5)], "two mirrored pairs tying bridge and upper inner stub"),
    ("three_mid_side", [(8, 2), (6, 2), (4, 2)], "three mirrored pairs along the side current-return path"),
]

LOCKED_PIXELS = {
    (7, 0),
    (7, 15),
    (8, 0),
    (8, 15),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mask_from_params(params: dict[str, object]) -> list[list[int]]:
    rows = params.get("mask_rows")
    if not rows:
        rows = params["parameters"]["custom_mask_rows"]  # type: ignore[index]
    clean_rows = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(clean_rows) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in clean_rows):
        raise ValueError("R5 generator currently expects a 16x16 binary mask")
    return [[int(ch) for ch in row] for row in clean_rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def expand_spec(points: list[tuple[int, int]], n: int = 16) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for row, col in points:
        for pixel in mirror_group(row, col, n=n):
            if pixel in seen:
                continue
            seen.add(pixel)
            out.append(pixel)
    return out


def via_mask_for(metal_mask: list[list[int]], points: list[tuple[int, int]]) -> list[list[int]] | None:
    n = len(metal_mask)
    via_mask = [[0 for _ in range(n)] for _ in range(n)]
    for row, col in points:
        if (row, col) in LOCKED_PIXELS:
            return None
        if row < 0 or row >= n or col < 0 or col >= n:
            return None
        if not metal_mask[row][col]:
            return None
        via_mask[row][col] = 1
    return via_mask


def make_row(
    template_params: dict[str, object],
    name: str,
    metal_rows: list[str],
    via_rows: list[str],
    notes: str,
    seed: int,
    via_diameter_mm: float,
    via_pad_diameter_mm: float,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
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
        "custom_mask_rows": ";".join(metal_rows),
        "via_mask_rows": ";".join(via_rows),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_pad_diameter_mm:.6g}",
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


def params_path(layouts_dir: Path, candidate: str) -> Path:
    return layouts_dir / f"{candidate}_params.json"


def build_rows(
    *,
    r4_layouts_dir: Path,
    max_candidates: int,
    via_diameter_mm: float,
    via_pad_diameter_mm: float,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    candidate_idx = 0

    for base_label, base_name, base_note in BASES:
        base_params = read_json(params_path(r4_layouts_dir, base_name))
        metal_mask = mask_from_params(base_params)
        metal_rows = mask_rows(metal_mask)
        for spec_label, anchor_points, spec_note in VIA_SET_SPECS:
            via_points = expand_spec(anchor_points, n=len(metal_mask))
            via_mask = via_mask_for(metal_mask, via_points)
            if via_mask is None:
                continue
            via_rows = mask_rows(via_mask)
            key = f"{';'.join(metal_rows)}|{';'.join(via_rows)}"
            if key in seen:
                continue
            seen.add(key)
            candidate_idx += 1
            name = f"pixel_qr16_fr4_210um_r5_{candidate_idx:02d}_{base_label}_via_{spec_label}"
            notes = (
                "R5 via-aware 5 GHz notch probe; "
                f"base={base_name} ({base_note}); via_set={spec_label}; "
                f"via_count={sum(sum(row) for row in via_mask)}; "
                f"via_diameter_mm={via_diameter_mm:.3g}; via_pad_diameter_mm={via_pad_diameter_mm:.3g}; "
                f"{spec_note}. Guard 6G/8G S21 before expanding this family."
            )
            rows.append(
                make_row(
                    base_params,
                    name,
                    metal_rows,
                    via_rows,
                    notes,
                    5500 + candidate_idx,
                    via_diameter_mm,
                    via_pad_diameter_mm,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R5 via-aware notch candidate plan.")
    parser.add_argument(
        "--r4-layouts-dir",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10",
    )
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument("--via-diameter-mm", type=float, default=0.18)
    parser.add_argument("--via-pad-diameter-mm", type=float, default=0.30)
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r5_via_notch_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(
        r4_layouts_dir=args.r4_layouts_dir,
        max_candidates=args.max_candidates,
        via_diameter_mm=args.via_diameter_mm,
        via_pad_diameter_mm=args.via_pad_diameter_mm,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R5 via-notch candidates: {args.out}")


if __name__ == "__main__":
    main()
