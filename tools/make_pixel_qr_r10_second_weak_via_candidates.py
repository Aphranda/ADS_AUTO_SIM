#!/usr/bin/env python3
"""Create R10 second weak-via candidates for the pixel QR BPF.

R10 keeps the R8 best-balanced topology and the main row8 c04/c11 via pair at
0.20 mm, then adds a second weaker mirrored grounded-via pair on lower-side
existing metal pixels. The goal is to deepen the 5 GHz notch without pulling
the 6 GHz passband edge below the guard floor.
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
    "via_diameter_rows",
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

BASE_NAME = "pixel_qr16_fr4_210um_r8_11_d0p20_add_r09c04"
MAIN_VIA_DIAMETER_MM = 0.20
WEAK_VIA_DIAMETERS_MM = [0.12, 0.14, 0.16]

SECOND_VIA_VARIANTS = [
    ("r09c04", (9, 4), "direct lower shoulder under the main via pair"),
    ("r09c03", (9, 3), "outer lower shoulder branch beside the main via pair"),
    ("r10c05", (10, 5), "lower inner branch farther from the main via pair"),
    ("r10c07", (10, 7), "lower center branch as a weak independent shorted island"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows_from_params(params: dict[str, object], key: str) -> list[str]:
    rows = params.get(key)
    if not rows:
        rows = params["parameters"][key]  # type: ignore[index]
    out = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(out) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in out):
        raise ValueError(f"R10 generator expects 16x16 binary {key}")
    return out


def mask_to_int(rows: list[str]) -> list[list[int]]:
    return [[int(ch) for ch in row] for row in rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def diameter_rows(values: list[list[float]]) -> list[str]:
    return [",".join(f"{value:.6g}" for value in row) for row in values]


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def fmt_mm(value: float) -> str:
    return f"{value:.2f}".replace(".", "p")


def build_via_diameter_map(
    metal_mask: list[list[int]],
    base_via_mask: list[list[int]],
    *,
    second_anchor: tuple[int, int],
    weak_diameter_mm: float,
) -> list[list[float]]:
    n = len(metal_mask)
    via_diameters = [[0.0 for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(n):
            if base_via_mask[row][col]:
                via_diameters[row][col] = MAIN_VIA_DIAMETER_MM

    for row, col in mirror_group(*second_anchor, n=n):
        if not metal_mask[row][col]:
            raise ValueError(f"second weak via target r{row} c{col} is not on metal")
        via_diameters[row][col] = weak_diameter_mm
    return via_diameters


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    variant_label: str,
    variant_note: str,
    metal_rows: list[str],
    via_diameter_rows_out: list[str],
    weak_diameter_mm: float,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    via_mask = [
        ["1" if float(value) > 0.0 else "0" for value in row.split(",")]
        for row in via_diameter_rows_out
    ]
    name = f"pixel_qr16_fr4_210um_r10_{idx:02d}_{variant_label}_d{fmt_mm(weak_diameter_mm)}"
    notes = (
        "R10 second weak-via probe; base="
        f"{BASE_NAME}; main row8 c04/c11 via pair fixed at {MAIN_VIA_DIAMETER_MM:.2f} mm; "
        f"added mirrored weak via {variant_label} at {weak_diameter_mm:.2f} mm. "
        f"{variant_note}. Objective: improve the 5 GHz bandstop notch while guarding 6-8 GHz S21."
    )
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
        "via_mask_rows": ";".join("".join(row) for row in via_mask),
        "via_diameter_rows": ";".join(via_diameter_rows_out),
        "via_diameter_mm": f"{MAIN_VIA_DIAMETER_MM:.6g}",
        "via_pad_diameter_mm": f"{MAIN_VIA_DIAMETER_MM + 0.12:.6g}",
        "seed": str(10000 + idx),
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


def build_rows(*, base_params_path: Path, max_candidates: int) -> list[dict[str, str]]:
    base_params = read_json(base_params_path)
    metal_rows = rows_from_params(base_params, "mask_rows")
    metal_mask = mask_to_int(metal_rows)
    base_via_mask = mask_to_int(rows_from_params(base_params, "via_mask_rows"))

    rows: list[dict[str, str]] = []
    idx = 0
    for variant_label, second_anchor, variant_note in SECOND_VIA_VARIANTS:
        for weak_diameter_mm in WEAK_VIA_DIAMETERS_MM:
            via_diameters = build_via_diameter_map(
                metal_mask,
                base_via_mask,
                second_anchor=second_anchor,
                weak_diameter_mm=weak_diameter_mm,
            )
            idx += 1
            rows.append(
                make_row(
                    base_params,
                    idx=idx,
                    variant_label=variant_label,
                    variant_note=variant_note,
                    metal_rows=metal_rows,
                    via_diameter_rows_out=diameter_rows(via_diameters),
                    weak_diameter_mm=weak_diameter_mm,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R10 second weak-via candidate plan.")
    parser.add_argument(
        "--base-params",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "layouts"
        / "pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10"
        / f"{BASE_NAME}_params.json",
    )
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r10_second_weak_via_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(base_params_path=args.base_params, max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R10 second weak-via candidates: {args.out}")


if __name__ == "__main__":
    main()
