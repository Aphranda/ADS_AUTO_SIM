#!/usr/bin/env python3
"""Create R16 continuous geometry tuning candidates for the pixel QR BPF.

R15 confirmed the best balanced family is still the d0.22 main row8 via pair
with lower-shoulder metal. R16 keeps the two most useful masks fixed and scans
continuous geometry variables that the surrogate already sees: via diameter,
feed width, and coupling overlap.
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
        "r8d22v",
        "pixel_qr16_fr4_210um_r15_05_r8d22v_keep_basefeed",
        "R8/R15 vertical lower shoulder; best 6-8G balance",
    ),
    (
        "r7d22a",
        "pixel_qr16_fr4_210um_r15_01_r7d22a_keep_basefeed",
        "R7/R15 single lower shoulder; slightly deeper 5G baseline",
    ),
]

GEOM_VARIANTS = [
    ("d0p210_fw0p36_ol0p50", 0.210, 0.36, 0.50, "weaker main via, R15 compensation feed"),
    ("d0p215_fw0p34_ol0p50", 0.215, 0.34, 0.50, "weaker feed plus slightly smaller via"),
    ("d0p220_fw0p36_ol0p50", 0.220, 0.36, 0.50, "R15 feed-compensation reference"),
    ("d0p225_fw0p36_ol0p50", 0.225, 0.36, 0.50, "slightly stronger main via"),
    ("d0p225_fw0p36_ol0p53", 0.225, 0.36, 0.53, "stronger via plus larger overlap recovery"),
    ("d0p225_fw0p38_ol0p47", 0.225, 0.38, 0.47, "wider feed with lower overlap"),
    ("d0p230_fw0p36_ol0p50", 0.230, 0.36, 0.50, "stronger notch via, same compensation feed"),
    ("d0p230_fw0p38_ol0p50", 0.230, 0.38, 0.50, "stronger via with wider feed recovery"),
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
        raise ValueError(f"R16 generator expects 16x16 binary {key}")
    return out


def row_from_base(
    template_params: dict[str, object],
    *,
    idx: int,
    base_label: str,
    base_name: str,
    base_note: str,
    geom_label: str,
    via_diameter_mm: float,
    feed_w_mm: float,
    coupling_overlap_mm: float,
    geom_note: str,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r16_{idx:02d}_{base_label}_{geom_label}"
    notes = (
        "R16 d0.22-family continuous geometry tune; "
        f"base={base_name} ({base_note}); geom={geom_label}; {geom_note}. "
        "Mask topology is fixed; only via diameter/feed width/coupling overlap change. "
        "S21 remains the ranking feedback; S11/S22 remain low-weight auxiliary training targets."
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
        "custom_mask_rows": ";".join(rows_from_params(template_params, "mask_rows")),
        "via_mask_rows": ";".join(rows_from_params(template_params, "via_mask_rows")),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_diameter_mm + 0.12:.6g}",
        "seed": str(16000 + idx),
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
    layout_dir = root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r15_d0p22_feed_path_1to10"
    rows: list[dict[str, str]] = []
    idx = 0
    for base_label, base_name, base_note in BASES:
        base_params = read_json(layout_dir / f"{base_name}_params.json")
        for geom_label, via_diameter_mm, feed_w_mm, coupling_overlap_mm, geom_note in GEOM_VARIANTS:
            idx += 1
            rows.append(
                row_from_base(
                    base_params,
                    idx=idx,
                    base_label=base_label,
                    base_name=base_name,
                    base_note=base_note,
                    geom_label=geom_label,
                    via_diameter_mm=via_diameter_mm,
                    feed_w_mm=feed_w_mm,
                    coupling_overlap_mm=coupling_overlap_mm,
                    geom_note=geom_note,
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R16 d0.22 continuous tuning candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=16)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r16_d0p22_continuous_tune_1to10.csv",
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
    print(f"Wrote {len(rows)} R16 d0.22 continuous tuning candidates: {args.out}")


if __name__ == "__main__":
    main()
