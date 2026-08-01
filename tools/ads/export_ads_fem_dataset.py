#!/usr/bin/env python3
"""Export ADS EM Setup FEM fitted dataset to tab-delimited text."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_TOOLS_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
for _path in (_TOOLS_ROOT, _SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import profile_names, resolve_workspace
from simads.ads.dataset import (
    DatasetExportPlan,
    dataset_path,
    db_from_mag,
    delimiter_text,
    phase_deg,
    write_ads_display_like_table,
    write_full_table,
)


def read_fem_data(path: Path) -> list[dict[str, float]]:
    import keysight.ads.dataset as dataset

    with dataset.open(path) as ds:
        block = ds["data"]
        df = block.to_dataframe().reset_index()

    rows: list[dict[str, float]] = []
    for _, item in df.iterrows():
        freq = complex(item["freq"]).real
        row: dict[str, float] = {
            "frequency_hz": freq,
            "frequency_ghz": freq / 1e9,
        }
        for label, ads_name in (
            ("s11", "S[1,1]"),
            ("s21", "S[2,1]"),
            ("s12", "S[1,2]"),
            ("s22", "S[2,2]"),
        ):
            value = complex(item[ads_name])
            mag = abs(value)
            row[f"{label}_real"] = value.real
            row[f"{label}_imag"] = value.imag
            row[f"{label}_mag"] = mag
            row[f"{label}_db"] = db_from_mag(mag)
            row[f"{label}_phase_deg"] = phase_deg(value)
        rows.append(row)
    return rows


def write_full_table(rows: list[dict[str, float]], path: Path, delimiter: str) -> None:
    if not rows:
        raise ValueError("no rows to export")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def write_ads_display_like_table(rows: list[dict[str, float]], path: Path, traces: list[str]) -> None:
    if not rows:
        raise ValueError("no rows to export")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        for idx, trace in enumerate(traces):
            if idx:
                fp.write("\n\n")
            fp.write(f"freq\tdB({trace}_fitted)\n")
            key = trace.lower()
            for row in rows:
                fp.write(f"{row['frequency_hz']:.17E}\t{row[f'{key}_db']:.17E}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export ADS *_FEM_a.ds fitted S-parameters to TXT/CSV.")
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--cell", help="ADS cell name, e.g. r2e_l600_mm_coords.")
    parser.add_argument("--dataset", type=Path, help="Explicit ADS .ds path. Overrides --cell.")
    parser.add_argument("--suffix", default="a", help="Dataset suffix after _FEM_, default: a.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--delimiter", default="tab", choices=["tab", "comma"])
    parser.add_argument("--format", default="ads-display", choices=["ads-display", "full"])
    parser.add_argument("--traces", nargs="+", default=["S21"], choices=["S11", "S21", "S12", "S22"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = resolve_workspace(args.profile, args.workspace)
    if args.dataset is None and not args.cell:
        raise SystemExit("Either --dataset or --cell is required.")

    ds_path = args.dataset or dataset_path(workspace, args.cell, args.suffix)
    if not ds_path.exists():
        raise FileNotFoundError(f"ADS dataset not found: {ds_path}")

    rows = read_fem_data(ds_path)
    plan = DatasetExportPlan(
        profile_id=args.profile,
        workspace=workspace,
        dataset_path=ds_path,
        output_path=args.out,
        delimiter=args.delimiter,
        output_format=args.format,
        traces=tuple(args.traces),
    )
    if args.format == "ads-display":
        write_ads_display_like_table(rows, plan.output_path, plan.traces)
    else:
        write_full_table(rows, plan.output_path, delimiter_text(plan.delimiter))
    print(f"Exported {len(rows)} fitted FEM points")
    print(f"  dataset: {ds_path}")
    print(f"  output:  {args.out}")


if __name__ == "__main__":
    main()
