#!/usr/bin/env python3
"""Create R20 two-level local subcell loading candidates.

The first-level grid remains the proven 16x16 QR-like metal/via topology. R20
adds second-level local continuous maps for open stubs, attached pads, and
in-pixel slots around the lower-shoulder hot region. These maps are written as
16x16 float rows so the neural surrogate can see the subcell operator.
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
    "sub_stub_len_rows",
    "sub_stub_w_rows",
    "sub_pad_rows",
    "sub_slot_gap_rows",
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
        "r19slot",
        "pixel_qr_bpf_fr4_210um_r19_local_pixel_guard_1to10",
        "pixel_qr16_fr4_210um_r19_20_safe_slot_rm_r10c05",
        "R19 high-side best slot baseline",
    ),
    (
        "r16best",
        "pixel_qr_bpf_fr4_210um_r16_d0p22_continuous_tune_1to10",
        "pixel_qr16_fr4_210um_r16_05_r8d22v_d0p225_fw0p36_ol0p53",
        "R16/R17 balanced best baseline",
    ),
]

SUBCELL_OPS = [
    ("stub_r10c05_l0p105_w0p105", "stub", (10, 5), 0.105, 0.105, "minimum-rule open stub at saturated lower inner pixel"),
    ("stub_r10c05_l0p14_w0p105", "stub", (10, 5), 0.14, 0.105, "medium open stub at saturated lower inner pixel"),
    ("stub_r11c05_l0p105_w0p105", "stub", (11, 5), 0.105, 0.105, "remote minimum-rule open stub"),
    ("stub_r11c05_l0p14_w0p105", "stub", (11, 5), 0.14, 0.105, "remote medium open stub"),
    ("pad_r11c05_s0p105", "pad", (11, 5), 0.105, 0.0, "minimum-rule attached lower pad"),
    ("pad_r12c05_s0p105", "pad", (12, 5), 0.105, 0.0, "far lower weak minimum-rule attached pad"),
    ("slot_r10c04_g0p105", "slot", (10, 4), 0.105, 0.0, "minimum-rule in-pixel slot on outer extension"),
    ("slot_r10c05_g0p105", "slot", (10, 5), 0.105, 0.0, "minimum-rule in-pixel slot on inner extension"),
    ("slot_r11c05_g0p105", "slot", (11, 5), 0.105, 0.0, "minimum-rule remote in-pixel slot"),
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
        raise ValueError(f"R20 generator expects 16x16 binary {key}")
    return out


def zero_map(n: int = 16) -> list[list[float]]:
    return [[0.0 for _ in range(n)] for _ in range(n)]


def float_rows(values: list[list[float]]) -> str:
    return ";".join(",".join(f"{value:.6g}" for value in row) for row in values)


def mirror_positions(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def subcell_maps(kind: str, pos: tuple[int, int], primary: float, secondary: float) -> tuple[str, str, str, str]:
    stub_len = zero_map()
    stub_w = zero_map()
    pad = zero_map()
    slot = zero_map()
    for row, col in mirror_positions(*pos):
        if kind == "stub":
            stub_len[row][col] = primary
            stub_w[row][col] = secondary
        elif kind == "pad":
            pad[row][col] = primary
        elif kind == "slot":
            slot[row][col] = primary
        else:
            raise ValueError(f"unsupported subcell kind: {kind}")
    return float_rows(stub_len), float_rows(stub_w), float_rows(pad), float_rows(slot)


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    base_label: str,
    base_name: str,
    base_note: str,
    op_label: str,
    op_note: str,
    sub_rows: tuple[str, str, str, str],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r20_{idx:02d}_{base_label}_{op_label}"
    notes = (
        "R20 two-level QR subcell loading; "
        f"base={base_name} ({base_note}); op={op_label}; {op_note}. "
        "First-level 16x16 QR mask is retained; second-level local maps encode stub/pad/slot geometry for the surrogate. "
        "S21 remains primary feedback; S11/S22 remain low-weight auxiliary targets."
    )
    via_diameter_mm = float(params["via_diameter_mm"])  # type: ignore[index]
    via_pad_diameter_mm = float(params["via_pad_diameter_mm"])  # type: ignore[index]
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
        "custom_mask_rows": ";".join(rows_from_params(template_params, "mask_rows")),
        "via_mask_rows": ";".join(rows_from_params(template_params, "via_mask_rows")),
        "via_diameter_mm": f"{via_diameter_mm:.6g}",
        "via_pad_diameter_mm": f"{via_pad_diameter_mm:.6g}",
        "sub_stub_len_rows": sub_rows[0],
        "sub_stub_w_rows": sub_rows[1],
        "sub_pad_rows": sub_rows[2],
        "sub_slot_gap_rows": sub_rows[3],
        "seed": str(20000 + idx),
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
    idx = 0
    for base_label, sweep_dir, base_name, base_note in BASES:
        params_path = root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / sweep_dir / f"{base_name}_params.json"
        base_params = read_json(params_path)
        for op_label, kind, pos, primary, secondary, op_note in SUBCELL_OPS:
            idx += 1
            rows.append(
                make_row(
                    base_params,
                    idx=idx,
                    base_label=base_label,
                    base_name=base_name,
                    base_note=base_note,
                    op_label=op_label,
                    op_note=op_note,
                    sub_rows=subcell_maps(kind, pos, primary, secondary),
                )
            )
            if len(rows) >= max_candidates:
                return rows
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R20 two-level subcell loading candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=20)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r20_subcell_loading_1to10.csv",
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
    print(f"Wrote {len(rows)} R20 two-level subcell loading candidates: {args.out}")


if __name__ == "__main__":
    main()
