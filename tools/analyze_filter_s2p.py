#!/usr/bin/env python3
"""Score ADS/Touchstone S2P files for the 6-8 GHz SIM-83+ output filter."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


UNIT_SCALE = {
    "HZ": 1e-9,
    "KHZ": 1e-6,
    "MHZ": 1e-3,
    "GHZ": 1.0,
}


def db_from_pair(a: float, b: float, fmt: str) -> float:
    if fmt == "DB":
        return a
    if fmt == "MA":
        return 20.0 * math.log10(max(a, 1e-30))
    if fmt == "RI":
        return 20.0 * math.log10(max(math.hypot(a, b), 1e-30))
    raise ValueError(f"unsupported Touchstone data format: {fmt}")


def read_s2p(path: Path) -> list[tuple[float, float, float, float, float]]:
    unit_scale = 1e-9
    data_fmt = "MA"
    samples: list[tuple[float, float, float, float, float]] = []

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            parts = line[1:].upper().split()
            for part in parts:
                if part in UNIT_SCALE:
                    unit_scale = UNIT_SCALE[part]
                if part in {"DB", "MA", "RI"}:
                    data_fmt = part
            continue
        values = [float(item) for item in line.split()]
        if len(values) < 9:
            continue
        freq_ghz = values[0] * unit_scale
        s11_db = db_from_pair(values[1], values[2], data_fmt)
        s21_db = db_from_pair(values[3], values[4], data_fmt)
        s12_db = db_from_pair(values[5], values[6], data_fmt)
        s22_db = db_from_pair(values[7], values[8], data_fmt)
        samples.append((freq_ghz, s11_db, s21_db, s12_db, s22_db))
    return samples


def interp(samples: list[tuple[float, float, float, float, float]], freq_ghz: float, column: int) -> float:
    ordered = sorted(samples)
    if freq_ghz <= ordered[0][0]:
        return ordered[0][column]
    if freq_ghz >= ordered[-1][0]:
        return ordered[-1][column]
    for left, right in zip(ordered, ordered[1:]):
        if left[0] <= freq_ghz <= right[0]:
            ratio = (freq_ghz - left[0]) / (right[0] - left[0])
            return left[column] + ratio * (right[column] - left[column])
    return ordered[-1][column]


def score(path: Path) -> dict[str, str]:
    samples = read_s2p(path)
    if not samples:
        raise ValueError(f"no S-parameter samples found in {path}")

    passband = [sample for sample in samples if 6.0 <= sample[0] <= 8.0]
    s21_pass = [sample[2] for sample in passband]
    s11_pass = [sample[1] for sample in passband]
    s22_pass = [sample[4] for sample in passband]

    s21_5 = interp(samples, 5.0, 2)
    s21_6 = interp(samples, 6.0, 2)
    s21_7 = interp(samples, 7.0, 2)
    s21_8 = interp(samples, 8.0, 2)
    s21_9 = interp(samples, 9.0, 2)

    pass_min = min(s21_pass) if s21_pass else float("nan")
    pass_max = max(s21_pass) if s21_pass else float("nan")
    ripple = pass_max - pass_min if s21_pass else float("nan")
    s11_best_worst = max(s11_pass) if s11_pass else float("nan")
    s22_best_worst = max(s22_pass) if s22_pass else float("nan")

    ok_5g = s21_5 <= -45.0
    ok_edges = s21_6 >= -3.0 and s21_8 >= -3.0
    ok_pass = pass_min >= -3.5 and ripple <= 3.0
    status = "PASS_CANDIDATE" if ok_5g and ok_edges and ok_pass else "TUNE"

    return {
        "file": str(path),
        "status": status,
        "s21_5g_db": f"{s21_5:.2f}",
        "s21_6g_db": f"{s21_6:.2f}",
        "s21_7g_db": f"{s21_7:.2f}",
        "s21_8g_db": f"{s21_8:.2f}",
        "s21_9g_db": f"{s21_9:.2f}",
        "passband_min_s21_db": f"{pass_min:.2f}",
        "passband_ripple_db": f"{ripple:.2f}",
        "worst_s11_6_8_db": f"{s11_best_worst:.2f}",
        "worst_s22_6_8_db": f"{s22_best_worst:.2f}",
        "note": make_note(s21_5, s21_6, s21_8, pass_min, ripple),
    }


def make_note(s21_5: float, s21_6: float, s21_8: float, pass_min: float, ripple: float) -> str:
    if s21_5 > -45.0:
        return "5 GHz rejection is weak; narrow bandwidth or add extra LO notch/highpass."
    if s21_6 < -3.0 and s21_8 < -3.0:
        return "Both band edges are weak; increase coupling or shorten L less aggressively."
    if s21_6 < -3.0:
        return "Low band edge is weak; increase coupling or slightly lengthen L."
    if s21_8 < -3.0:
        return "High band edge is weak; increase coupling or slightly shorten L."
    if pass_min < -3.5 or ripple > 3.0:
        return "Passband ripple/loss is high; retune tap and symmetric gap pairs."
    return "Candidate meets coarse numeric targets; verify mesh, ports, conductor loss, and manufacturing margins."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze one or more S2P files exported by ADS.")
    parser.add_argument("s2p", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=None, help="Optional CSV summary path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = [score(path) for path in args.s2p]
    fieldnames = list(rows[0].keys())
    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.out}")
    else:
        writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
