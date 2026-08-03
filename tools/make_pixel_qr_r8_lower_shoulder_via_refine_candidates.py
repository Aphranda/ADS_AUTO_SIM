#!/usr/bin/env python3
"""Create R8 lower-shoulder/via-refine candidates for the pixel QR BPF.

R8 keeps the R6/R7 row8 c04/c11 grounded-via pair and focuses on the only
R7 metal edits that remained useful: lower-side metal additions around rows
9-10. The round scans via diameter and a few mirrored lower shoulder shapes.
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

BASE_NAME = "pixel_qr16_fr4_210um_r6_08_r4_02_via_r08c04_d0p18"

VIA_DIAMETERS_MM = [0.16, 0.18, 0.20, 0.22]

LOWER_SHOULDER_VARIANTS = [
    ("add_r09c04", [(9, 4)], "single lower outer shoulder; R7 best-balanced mechanism"),
    ("add_r09c05", [(9, 5)], "single lower inner shoulder; R7 slightly deeper 5G variant"),
    ("add_r09c04_r09c05", [(9, 4), (9, 5)], "combined lower shoulder around the via pair"),
    ("add_r10c04", [(10, 4)], "move the lower shoulder one row farther from the via pair"),
    ("add_r09c04_r10c04", [(9, 4), (10, 4)], "extend the outer lower shoulder vertically"),
    ("add_r09c05_r10c05", [(9, 5), (10, 5)], "extend the inner lower shoulder vertically"),
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
        raise ValueError(f"R8 generator currently expects a 16x16 binary {key}")
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


def apply_additions(mask: list[list[int]], anchors: list[tuple[int, int]]) -> None:
    for row, col in anchors:
        for r, c in mirror_group(row, col, n=len(mask)):
            if (r, c) not in LOCKED_PIXELS:
                mask[r][c] = 1
    for row, col in LOCKED_PIXELS:
        mask[row][col] = 1


def fmt_mm(value: float) -> str:
    return f"{value:.2f}".replace(".", "p")


def make_row(
    template_params: dict[str, object],
    *,
    name: str,
    metal_rows: list[str],
    via_rows: list[str],
    via_diameter_mm: float,
    notes: str,
    seed: int,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    via_pad_diameter_mm = via_diameter_mm + 0.12
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


def build_rows(*, r6_layouts_dir: Path, max_candidates: int) -> list[dict[str, str]]:
    base_params = read_json(r6_layouts_dir / f"{BASE_NAME}_params.json")
    base_metal = mask_from_params(base_params, "mask_rows")
    via_rows = mask_rows(mask_from_params(base_params, "via_mask_rows"))

    rows: list[dict[str, str]] = []
    idx = 0
    seen: set[str] = set()
    for via_diameter_mm in VIA_DIAMETERS_MM:
        for variant_label, anchors, variant_note in LOWER_SHOULDER_VARIANTS:
            out = copy_mask(base_metal)
            apply_additions(out, anchors)
            metal_rows = mask_rows(out)
            key = f"{via_diameter_mm:.4f}|{';'.join(metal_rows)}|{';'.join(via_rows)}"
            if key in seen:
                continue
            seen.add(key)
            idx += 1
            diameter_label = f"d{fmt_mm(via_diameter_mm)}"
            name = f"pixel_qr16_fr4_210um_r8_{idx:02d}_{diameter_label}_{variant_label}"
            notes = (
                "R8 lower-shoulder via refinement; base="
                f"{BASE_NAME} (R6/R7 fixed row8 c04/c11 via pair); "
                f"via_diameter={via_diameter_mm:.2f} mm; op={variant_label}; {variant_note}. "
                "Objective: deepen the 5 GHz notch while keeping 6 GHz above the guarded passband floor."
            )
            rows.append(
                make_row(
                    base_params,
                    name=name,
                    metal_rows=metal_rows,
                    via_rows=via_rows,
                    via_diameter_mm=via_diameter_mm,
                    notes=notes,
                    seed=8800 + idx,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R8 lower-shoulder/via-refine candidate plan.")
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
        / "pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10.csv",
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
    print(f"Wrote {len(rows)} R8 lower-shoulder/via-refine candidates: {args.out}")


if __name__ == "__main__":
    main()
