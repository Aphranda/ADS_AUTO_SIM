#!/usr/bin/env python3
"""Create R17 local continuous tuning candidates for the pixel QR BPF.

R16 found the best measured local point at r16_05. R17 keeps that exact
16x16 metal/via topology and scans a finer continuous neighborhood:
via diameter, feed width, and coupling overlap. This round is intended to
add calibration samples for the surrogate geometry features while preserving
the 5 GHz stopband mechanism.
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

GEOM_VARIANTS = [
    ("d0p222_fw0p35_ol0p51", 0.222, 0.35, 0.51, "lower via/feed/overlap corner"),
    ("d0p222_fw0p35_ol0p53", 0.222, 0.35, 0.53, "lower via/feed at R16 best overlap"),
    ("d0p222_fw0p36_ol0p52", 0.222, 0.36, 0.52, "lower via with centered feed and slightly reduced overlap"),
    ("d0p222_fw0p36_ol0p55", 0.222, 0.36, 0.55, "lower via with higher overlap recovery"),
    ("d0p222_fw0p37_ol0p53", 0.222, 0.37, 0.53, "lower via with wider feed"),
    ("d0p225_fw0p35_ol0p51", 0.225, 0.35, 0.51, "R16 best via with reduced feed and overlap"),
    ("d0p225_fw0p35_ol0p53", 0.225, 0.35, 0.53, "R16 best via/overlap with reduced feed"),
    ("d0p225_fw0p35_ol0p55", 0.225, 0.35, 0.55, "R16 best via with low feed and high overlap"),
    ("d0p225_fw0p36_ol0p51", 0.225, 0.36, 0.51, "R16 best via/feed with reduced overlap"),
    ("d0p225_fw0p36_ol0p53", 0.225, 0.36, 0.53, "R16 measured best point repeat"),
    ("d0p225_fw0p36_ol0p55", 0.225, 0.36, 0.55, "R16 best via/feed with stronger overlap"),
    ("d0p225_fw0p37_ol0p51", 0.225, 0.37, 0.51, "wider feed with lower overlap"),
    ("d0p225_fw0p37_ol0p53", 0.225, 0.37, 0.53, "wider feed at R16 best overlap"),
    ("d0p225_fw0p37_ol0p55", 0.225, 0.37, 0.55, "higher feed and overlap corner"),
    ("d0p228_fw0p35_ol0p53", 0.228, 0.35, 0.53, "higher via with reduced feed"),
    ("d0p228_fw0p36_ol0p51", 0.228, 0.36, 0.51, "higher via with reduced overlap"),
    ("d0p228_fw0p36_ol0p53", 0.228, 0.36, 0.53, "higher via at R16 best feed/overlap"),
    ("d0p228_fw0p36_ol0p55", 0.228, 0.36, 0.55, "higher via with stronger overlap"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows_from_params(template_params: dict[str, object], key: str) -> list[str]:
    rows = template_params.get(key)
    if not rows:
        rows = template_params["parameters"][key]  # type: ignore[index]
    out = [str(row) for row in rows]  # type: ignore[union-attr]
    if len(out) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in out):
        raise ValueError(f"R17 generator expects 16x16 binary {key}")
    return out


def row_from_params(
    template_params: dict[str, object],
    *,
    idx: int,
    geom_label: str,
    via_diameter_mm: float,
    feed_w_mm: float,
    coupling_overlap_mm: float,
    geom_note: str,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r17_{idx:02d}_r16best_{geom_label}"
    notes = (
        "R17 local continuous tune around measured R16 best; "
        f"base={BASE_NAME}; geom={geom_label}; {geom_note}. "
        "Metal/via topology is fixed to isolate continuous geometry response. "
        "S21 remains the primary objective; S11/S22 remain low-weight auxiliary training targets."
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
        "seed": str(17000 + idx),
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
    rows: list[dict[str, str]] = []
    for idx, (geom_label, via_diameter_mm, feed_w_mm, coupling_overlap_mm, geom_note) in enumerate(
        GEOM_VARIANTS,
        start=1,
    ):
        rows.append(
            row_from_params(
                base_params,
                idx=idx,
                geom_label=geom_label,
                via_diameter_mm=via_diameter_mm,
                feed_w_mm=feed_w_mm,
                coupling_overlap_mm=coupling_overlap_mm,
                geom_note=geom_note,
            )
        )
        if len(rows) >= max_candidates:
            break
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R17 local continuous tuning candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=18)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r17_local_continuous_tune_1to10.csv",
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
    print(f"Wrote {len(rows)} R17 local continuous tuning candidates: {args.out}")


if __name__ == "__main__":
    main()
