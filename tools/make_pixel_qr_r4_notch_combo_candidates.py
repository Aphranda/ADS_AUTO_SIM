#!/usr/bin/env python3
"""Create R4 local notch-combo candidates for the pixel QR BPF.

R4 is intentionally not another random add/remove/toggle sweep. It combines
validated 6-8 GHz passband bases with small local add-pixel groups observed in
R3 candidates that deepened the 5 GHz response.
"""

from __future__ import annotations

import argparse
import csv
import itertools
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

PASSBAND_BASES = [
    "pixel_qr16_fr4_210um_r3_toggle02_03",
    "pixel_qr16_fr4_210um_r3_remove02_03",
    "pixel_qr16_fr4_210um_r3_add02_02",
]

NOTCH_DONORS = [
    "pixel_qr16_fr4_210um_r3_add04_02",
    "pixel_qr16_fr4_210um_r3_add02_01",
    "pixel_qr16_fr4_210um_r3_add04_01",
    "pixel_qr16_fr4_210um_r3_add02_00",
]


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
        raise ValueError("R4 generator currently expects a 16x16 binary mask")
    return [[int(ch) for ch in row] for row in clean_rows]


def mask_rows(mask: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in mask]


def enforce_feed_coupling(mask: list[list[int]]) -> None:
    for row, col in LOCKED_PIXELS:
        mask[row][col] = 1


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def canonical_groups(n: int = 16) -> list[tuple[tuple[int, int], ...]]:
    groups: list[tuple[tuple[int, int], ...]] = []
    for row in range(n):
        for col in range((n + 1) // 2):
            group = mirror_group(row, col, n=n)
            if any(pixel in LOCKED_PIXELS for pixel in group):
                continue
            groups.append(group)
    return groups


def group_center(group: tuple[tuple[int, int], ...]) -> tuple[float, float]:
    return (
        sum(row for row, _ in group) / len(group),
        sum(col for _, col in group) / len(group),
    )


def group_priority(group: tuple[tuple[int, int], ...]) -> tuple[float, float, float]:
    row, col = group_center(group)
    center_row = min(abs(row - 7.0), abs(row - 8.0))
    edge_col = min(abs(col - 2.0), abs(col - 13.0))
    return (center_row, edge_col, row)


def addition_groups(reference: list[list[int]], donor: list[list[int]]) -> list[tuple[tuple[int, int], ...]]:
    groups: list[tuple[tuple[int, int], ...]] = []
    for group in canonical_groups(len(reference)):
        ref_values = [reference[row][col] for row, col in group]
        donor_values = [donor[row][col] for row, col in group]
        if any(ref == 0 and value == 1 for ref, value in zip(ref_values, donor_values, strict=False)):
            groups.append(group)
    groups.sort(key=group_priority)
    return groups


def r1_restore_groups(base: list[list[int]], r1: list[list[int]]) -> list[tuple[tuple[int, int], ...]]:
    groups: list[tuple[tuple[int, int], ...]] = []
    for group in canonical_groups(len(base)):
        if any(base[row][col] != r1[row][col] for row, col in group):
            groups.append(group)
    groups.sort(key=group_priority)
    return groups


def copy_mask(mask: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in mask]


def apply_add_groups(mask: list[list[int]], groups: list[tuple[tuple[int, int], ...]]) -> None:
    for group in groups:
        for row, col in group:
            mask[row][col] = 1


def apply_restore_groups(mask: list[list[int]], r1: list[list[int]], groups: list[tuple[tuple[int, int], ...]]) -> None:
    for group in groups:
        for row, col in group:
            mask[row][col] = r1[row][col]


def make_row(template_params: dict[str, object], name: str, rows: list[str], notes: str, seed: int) -> dict[str, str]:
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


def params_path(layouts_dir: Path, candidate: str) -> Path:
    return layouts_dir / f"{candidate}_params.json"


def build_rows(
    *,
    r1_params_path: Path,
    r3_layouts_dir: Path,
    max_candidates: int,
) -> list[dict[str, str]]:
    r1_params = read_json(r1_params_path)
    r1_mask = mask_from_params(r1_params)
    enforce_feed_coupling(r1_mask)

    base_params_by_name = {name: read_json(params_path(r3_layouts_dir, name)) for name in PASSBAND_BASES}
    donor_masks = {name: mask_from_params(read_json(params_path(r3_layouts_dir, name))) for name in NOTCH_DONORS}

    rows: list[dict[str, str]] = []
    seen_masks: set[str] = set()
    candidate_idx = 0

    for base_name in PASSBAND_BASES:
        base_params = base_params_by_name[base_name]
        base_mask = mask_from_params(base_params)
        restore_groups = r1_restore_groups(base_mask, r1_mask)
        restore_options: list[tuple[str, list[tuple[tuple[int, int], ...]]]] = [("keep", [])]
        if "remove02_03" in base_name and restore_groups:
            restore_options += [
                ("repair1", restore_groups[:1]),
                ("repair2", restore_groups[:2]),
            ]

        for donor_name in NOTCH_DONORS:
            donor_groups = addition_groups(r1_mask, donor_masks[donor_name])
            if not donor_groups:
                continue
            group_sets = [
                donor_groups[:1],
                donor_groups[:2],
                donor_groups[:3],
            ]
            for (restore_label, restore_set), add_set in itertools.product(restore_options, group_sets):
                out = copy_mask(base_mask)
                apply_restore_groups(out, r1_mask, restore_set)
                apply_add_groups(out, add_set)
                enforce_feed_coupling(out)
                rows_key = ";".join(mask_rows(out))
                if rows_key in seen_masks:
                    continue
                seen_masks.add(rows_key)
                candidate_idx += 1
                short_base = base_name.replace("pixel_qr16_fr4_210um_r3_", "")
                short_donor = donor_name.replace("pixel_qr16_fr4_210um_r3_", "")
                name = f"pixel_qr16_fr4_210um_r4_{candidate_idx:02d}_{short_base}_{short_donor}_{restore_label}_a{len(add_set):02d}"
                filled = sum(sum(row) for row in out)
                notes = (
                    "R4 local notch-combo candidate; "
                    f"passband_base={base_name}; notch_donor={donor_name}; "
                    f"restore_groups={len(restore_set)}; add_groups={len(add_set)}; "
                    f"filled_pixels={filled}/256. Use surrogate 6G/8G guard before ADS/RFPro."
                )
                rows.append(make_row(base_params, name, mask_rows(out), notes, 4400 + candidate_idx))
                if len(rows) >= max_candidates:
                    return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R4 local notch-combo candidate plan.")
    parser.add_argument(
        "--r1-params",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "layouts"
        / "pixel_qr_bpf_fr4_210um_r1"
        / "pixel_qr16_fr4_210um_seed0_p035_ov10_fw038_ol045_params.json",
    )
    parser.add_argument(
        "--r3-layouts-dir",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10",
    )
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "pixel_qr_bpf_fr4_210um" / "plans" / "pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(r1_params_path=args.r1_params, r3_layouts_dir=args.r3_layouts_dir, max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} R4 notch-combo candidates: {args.out}")


if __name__ == "__main__":
    main()
