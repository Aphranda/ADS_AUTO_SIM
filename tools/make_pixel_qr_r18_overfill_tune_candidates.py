#!/usr/bin/env python3
"""Create R18 overfill tuning candidates for the pixel QR BPF.

R18 keeps the measured R16/R17 best topology and uses the newly exposed
surrogate geometry feature `pixel_overfill_ratio`. For this connected grid,
gap_mm is not a physical degree of freedom while cell_pitch_mm is positive, so
gap is kept fixed at zero.
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
    ("of0p04_d0p222_fw0p35_ol0p51", 0.04, 0.222, 0.35, 0.51, "least overfill, safest low-via corner"),
    ("of0p04_d0p225_fw0p36_ol0p53", 0.04, 0.225, 0.36, 0.53, "least overfill at R16 best via/feed/overlap"),
    ("of0p04_d0p228_fw0p36_ol0p55", 0.04, 0.228, 0.36, 0.55, "least overfill with strongest local notch drive"),
    ("of0p08_d0p222_fw0p35_ol0p51", 0.08, 0.222, 0.35, 0.51, "slightly reduced overfill, safe corner"),
    ("of0p08_d0p225_fw0p36_ol0p53", 0.08, 0.225, 0.36, 0.53, "slightly reduced overfill at center"),
    ("of0p08_d0p228_fw0p36_ol0p55", 0.08, 0.228, 0.36, 0.55, "slightly reduced overfill with strong via"),
    ("of0p10_d0p222_fw0p35_ol0p51", 0.10, 0.222, 0.35, 0.51, "R17 safe low-via repeat"),
    ("of0p10_d0p225_fw0p36_ol0p53", 0.10, 0.225, 0.36, 0.53, "R16/R17 measured best repeat"),
    ("of0p10_d0p228_fw0p36_ol0p55", 0.10, 0.228, 0.36, 0.55, "R17 strongest 5G repeat"),
    ("of0p12_d0p222_fw0p35_ol0p51", 0.12, 0.222, 0.35, 0.51, "slightly increased overfill, safe via"),
    ("of0p12_d0p225_fw0p36_ol0p53", 0.12, 0.225, 0.36, 0.53, "slightly increased overfill at center"),
    ("of0p12_d0p228_fw0p36_ol0p55", 0.12, 0.228, 0.36, 0.55, "slightly increased overfill with strong via"),
    ("of0p16_d0p222_fw0p35_ol0p51", 0.16, 0.222, 0.35, 0.51, "largest overfill, safe via"),
    ("of0p16_d0p225_fw0p36_ol0p53", 0.16, 0.225, 0.36, 0.53, "largest overfill at center"),
    ("of0p16_d0p228_fw0p36_ol0p55", 0.16, 0.228, 0.36, 0.55, "largest overfill with strong via"),
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
        raise ValueError(f"R18 generator expects 16x16 binary {key}")
    return out


def row_from_params(
    template_params: dict[str, object],
    *,
    idx: int,
    geom_label: str,
    overfill_ratio: float,
    via_diameter_mm: float,
    feed_w_mm: float,
    coupling_overlap_mm: float,
    geom_note: str,
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r18_{idx:02d}_r16best_{geom_label}"
    notes = (
        "R18 pixel overfill tune around measured R16/R17 best; "
        f"base={BASE_NAME}; geom={geom_label}; {geom_note}. "
        "Metal/via topology is fixed; overfill is now an explicit NN geometry feature. "
        "S21 remains primary; S11/S22 remain low-weight auxiliary training targets."
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
        "custom_mask_rows": ";".join(rows_from_params(template_params, "mask_rows")),
        "via_mask_rows": ";".join(rows_from_params(template_params, "via_mask_rows")),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_diameter_mm + 0.12:.6g}",
        "seed": str(18000 + idx),
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
    for idx, (geom_label, overfill_ratio, via_diameter_mm, feed_w_mm, coupling_overlap_mm, geom_note) in enumerate(
        GEOM_VARIANTS,
        start=1,
    ):
        rows.append(
            row_from_params(
                base_params,
                idx=idx,
                geom_label=geom_label,
                overfill_ratio=overfill_ratio,
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
    parser = argparse.ArgumentParser(description="Write R18 pixel overfill tuning candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=15)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r18_overfill_tune_1to10.csv",
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
    print(f"Wrote {len(rows)} R18 overfill tuning candidates: {args.out}")


if __name__ == "__main__":
    main()
