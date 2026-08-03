#!/usr/bin/env python3
"""Create R7 via-aware local metal trim candidates for the pixel QR BPF.

R7 keeps the useful R6 grounded-via pair fixed at row8 col4/col11 and only
adds/removes a few mirrored metal pixel groups around that shorted-stub region.
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
    ("d0p18", "pixel_qr16_fr4_210um_r6_08_r4_02_via_r08c04_d0p18", "best balanced 5G notch/passband"),
    ("d0p22", "pixel_qr16_fr4_210um_r6_09_r4_02_via_r08c04_d0p22", "stronger 5G notch with 6G cost"),
]

OPERATIONS = [
    ("add_r07c04", "add", [(7, 4)], "add metal above the via pair to recover 6G coupling"),
    ("add_r07c03", "add", [(7, 3)], "add upper outer shoulder near the shorted stub"),
    ("add_r07c05", "add", [(7, 5)], "add upper inner shoulder near the shorted stub"),
    ("add_r09c04", "add", [(9, 4)], "add metal below the via pair to tune lower-side current return"),
    ("add_r09c05", "add", [(9, 5)], "add lower inner shoulder near the shorted stub"),
    ("remove_r08c03", "remove", [(8, 3)], "open the outer neighbor next to the via pixel"),
    ("remove_r08c05", "remove", [(8, 5)], "open the inner neighbor next to the via pixel"),
    ("remove_r08c02", "remove", [(8, 2)], "shorten the side row before the via pair"),
    ("remove_r08c06", "remove", [(8, 6)], "thin the center-side bridge after the via pair"),
    (
        "add_r07c04_remove_r08c03",
        "mixed",
        [(7, 4), (8, 3)],
        "recover 6G above the via while opening the outer row8 neighbor",
    ),
    (
        "add_r09c04_remove_r08c05",
        "mixed",
        [(9, 4), (8, 5)],
        "recover lower-side coupling while opening the inner row8 neighbor",
    ),
    (
        "remove_r08c03_r08c05",
        "remove",
        [(8, 3), (8, 5)],
        "symmetrically thin both row8 neighbors around the via pixel",
    ),
]

LOCKED_PIXELS = {
    (7, 0),
    (7, 15),
    (8, 0),
    (8, 15),
    (8, 4),
    (8, 11),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mask_from_params(params: dict[str, object], key: str) -> list[list[int]]:
    rows = params.get(key)
    if not rows:
        rows = params["parameters"][key]  # type: ignore[index]
    clean_rows = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(clean_rows) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in clean_rows):
        raise ValueError(f"R7 generator currently expects a 16x16 binary {key}")
    return [[int(ch) for ch in row] for row in clean_rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def copy_mask(mask: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in mask]


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def apply_operation(mask: list[list[int]], mode: str, anchors: list[tuple[int, int]]) -> None:
    for row, col in anchors:
        for pixel in mirror_group(row, col, n=len(mask)):
            if pixel in LOCKED_PIXELS:
                continue
            r, c = pixel
            if mode == "add":
                mask[r][c] = 1
            elif mode == "remove":
                mask[r][c] = 0
            elif mode == "mixed":
                if (row, col) == (7, 4) or (row, col) == (9, 4):
                    mask[r][c] = 1
                else:
                    mask[r][c] = 0
            else:
                raise ValueError(f"unknown R7 operation mode: {mode}")
    for row, col in LOCKED_PIXELS:
        mask[row][col] = 1


def make_row(
    template_params: dict[str, object],
    name: str,
    metal_rows: list[str],
    via_rows: list[str],
    notes: str,
    seed: int,
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
        "via_diameter_mm": f"{float(params['via_diameter_mm']):.6g}",  # type: ignore[index]
        "via_pad_diameter_mm": f"{float(params['via_pad_diameter_mm']):.6g}",  # type: ignore[index]
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


def build_rows(*, r6_layouts_dir: Path, max_candidates: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    idx = 0
    for base_label, base_name, base_note in BASES:
        base_params = read_json(params_path(r6_layouts_dir, base_name))
        base_metal = mask_from_params(base_params, "mask_rows")
        via_rows = mask_rows(mask_from_params(base_params, "via_mask_rows"))
        for op_label, mode, anchors, op_note in OPERATIONS:
            out = copy_mask(base_metal)
            apply_operation(out, mode, anchors)
            metal_rows = mask_rows(out)
            key = f"{base_label}|{';'.join(metal_rows)}|{';'.join(via_rows)}"
            if key in seen:
                continue
            seen.add(key)
            idx += 1
            name = f"pixel_qr16_fr4_210um_r7_{idx:02d}_{base_label}_{op_label}"
            notes = (
                "R7 local metal trim around fixed row8 c04/c11 grounded-via pair; "
                f"base={base_name} ({base_note}); op={op_label}; {op_note}. "
                "Objective: keep the 5 GHz notch while recovering 6-8 GHz passband edge loss."
            )
            rows.append(make_row(base_params, name, metal_rows, via_rows, notes, 7700 + idx))
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R7 via-metal-trim candidate plan.")
    parser.add_argument(
        "--r6-layouts-dir",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r6_via_tune_1to10",
    )
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r7_via_metal_trim_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(r6_layouts_dir=args.r6_layouts_dir, max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R7 via-metal-trim candidates: {args.out}")


if __name__ == "__main__":
    main()
