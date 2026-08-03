#!/usr/bin/env python3
"""Create R11 ultra-weak via plus feed-recovery candidates for the pixel QR BPF."""

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
WEAK_VIA_DIAMETERS_MM = [0.105, 0.110]
FEED_VARIANTS = [
    ("base", 0.38, 0.45, "R8 best-balanced external coupling"),
    ("fw0p40_ol0p43", 0.40, 0.43, "R9 passband-edge recovery coupling"),
]
SECOND_VIA_VARIANTS = [
    ("r10c05", (10, 5), "lower inner branch; least harmful among R10 real tests"),
    ("r09c04", (9, 4), "direct lower shoulder; deepest 5 GHz among R10 real tests"),
    ("r09c03", (9, 3), "outer lower shoulder branch; untested R10 neighbor"),
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
        raise ValueError(f"R11 generator expects 16x16 binary {key}")
    return out


def mask_to_int(rows: list[str]) -> list[list[int]]:
    return [[int(ch) for ch in row] for row in rows]


def mirror_group(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def fmt_mm(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".").replace(".", "p")


def diameter_rows(values: list[list[float]]) -> list[str]:
    return [",".join(f"{value:.6g}" for value in row) for row in values]


def via_mask_rows(values: list[list[float]]) -> list[str]:
    return ["".join("1" if value > 0.0 else "0" for value in row) for row in values]


def build_via_diameter_map(
    metal_mask: list[list[int]],
    base_via_mask: list[list[int]],
    *,
    second_anchor: tuple[int, int],
    weak_diameter_mm: float,
) -> list[list[float]]:
    n = len(metal_mask)
    out = [[0.0 for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(n):
            if base_via_mask[row][col]:
                out[row][col] = MAIN_VIA_DIAMETER_MM
    for row, col in mirror_group(*second_anchor, n=n):
        if not metal_mask[row][col]:
            raise ValueError(f"second weak via target r{row} c{col} is not on metal")
        out[row][col] = weak_diameter_mm
    return out


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    feed_label: str,
    feed_w_mm: float,
    overlap_mm: float,
    feed_note: str,
    variant_label: str,
    variant_note: str,
    metal_rows: list[str],
    via_diameters: list[list[float]],
    weak_diameter_mm: float,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = (
        f"pixel_qr16_fr4_210um_r11_{idx:02d}_{feed_label}_"
        f"{variant_label}_d{fmt_mm(weak_diameter_mm)}"
    )
    notes = (
        "R11 ultra-weak via/feed-recovery probe; base="
        f"{BASE_NAME}; main row8 c04/c11 via fixed at {MAIN_VIA_DIAMETER_MM:.2f} mm; "
        f"second mirrored via {variant_label} at {weak_diameter_mm:.3f} mm; "
        f"feed_w={feed_w_mm:.2f} mm, coupling_overlap={overlap_mm:.2f} mm. "
        f"{variant_note}; {feed_note}. Objective: keep the R10 5 GHz notch gain but recover 6 GHz above -5.5 dB."
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
        "coupling_overlap_mm": f"{overlap_mm:.6g}",
        "pattern": "custom",
        "custom_mask_rows": ";".join(metal_rows),
        "via_mask_rows": ";".join(via_mask_rows(via_diameters)),
        "via_diameter_rows": ";".join(diameter_rows(via_diameters)),
        "via_diameter_mm": f"{MAIN_VIA_DIAMETER_MM:.6g}",
        "via_pad_diameter_mm": f"{MAIN_VIA_DIAMETER_MM + 0.12:.6g}",
        "seed": str(11000 + idx),
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
    for feed_label, feed_w_mm, overlap_mm, feed_note in FEED_VARIANTS:
        for variant_label, anchor, variant_note in SECOND_VIA_VARIANTS:
            for weak_diameter_mm in WEAK_VIA_DIAMETERS_MM:
                via_diameters = build_via_diameter_map(
                    metal_mask,
                    base_via_mask,
                    second_anchor=anchor,
                    weak_diameter_mm=weak_diameter_mm,
                )
                idx += 1
                rows.append(
                    make_row(
                        base_params,
                        idx=idx,
                        feed_label=feed_label,
                        feed_w_mm=feed_w_mm,
                        overlap_mm=overlap_mm,
                        feed_note=feed_note,
                        variant_label=variant_label,
                        variant_note=variant_note,
                        metal_rows=metal_rows,
                        via_diameters=via_diameters,
                        weak_diameter_mm=weak_diameter_mm,
                    )
                )
                if len(rows) >= max_candidates:
                    return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R11 ultra-weak via/feed-recovery candidate plan.")
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
        / "pixel_qr_bpf_fr4_210um_r11_ultra_weak_via_feed_recovery_1to10.csv",
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
    print(f"Wrote {len(rows)} R11 ultra-weak via/feed-recovery candidates: {args.out}")


if __name__ == "__main__":
    main()
