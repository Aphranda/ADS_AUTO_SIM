#!/usr/bin/env python3
"""Create R6 via position/diameter tuning candidates for the pixel QR BPF."""

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
    ("r4_02", "pixel_qr16_fr4_210um_r4_02_toggle02_03_add04_02_keep_a02", "best R5 mid-inner via base"),
    ("r4_03", "pixel_qr16_fr4_210um_r4_03_toggle02_03_add04_02_keep_a03", "balanced R4 passband base"),
]

ROW = 8
COLUMNS = [2, 3, 4, 5]
DIAMETERS_MM = [0.14, 0.18, 0.22]


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
        raise ValueError("R6 generator currently expects a 16x16 binary mask")
    return [[int(ch) for ch in row] for row in clean_rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def mirror_pair(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], tuple[int, int]]:
    other = n - 1 - col
    return (row, min(col, other)), (row, max(col, other))


def via_mask_for(metal_mask: list[list[int]], row: int, col: int) -> list[list[int]]:
    n = len(metal_mask)
    via_mask = [[0 for _ in range(n)] for _ in range(n)]
    for via_row, via_col in mirror_pair(row, col, n=n):
        if not metal_mask[via_row][via_col]:
            raise ValueError(f"cannot place R6 via on empty metal pixel r{via_row} c{via_col}")
        via_mask[via_row][via_col] = 1
    return via_mask


def pad_diameter(diameter: float) -> float:
    return max(0.26, diameter + 0.12)


def make_row(
    template_params: dict[str, object],
    name: str,
    metal_rows: list[str],
    via_rows: list[str],
    notes: str,
    seed: int,
    via_diameter_mm: float,
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
        "via_pad_diameter_mm": f"{pad_diameter(via_diameter_mm):.6g}",
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


def build_rows(*, r4_layouts_dir: Path, max_candidates: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    idx = 0
    for base_label, base_name, base_note in BASES:
        base_params = read_json(params_path(r4_layouts_dir, base_name))
        metal_mask = mask_from_params(base_params)
        metal_rows = mask_rows(metal_mask)
        for col in COLUMNS:
            for diameter in DIAMETERS_MM:
                via_mask = via_mask_for(metal_mask, ROW, col)
                via_rows = mask_rows(via_mask)
                idx += 1
                diameter_label = str(diameter).replace(".", "p")
                name = f"pixel_qr16_fr4_210um_r6_{idx:02d}_{base_label}_via_r{ROW:02d}c{col:02d}_d{diameter_label}"
                notes = (
                    "R6 row8 via-pair tune; "
                    f"base={base_name} ({base_note}); via_pair=r{ROW:02d}c{col:02d}/r{ROW:02d}c{15-col:02d}; "
                    f"via_diameter_mm={diameter:.3g}; via_pad_diameter_mm={pad_diameter(diameter):.3g}. "
                    "Tune 5 GHz notch strength against 6 GHz passband collapse."
                )
                rows.append(make_row(base_params, name, metal_rows, via_rows, notes, 6600 + idx, diameter))
                if len(rows) >= max_candidates:
                    return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R6 via position/diameter tuning candidate plan.")
    parser.add_argument(
        "--r4-layouts-dir",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10",
    )
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r6_via_tune_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(r4_layouts_dir=args.r4_layouts_dir, max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R6 via-tune candidates: {args.out}")


if __name__ == "__main__":
    main()
