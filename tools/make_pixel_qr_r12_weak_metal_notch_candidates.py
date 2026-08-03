#!/usr/bin/env python3
"""Create R12 weak metal-only notch perturbation candidates.

R12 keeps the useful R8/R9 main grounded-via pair fixed and avoids adding a
second via. The operator only shifts small mirrored lower-side metal groups to
probe weaker 5 GHz notch perturbations that may not drag the 6 GHz passband
edge down as strongly as R10/R11 second-via candidates.
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
    (
        "r8b",
        "pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10",
        "pixel_qr16_fr4_210um_r8_11_d0p20_add_r09c04",
        "R8 best-balanced base",
    ),
    (
        "r9h",
        "pixel_qr_bpf_fr4_210um_r9_feed_overlap_comp_1to10",
        "pixel_qr16_fr4_210um_r9_04_fw0p36_ol0p47",
        "R9 high-side stopband base",
    ),
]

OPERATORS = [
    ("add_r10c06", [(10, 6, 1)], "add one lower-inner capacitive bridge, away from the main via"),
    ("add_r11c05", [(11, 5, 1)], "add one remote lower shoulder pixel one row below the saturated R8 shoulder"),
    ("add_r11c06", [(11, 6, 1)], "add one weak inner lower capacitive pixel near the center branch"),
    ("add_r12c04", [(12, 4, 1)], "add a far lower outer pixel, weakly coupled to the row9 shoulder"),
    ("add_r12c05", [(12, 5, 1)], "add a far lower inner pixel, weak metal-only notch probe"),
    ("add_r11c05_r12c05", [(11, 5, 1), (12, 5, 1)], "short vertical remote lower stub without any added via"),
    ("add_r12c04_r12c05", [(12, 4, 1), (12, 5, 1)], "far lower capacitive pad pair, expected weak coupling"),
    ("rm_r10c05", [(10, 5, 0)], "remove one existing lower inner pixel to recover 6 GHz edge"),
    ("rm_r09c03", [(9, 3, 0)], "trim the outer lower shoulder feed-in pixel while keeping r09c04"),
    (
        "shift_r10c05_to_r11c05",
        [(10, 5, 0), (11, 5, 1)],
        "shift existing lower inner metal one row farther from the main path",
    ),
]

LOCKED_ON = {
    (7, 0),
    (7, 15),
    (8, 0),
    (8, 15),
    (8, 4),
    (8, 11),
    (9, 4),
    (9, 11),
}


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
        raise ValueError(f"R12 generator expects 16x16 binary {key}")
    return out


def rows_to_mask(rows: list[str]) -> list[list[int]]:
    return [[int(ch) for ch in row] for row in rows]


def mask_to_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def apply_operator(mask: list[list[int]], ops: list[tuple[int, int, int]]) -> list[str]:
    out = [row[:] for row in mask]
    for row, col, value in ops:
        for r, c in mirror_group(row, col, n=len(mask)):
            if (r, c) in LOCKED_ON:
                out[r][c] = 1
            else:
                out[r][c] = value
    for r, c in LOCKED_ON:
        out[r][c] = 1
    return mask_to_rows(out)


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    base_label: str,
    base_name: str,
    base_note: str,
    operator_label: str,
    operator_note: str,
    metal_rows: list[str],
    via_rows: list[str],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    via_diameter_mm = float(params["via_diameter_mm"])  # type: ignore[index]
    via_pad_diameter_mm = float(params["via_pad_diameter_mm"])  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r12_{idx:02d}_{base_label}_{operator_label}"
    notes = (
        "R12 weak metal-only notch perturbation; "
        f"base={base_name} ({base_note}); op={operator_label}; {operator_note}. "
        "Main row8 c04/c11 via pair and via diameter are unchanged; no second via is added. "
        "Objective: find a weaker 5 GHz notch model that preserves S21@6G above the guard."
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
        "via_mask_rows": ";".join(via_rows),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_pad_diameter_mm:.6g}",
        "seed": str(12000 + idx),
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


def build_rows(*, max_candidates: int) -> list[dict[str, str]]:
    root = repo_root()
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    idx = 0
    for base_label, sweep_dir, base_name, base_note in BASES:
        params_path = (
            root
            / "projects"
            / "pixel_qr_bpf_fr4_210um"
            / "layouts"
            / sweep_dir
            / f"{base_name}_params.json"
        )
        base_params = read_json(params_path)
        base_metal = rows_to_mask(rows_from_params(base_params, "mask_rows"))
        via_rows = rows_from_params(base_params, "via_mask_rows")
        for operator_label, ops, operator_note in OPERATORS:
            metal_rows = apply_operator(base_metal, ops)
            key = f"{';'.join(metal_rows)}|{';'.join(via_rows)}|{base_params['parameters']['feed_w_mm']}|{base_params['parameters']['coupling_overlap_mm']}"  # type: ignore[index]
            if key in seen:
                continue
            seen.add(key)
            idx += 1
            rows.append(
                make_row(
                    base_params,
                    idx=idx,
                    base_label=base_label,
                    base_name=base_name,
                    base_note=base_note,
                    operator_label=operator_label,
                    operator_note=operator_note,
                    metal_rows=metal_rows,
                    via_rows=via_rows,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R12 weak metal-only notch candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=20)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r12_weak_metal_notch_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R12 weak metal-only notch candidates: {args.out}")


if __name__ == "__main__":
    main()
