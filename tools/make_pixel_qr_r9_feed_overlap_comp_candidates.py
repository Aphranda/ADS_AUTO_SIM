#!/usr/bin/env python3
"""Create R9 feed-overlap compensation candidates for the pixel QR BPF.

R9 keeps the best R8 metal/via topology fixed and scans only external
coupling parameters. This adds a new degree of freedom after the lower
shoulder/via-diameter mechanism reached a local plateau.
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

BASE_NAME = "pixel_qr16_fr4_210um_r8_11_d0p20_add_r09c04"
FEED_WIDTHS_MM = [0.36, 0.38, 0.40]
COUPLING_OVERLAPS_MM = [0.40, 0.43, 0.45, 0.47, 0.50]
BASE_FEED_W_MM = 0.38
BASE_COUPLING_OVERLAP_MM = 0.45


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fmt_mm(value: float) -> str:
    return f"{value:.2f}".replace(".", "p")


def rows_from_params(params: dict[str, object], key: str) -> list[str]:
    rows = params.get(key)
    if not rows:
        rows = params["parameters"][key]  # type: ignore[index]
    out = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(out) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in out):
        raise ValueError(f"R9 generator expects 16x16 binary {key}")
    return out


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    feed_w_mm: float,
    overlap_mm: float,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    metal_rows = rows_from_params(template_params, "mask_rows")
    via_rows = rows_from_params(template_params, "via_mask_rows")
    via_diameter_mm = float(params["via_diameter_mm"])  # type: ignore[index]
    via_pad_diameter_mm = float(params["via_pad_diameter_mm"])  # type: ignore[index]
    name = (
        f"pixel_qr16_fr4_210um_r9_{idx:02d}_"
        f"fw{fmt_mm(feed_w_mm)}_ol{fmt_mm(overlap_mm)}"
    )
    notes = (
        "R9 feed-overlap compensation; base="
        f"{BASE_NAME}; fixed d0.20 row8 c04/c11 via pair and r09c04 lower shoulder. "
        f"feed_w={feed_w_mm:.2f} mm; coupling_overlap={overlap_mm:.2f} mm. "
        "Objective: recover the 6 GHz passband edge and inspect 5 GHz notch stability "
        "without adding more saturated lower-shoulder pixels."
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
        "via_mask_rows": ";".join(via_rows),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_pad_diameter_mm:.6g}",
        "seed": str(9900 + idx),
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
    rows: list[dict[str, str]] = []
    idx = 0
    for feed_w_mm in FEED_WIDTHS_MM:
        for overlap_mm in COUPLING_OVERLAPS_MM:
            if abs(feed_w_mm - BASE_FEED_W_MM) < 1e-9 and abs(overlap_mm - BASE_COUPLING_OVERLAP_MM) < 1e-9:
                continue
            idx += 1
            rows.append(make_row(base_params, idx=idx, feed_w_mm=feed_w_mm, overlap_mm=overlap_mm))
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R9 feed-overlap compensation candidate plan.")
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
    parser.add_argument("--max-candidates", type=int, default=14)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r9_feed_overlap_comp_1to10.csv",
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
    print(f"Wrote {len(rows)} R9 feed-overlap compensation candidates: {args.out}")


if __name__ == "__main__":
    main()
