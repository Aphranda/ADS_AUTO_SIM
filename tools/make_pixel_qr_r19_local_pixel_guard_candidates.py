#!/usr/bin/env python3
"""Create R19 local pixel guard candidates for the pixel QR BPF.

R18 showed that global overfill is a real but saturated operator. R19 returns
to NN-visible local metal edits around the measured R16/R17 best topology. The
candidate pool uses small mirrored add/remove/shift edits near the lower
shoulder notch region, combined with two conservative continuous-geometry
anchors that the 7D surrogate can already represent.
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

BASE_NAME = "pixel_qr16_fr4_210um_r16_05_r8d22v_d0p225_fw0p36_ol0p53"

GEOM_ANCHORS = [
    ("center", 0.10, 0.225, 0.36, 0.53, "measured R16/R17 best geometry"),
    ("safe", 0.10, 0.222, 0.35, 0.51, "safer 6G guard corner from R17"),
    ("recover", 0.12, 0.222, 0.35, 0.51, "slightly larger overfill to recover 6G after local metal edit"),
]

OPERATORS = [
    ("add_r10c05", [(10, 5, 1)], "add one lower inner capacitive pixel"),
    ("add_r10c06", [(10, 6, 1)], "add one lower center-side capacitive pixel"),
    ("add_r11c04", [(11, 4, 1)], "add one remote outer lower pixel"),
    ("add_r11c05", [(11, 5, 1)], "add one remote lower shoulder pixel"),
    ("add_r11c06", [(11, 6, 1)], "add one remote lower center-side pixel"),
    ("add_r12c04", [(12, 4, 1)], "add far lower outer weak-loading pixel"),
    ("add_r12c05", [(12, 5, 1)], "add far lower weak-loading pixel"),
    ("pad_r11c04_r11c05", [(11, 4, 1), (11, 5, 1)], "add compact remote lower pad"),
    ("pad_r11c05_r11c06", [(11, 5, 1), (11, 6, 1)], "add compact inner remote lower pad"),
    ("stub_r10c05_r11c05", [(10, 5, 1), (11, 5, 1)], "add short vertical open metal stub"),
    ("stub_r11c05_r12c05", [(11, 5, 1), (12, 5, 1)], "add remote weak vertical open metal stub"),
    ("slot_rm_r10c05", [(10, 5, 0)], "remove lower inner pixel to recover 6G edge"),
    ("slot_rm_r09c05", [(9, 5, 0)], "trim inner lower shoulder to weaken over-coupled notch"),
    ("shift_r10c05_to_r11c05", [(10, 5, 0), (11, 5, 1)], "move lower inner metal one row farther from the main path"),
    ("shift_r10c04_to_r11c04", [(10, 4, 0), (11, 4, 1)], "move outer lower extension one row farther from the main path"),
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
        raise ValueError(f"R19 generator expects 16x16 binary {key}")
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
            out[r][c] = 1 if (r, c) in LOCKED_ON else value
    for r, c in LOCKED_ON:
        out[r][c] = 1
    return mask_to_rows(out)


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    geom_label: str,
    overfill_ratio: float,
    via_diameter_mm: float,
    feed_w_mm: float,
    coupling_overlap_mm: float,
    geom_note: str,
    operator_label: str,
    operator_note: str,
    metal_rows: list[str],
    via_rows: list[str],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r19_{idx:02d}_{geom_label}_{operator_label}"
    notes = (
        "R19 local pixel guard mutation around measured R16/R17 best; "
        f"base={BASE_NAME}; geom={geom_label}; {geom_note}; op={operator_label}; {operator_note}. "
        "Operator is visible to the current CNN via metal/via image channels and 7D geometry features. "
        "S21 is primary feedback; S11/S22 remain low-weight auxiliary training targets."
    )
    return {
        "name": name,
        "matrix_n": str(params["matrix_n"]),  # type: ignore[index]
        "pixel_mm": f"{float(params['pixel_mm']):.6g}",  # type: ignore[index]
        "cell_pitch_mm": f"{float(params['cell_pitch_mm']):.6g}",  # type: ignore[index]
        "pixel_overfill_ratio": f"{overfill_ratio:.6g}",
        "gap_mm": "0",
        "feed_w_mm": f"{feed_w_mm:.6g}",
        "feed_len_mm": f"{float(params['feed_len_mm']):.6g}",  # type: ignore[index]
        "coupling_overlap_mm": f"{coupling_overlap_mm:.6g}",
        "pattern": "custom",
        "custom_mask_rows": ";".join(metal_rows),
        "via_mask_rows": ";".join(via_rows),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_diameter_mm + 0.12:.6g}",
        "seed": str(19000 + idx),
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
    params_path = (
        root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "layouts"
        / "pixel_qr_bpf_fr4_210um_r16_d0p22_continuous_tune_1to10"
        / f"{BASE_NAME}_params.json"
    )
    base_params = read_json(params_path)
    base_metal = rows_to_mask(rows_from_params(base_params, "mask_rows"))
    via_rows = rows_from_params(base_params, "via_mask_rows")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    idx = 0
    for geom_label, overfill_ratio, via_diameter_mm, feed_w_mm, coupling_overlap_mm, geom_note in GEOM_ANCHORS:
        for operator_label, ops, operator_note in OPERATORS:
            metal_rows = apply_operator(base_metal, ops)
            key = (
                f"{';'.join(metal_rows)}|{';'.join(via_rows)}|"
                f"{overfill_ratio:.6g}|{via_diameter_mm:.6g}|{feed_w_mm:.6g}|{coupling_overlap_mm:.6g}"
            )
            if key in seen:
                continue
            seen.add(key)
            idx += 1
            rows.append(
                make_row(
                    base_params,
                    idx=idx,
                    geom_label=geom_label,
                    overfill_ratio=overfill_ratio,
                    via_diameter_mm=via_diameter_mm,
                    feed_w_mm=feed_w_mm,
                    coupling_overlap_mm=coupling_overlap_mm,
                    geom_note=geom_note,
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
    parser = argparse.ArgumentParser(description="Write R19 local pixel guard candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=45)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r19_local_pixel_guard_1to10.csv",
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
    print(f"Wrote {len(rows)} R19 local pixel guard candidates: {args.out}")


if __name__ == "__main__":
    main()
