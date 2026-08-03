#!/usr/bin/env python3
"""Create R13 remote weak-shorted-pad candidates for the pixel QR BPF.

R10/R11 showed that a second via near the lower shoulder deepens the 5 GHz
notch but over-couples the 6 GHz passband edge. R12 showed that metal-only
remote perturbations are too weak. R13 tests the middle ground: add a very
small grounded pad farther from the main row8 via pair, so coupling is mostly
capacitive and should be weaker than the R10/R11 r10c05 second via.
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

MAIN_VIA_DIAMETER_MM = 0.20
REMOTE_VIA_DIAMETER_MM = 0.105

# Each operator adds or removes mirrored metal pixels, then places the weak
# via on a mirrored anchor. Anchors are deliberately farther from row8 than
# R10/R11's r10c05 second via.
OPERATORS = [
    (
        "pad_r11c05_via",
        [(11, 5, 1)],
        (11, 5),
        "single isolated shorted pad one row below r10c05",
    ),
    (
        "pad_r11c06_via",
        [(11, 6, 1)],
        (11, 6),
        "single isolated inner shorted pad near the center branch",
    ),
    (
        "pad_r12c05_via",
        [(12, 5, 1)],
        (12, 5),
        "far lower shorted pad, weaker than r11 probes",
    ),
    (
        "pad_r12c04_via",
        [(12, 4, 1)],
        (12, 4),
        "far lower outer shorted pad near the lower shoulder",
    ),
    (
        "stub_r11c05_r12c05_via_r12",
        [(11, 5, 1), (12, 5, 1)],
        (12, 5),
        "two-pixel vertical remote shorted stub with the via at the far end",
    ),
    (
        "stub_r12c04_r12c05_via_c05",
        [(12, 4, 1), (12, 5, 1)],
        (12, 5),
        "two-pixel lower capacitive pad with a weak via on the inner end",
    ),
    (
        "shift_r10c05_to_r11c05_via",
        [(10, 5, 0), (11, 5, 1)],
        (11, 5),
        "move the harmful R10 r10c05 shorted pad one row farther away",
    ),
    (
        "shift_r10c05_to_r12c05_via",
        [(10, 5, 0), (12, 5, 1)],
        (12, 5),
        "move the harmful R10 r10c05 shorted pad two rows farther away",
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
        raise ValueError(f"R13 generator expects 16x16 binary {key}")
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


def apply_metal_operator(mask: list[list[int]], ops: list[tuple[int, int, int]]) -> list[list[int]]:
    out = [row[:] for row in mask]
    for row, col, value in ops:
        for r, c in mirror_group(row, col, n=len(mask)):
            if (r, c) in LOCKED_ON:
                out[r][c] = 1
            else:
                out[r][c] = value
    for r, c in LOCKED_ON:
        out[r][c] = 1
    return out


def build_via_diameters(
    metal_mask: list[list[int]],
    base_via_rows: list[str],
    anchor: tuple[int, int],
) -> list[list[float]]:
    n = len(metal_mask)
    out = [[0.0 for _ in range(n)] for _ in range(n)]
    base_via = rows_to_mask(base_via_rows)
    for row in range(n):
        for col in range(n):
            if base_via[row][col]:
                out[row][col] = MAIN_VIA_DIAMETER_MM
    for row, col in mirror_group(*anchor, n=n):
        if not metal_mask[row][col]:
            raise ValueError(f"R13 weak via target r{row} c{col} is not on metal")
        out[row][col] = REMOTE_VIA_DIAMETER_MM
    return out


def diameter_rows(values: list[list[float]]) -> list[str]:
    return [",".join(f"{value:.6g}" for value in row) for row in values]


def via_mask_rows(values: list[list[float]]) -> list[str]:
    return ["".join("1" if value > 0.0 else "0" for value in row) for row in values]


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
    via_diameters: list[list[float]],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r13_{idx:02d}_{base_label}_{operator_label}"
    notes = (
        "R13 remote weak-shorted-pad notch probe; "
        f"base={base_name} ({base_note}); op={operator_label}; {operator_note}. "
        f"Main row8 c04/c11 via pair fixed at {MAIN_VIA_DIAMETER_MM:.3g} mm; "
        f"remote mirrored weak via/pad at {REMOTE_VIA_DIAMETER_MM:.3g} mm. "
        "Objective: find a 5 GHz notch operator weaker than R10/R11 second via but stronger than R12 metal-only perturbations, "
        "with S21@6G guarded above about -5.5 dB."
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
        "via_mask_rows": ";".join(via_mask_rows(via_diameters)),
        "via_diameter_rows": ";".join(diameter_rows(via_diameters)),
        "via_diameter_mm": f"{MAIN_VIA_DIAMETER_MM:.6g}",
        "via_pad_diameter_mm": f"{MAIN_VIA_DIAMETER_MM + 0.12:.6g}",
        "seed": str(13000 + idx),
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
        base_via_rows = rows_from_params(base_params, "via_mask_rows")
        for operator_label, ops, via_anchor, operator_note in OPERATORS:
            metal_mask = apply_metal_operator(base_metal, ops)
            via_diameters = build_via_diameters(metal_mask, base_via_rows, via_anchor)
            metal_rows = mask_to_rows(metal_mask)
            key = (
                f"{';'.join(metal_rows)}|{';'.join(diameter_rows(via_diameters))}|"
                f"{base_params['parameters']['feed_w_mm']}|{base_params['parameters']['coupling_overlap_mm']}"  # type: ignore[index]
            )
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
                    via_diameters=via_diameters,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R13 remote weak-shorted-pad candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=16)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r13_remote_shorted_pad_1to10.csv",
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
    print(f"Wrote {len(rows)} R13 remote weak-shorted-pad candidates: {args.out}")


if __name__ == "__main__":
    main()
