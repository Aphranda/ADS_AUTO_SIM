#!/usr/bin/env python3
"""Create R14 floating-stub and slit candidates for the pixel QR BPF.

R13 proved that even remote weak shorted pads can deepen the 5 GHz notch while
collapsing S21 around 6 GHz. R14 keeps the useful R8/R9 main row8 via pair but
does not add any new grounded via. The operators use floating metal length,
local open stubs, and small slits, with optional feed-coupling compensation.
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

# Keep only launch anchors and the proven main row8 via pixels fixed. R14 may
# alter nearby metal, but it must not remove the actual via landing pixels.
LOCKED_ON = {
    (7, 0),
    (7, 15),
    (8, 0),
    (8, 15),
    (8, 4),
    (8, 11),
}

OPERATORS = [
    (
        "open_stub_r10c06_r11c06",
        [(10, 6, 1), (11, 6, 1)],
        "two-pixel floating inner open stub, intended as weak 5 GHz capacitive resonator",
    ),
    (
        "open_stub_r11c05_r12c05",
        [(11, 5, 1), (12, 5, 1)],
        "remote floating vertical open stub, weaker than the R13 shorted version",
    ),
    (
        "open_stub_r11c06_r12c06",
        [(11, 6, 1), (12, 6, 1)],
        "inner remote floating open stub near the center branch",
    ),
    (
        "l_stub_r10c06_r11c05",
        [(10, 6, 1), (11, 5, 1), (11, 6, 1)],
        "small floating L stub to add electrical length without a DC short",
    ),
    (
        "cap_pad_r12c04_r12c05",
        [(12, 4, 1), (12, 5, 1)],
        "far lower floating capacitive pad pair",
    ),
    (
        "slot_rm_r10c05_add_r11c05",
        [(10, 5, 0), (11, 5, 1)],
        "move one existing lower inner pixel farther from the main path, no added via",
    ),
    (
        "slot_rm_r10c05_stub_r11c05_r12c05",
        [(10, 5, 0), (11, 5, 1), (12, 5, 1)],
        "combine a local slit with a remote floating open stub",
    ),
    (
        "near_via_slit_r08c05",
        [(8, 5, 0)],
        "make a narrow floating slit next to the main via landing pixel to tune the lower shoulder",
    ),
    (
        "center_slit_r08c06",
        [(8, 6, 0)],
        "make a central row8 slit to probe whether the 5 GHz notch can move without adding grounded loading",
    ),
]

FEED_VARIANTS = [
    ("basefeed", None, None, "keep base feed geometry"),
    ("recover_olp03", None, 0.03, "increase overlap by 0.03 mm to recover 6 GHz coupling"),
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
        raise ValueError(f"R14 generator expects 16x16 binary {key}")
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


def adjusted_geometry(
    params: dict[str, object],
    feed_w_delta: float | None,
    overlap_delta: float | None,
) -> tuple[float, float]:
    base = params["parameters"]  # type: ignore[index]
    feed_w = float(base["feed_w_mm"])  # type: ignore[index]
    overlap = float(base["coupling_overlap_mm"])  # type: ignore[index]
    if feed_w_delta is not None:
        feed_w += feed_w_delta
    if overlap_delta is not None:
        overlap += overlap_delta
    return feed_w, overlap


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
    name = f"pixel_qr16_fr4_210um_r14_{idx:02d}_{base_label}_{operator_label}_{feed_label}"
    notes = (
        "R14 floating-stub/slit notch probe; "
        f"base={base_name} ({base_note}); op={operator_label}; {operator_note}; feed={feed_label}; {feed_note}. "
        "No new grounded via is added; the main row8 c04/c11 via pair is preserved. "
        "Objective: improve the 5 GHz stopband using S21-primary feedback while keeping S21@6G above the guard."
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
        "seed": str(14000 + idx),
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
        via_rows = rows_from_params(base_params, "via_mask_rows")
        for operator_label, ops, operator_note in OPERATORS:
            metal_rows = apply_operator(base_metal, ops)
            for feed_label, feed_w_delta, overlap_delta, feed_note in FEED_VARIANTS:
                feed_w_mm, coupling_overlap_mm = adjusted_geometry(base_params, feed_w_delta, overlap_delta)
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
    parser = argparse.ArgumentParser(description="Write R14 floating-stub/slit candidate plan.")
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--out",
        type=Path,
        default=root
        / "projects"
        / "pixel_qr_bpf_fr4_210um"
        / "plans"
        / "pixel_qr_bpf_fr4_210um_r14_floating_stub_slit_1to10.csv",
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
    print(f"Wrote {len(rows)} R14 floating-stub/slit candidates: {args.out}")


if __name__ == "__main__":
    main()
