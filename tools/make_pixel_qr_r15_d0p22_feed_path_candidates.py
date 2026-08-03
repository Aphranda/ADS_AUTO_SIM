#!/usr/bin/env python3
"""Create R15 d0.22 feed/path compensation candidates for the pixel QR BPF.

R7/R8 showed that the 0.22 mm main row8 via pair plus lower-shoulder metal is
the best S21-balanced 5 GHz notch family found so far. R9 showed feed/overlap
compensation can move the 6 GHz edge, but it was only applied to the d0.20
base. R15 combines the stronger d0.22 notch bases with conservative feed
compensation and lower-shoulder path edits, without adding a second via.
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
        "r7d22a",
        "pixel_qr_bpf_fr4_210um_r7_via_metal_trim_1to10",
        "pixel_qr16_fr4_210um_r7_16_d0p22_add_r09c04",
        "R7 best d0.22 single lower shoulder",
    ),
    (
        "r8d22v",
        "pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10",
        "pixel_qr16_fr4_210um_r8_20_d0p22_add_r09c04_r10c04",
        "R8 vertical lower shoulder with strongest guarded 5G",
    ),
    (
        "r8d22p",
        "pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10",
        "pixel_qr16_fr4_210um_r8_18_d0p22_add_r09c04_r09c05",
        "R8 paired row9 lower shoulder with better 9G",
    ),
]

OPERATORS = [
    ("keep", [], "keep the proven d0.22 metal path"),
    ("add_r10c05", [(10, 5, 1)], "add lower inner pixel one row below the shoulder"),
    ("add_r09c05_r10c05", [(9, 5, 1), (10, 5, 1)], "add inner lower shoulder and vertical extension"),
    ("swap_r10c04_to_r10c05", [(10, 4, 0), (10, 5, 1)], "move far lower extension one column inward"),
]

FEED_VARIANTS = [
    ("basefeed", None, None, "keep base feed geometry"),
    ("fw0p36_ol0p50", 0.36, 0.50, "narrow feed and larger overlap, based on R9 deeper-5G compensation"),
]

LOCKED_ON = {
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


def rows_from_params(params: dict[str, object], key: str) -> list[str]:
    rows = params.get(key)
    if not rows:
        rows = params["parameters"][key]  # type: ignore[index]
    out = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(out) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in out):
        raise ValueError(f"R15 generator expects 16x16 binary {key}")
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
    feed_label: str,
    feed_note: str,
    feed_w_mm: float,
    coupling_overlap_mm: float,
    metal_rows: list[str],
    via_rows: list[str],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r15_{idx:02d}_{base_label}_{operator_label}_{feed_label}"
    notes = (
        "R15 d0.22 feed/path compensation; "
        f"base={base_name} ({base_note}); op={operator_label}; {operator_note}; feed={feed_label}; {feed_note}. "
        "No second via is added; S21 is the primary ranking feedback while S11/S22 remain low-weight auxiliary training targets."
    )
    return {
        "name": name,
        "matrix_n": str(params["matrix_n"]),  # type: ignore[index]
        "pixel_mm": f"{float(params['pixel_mm']):.6g}",  # type: ignore[index]
        "cell_pitch_mm": f"{float(params['cell_pitch_mm']):.6g}",  # type: ignore[index]
        "pixel_overfill_ratio": f"{float(params['pixel_overfill_ratio']):.6g}",  # type: ignore[index]
        "gap_mm": f"{float(params['gap_mm']):.6g}",  # type: ignore[index]
        "feed_w_mm": f"{feed_w_mm:.6g}",
        "feed_len_mm": f"{float(params['feed_len_mm']):.6g}",  # type: ignore[index]
        "coupling_overlap_mm": f"{coupling_overlap_mm:.6g}",
        "pattern": "custom",
        "custom_mask_rows": ";".join(metal_rows),
        "via_mask_rows": ";".join(via_rows),
        "via_diameter_mm": f"{float(params['via_diameter_mm']):.6g}",  # type: ignore[index]
        "via_pad_diameter_mm": f"{float(params['via_pad_diameter_mm']):.6g}",  # type: ignore[index]
        "seed": str(15000 + idx),
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
        params_path = root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / sweep_dir / f"{base_name}_params.json"
        base_params = read_json(params_path)
        base_metal = rows_to_mask(rows_from_params(base_params, "mask_rows"))
        via_rows = rows_from_params(base_params, "via_mask_rows")
        base_feed_w = float(base_params["parameters"]["feed_w_mm"])  # type: ignore[index]
        base_overlap = float(base_params["parameters"]["coupling_overlap_mm"])  # type: ignore[index]
        for operator_label, ops, operator_note in OPERATORS:
            metal_rows = apply_operator(base_metal, ops)
            for feed_label, feed_w_override, overlap_override, feed_note in FEED_VARIANTS:
                feed_w_mm = base_feed_w if feed_w_override is None else feed_w_override
                coupling_overlap_mm = base_overlap if overlap_override is None else overlap_override
                key = f"{';'.join(metal_rows)}|{';'.join(via_rows)}|{feed_w_mm:.6g}|{coupling_overlap_mm:.6g}"
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
                        feed_label=feed_label,
                        feed_note=feed_note,
                        feed_w_mm=feed_w_mm,
                        coupling_overlap_mm=coupling_overlap_mm,
                        metal_rows=metal_rows,
                        via_rows=via_rows,
                    )
                )
                if len(rows) >= max_candidates:
                    return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R15 d0.22 feed/path compensation candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r15_d0p22_feed_path_1to10.csv",
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
    print(f"Wrote {len(rows)} R15 d0.22 feed/path candidates: {args.out}")


if __name__ == "__main__":
    main()
