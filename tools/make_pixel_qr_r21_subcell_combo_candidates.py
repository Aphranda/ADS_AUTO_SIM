#!/usr/bin/env python3
"""Create R21 two-level subcell combination candidates.

R20 proved that the six-channel surrogate can see local stub/pad/slot maps,
but single operators stayed near the -17 dB 5 GHz notch plateau. R21 keeps the
same first-level 16x16 QR grid and only combines or slightly resizes already
validated second-level operators. No new neural-network input schema is needed.
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

BASES = {
    "r19high": (
        "pixel_qr16_fr4_210um_r20_08_r19slot_slot_r10c05_g0p105",
        "R20 high-side best based on the R19 safe slot topology",
    ),
    "r19stub": (
        "pixel_qr16_fr4_210um_r20_01_r19slot_stub_r10c05_l0p105_w0p105",
        "R20 safest high-side stub based on the R19 safe slot topology",
    ),
    "r16deep": (
        "pixel_qr16_fr4_210um_r20_11_r16best_stub_r10c05_l0p14_w0p105",
        "R20 deepest measured 5G notch on the R16/R17 balanced topology",
    ),
    "r16slot": (
        "pixel_qr16_fr4_210um_r20_18_r16best_slot_r11c05_g0p105",
        "R20 balanced R16 slot sample with good high-side average",
    ),
}

OPS = [
    ("r19high_slot_g0p12", "r19high", [("slot", 10, 5, 0.12, 0.0)], "slightly wider inner slot on high-side best base"),
    ("r19high_slot_g0p14", "r19high", [("slot", 10, 5, 0.14, 0.0)], "wide inner slot boundary sample"),
    ("r19high_slot_pad_r11", "r19high", [("slot", 10, 5, 0.105, 0.0), ("pad", 11, 5, 0.105, 0.0)], "high-side slot plus minimum remote pad"),
    ("r19high_slot_pad_r12", "r19high", [("slot", 10, 5, 0.105, 0.0), ("pad", 12, 5, 0.105, 0.0)], "high-side slot plus far weak pad"),
    ("r19high_slot_stub_r11", "r19high", [("slot", 10, 5, 0.105, 0.0), ("stub", 11, 5, 0.105, 0.105)], "high-side slot plus remote minimum stub"),
    ("r19high_slot_stub_r10", "r19high", [("slot", 10, 5, 0.105, 0.0), ("stub", 10, 5, 0.105, 0.105)], "high-side slot plus colocated minimum stub"),
    ("r19stub_l0p122", "r19stub", [("stub", 10, 5, 0.122, 0.105)], "intermediate stub length between R20 short and medium"),
    ("r19stub_w0p111", "r19stub", [("stub", 10, 5, 0.105, 0.111)], "minimum-length mildly wider stub within the 4 mil spacing guard"),
    ("r19stub_slot_r11", "r19stub", [("stub", 10, 5, 0.105, 0.105), ("slot", 11, 5, 0.105, 0.0)], "safe stub plus remote slot"),
    ("r19stub_pad_r11", "r19stub", [("stub", 10, 5, 0.105, 0.105), ("pad", 11, 5, 0.105, 0.0)], "safe stub plus minimum remote pad"),
    ("r16deep_l0p122", "r16deep", [("stub", 10, 5, 0.122, 0.105)], "relax deepest R20 stub to recover 6G guard"),
    ("r16deep_w0p111", "r16deep", [("stub", 10, 5, 0.14, 0.111)], "deep R16 stub with mildly wider loading within the 4 mil spacing guard"),
    ("r16deep_stub_pad_r11", "r16deep", [("stub", 10, 5, 0.14, 0.105), ("pad", 11, 5, 0.105, 0.0)], "deep R16 stub plus remote pad"),
    ("r16deep_stub_slot_r11", "r16deep", [("stub", 10, 5, 0.14, 0.105), ("slot", 11, 5, 0.105, 0.0)], "deep R16 stub plus remote slot boundary"),
    ("r16slot_g0p12", "r16slot", [("slot", 11, 5, 0.12, 0.0)], "slightly wider remote slot on R16 base"),
    ("r16slot_g0p14", "r16slot", [("slot", 11, 5, 0.14, 0.0)], "wide remote slot boundary on R16 base"),
    ("r16slot_stub_r10", "r16slot", [("slot", 11, 5, 0.105, 0.0), ("stub", 10, 5, 0.105, 0.105)], "R16 remote slot plus inner minimum stub"),
    ("r16slot_pad_r11", "r16slot", [("slot", 11, 5, 0.105, 0.0), ("pad", 11, 5, 0.105, 0.0)], "R16 remote slot plus colocated minimum pad"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows_from_params(params: dict[str, object], key: str) -> list[str]:
    values = params.get(key)
    if not values:
        values = params["parameters"][key]  # type: ignore[index]
    rows = [str(row) for row in values]  # type: ignore[union-attr]
    if len(rows) != 16 or any(len(row) != 16 or set(row) - {"0", "1"} for row in rows):
        raise ValueError(f"R21 generator expects 16x16 binary {key}")
    return rows


def zero_map(n: int = 16) -> list[list[float]]:
    return [[0.0 for _ in range(n)] for _ in range(n)]


def float_rows(values: list[list[float]]) -> str:
    return ";".join(",".join(f"{value:.6g}" for value in row) for row in values)


def mirror_positions(row: int, col: int, n: int = 16) -> tuple[tuple[int, int], ...]:
    other = n - 1 - col
    if other == col:
        return ((row, col),)
    return ((row, min(col, other)), (row, max(col, other)))


def subcell_maps(settings: list[tuple[str, int, int, float, float]]) -> tuple[str, str, str, str]:
    stub_len = zero_map()
    stub_w = zero_map()
    pad = zero_map()
    slot = zero_map()
    for kind, row, col, primary, secondary in settings:
        for rr, cc in mirror_positions(row, col):
            if kind == "stub":
                stub_len[rr][cc] = primary
                stub_w[rr][cc] = secondary
            elif kind == "pad":
                pad[rr][cc] = primary
            elif kind == "slot":
                slot[rr][cc] = primary
            else:
                raise ValueError(f"unsupported subcell kind: {kind}")
    return float_rows(stub_len), float_rows(stub_w), float_rows(pad), float_rows(slot)


def make_row(
    template_params: dict[str, object],
    *,
    idx: int,
    op_label: str,
    base_label: str,
    base_name: str,
    base_note: str,
    op_note: str,
    sub_rows: tuple[str, str, str, str],
) -> dict[str, str]:
    params = template_params["parameters"]  # type: ignore[index]
    name = f"pixel_qr16_fr4_210um_r21_{idx:02d}_{op_label}"
    notes = (
        "R21 two-level QR subcell combo; "
        f"base={base_name} ({base_label}: {base_note}); op={op_label}; {op_note}. "
        "First-level 16x16 QR mask/via/geometry are retained from the measured R20 base; "
        "second-level stub/pad/slot maps are explicit six-channel surrogate inputs. "
        "S21 remains primary feedback; S11/S22 remain low-weight auxiliary targets."
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
        "custom_mask_rows": ";".join(rows_from_params(template_params, "custom_mask_rows")),
        "via_mask_rows": ";".join(rows_from_params(template_params, "via_mask_rows")),
        "via_diameter_mm": f"{float(params['via_diameter_mm']):.6g}",  # type: ignore[index]
        "via_pad_diameter_mm": f"{float(params['via_pad_diameter_mm']):.6g}",  # type: ignore[index]
        "sub_stub_len_rows": sub_rows[0],
        "sub_stub_w_rows": sub_rows[1],
        "sub_pad_rows": sub_rows[2],
        "sub_slot_gap_rows": sub_rows[3],
        "seed": str(21000 + idx),
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
    layout_dir = root / "projects" / "pixel_qr_bpf_fr4_210um" / "layouts" / "pixel_qr_bpf_fr4_210um_r20_subcell_loading_1to10"
    base_params: dict[str, dict[str, object]] = {}
    for label, (base_name, _) in BASES.items():
        base_params[label] = read_json(layout_dir / f"{base_name}_params.json")

    rows: list[dict[str, str]] = []
    for idx, (op_label, base_label, settings, op_note) in enumerate(OPS, start=1):
        base_name, base_note = BASES[base_label]
        rows.append(
            make_row(
                base_params[base_label],
                idx=idx,
                op_label=op_label,
                base_label=base_label,
                base_name=base_name,
                base_note=base_note,
                op_note=op_note,
                sub_rows=subcell_maps(settings),
            )
        )
        if len(rows) >= max_candidates:
            break
    return rows


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Write R21 two-level subcell combination candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=18)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r21_subcell_combo_1to10.csv",
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
    print(f"Wrote {len(rows)} R21 two-level subcell combo candidates: {args.out}")


if __name__ == "__main__":
    main()
