#!/usr/bin/env python3
"""Build a joined optimization dataset for the FR4 7th-order interdigital BPF."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


PARAM_COLUMNS = [
    "L_mm",
    "tap_mm",
    "Egap_mm",
    "S1_mm",
    "S2_mm",
    "S3_mm",
    "S4_mm",
    "S5_mm",
    "S6_mm",
    "W0_mm",
    "feed_len_mm",
    "feed_taper_len_mm",
    "feed_tip_w_mm",
    "feed_overlap_mm",
    "via_diameter_mm",
]

METRIC_COLUMNS = [
    "s21_5g_db",
    "s21_6g_db",
    "s21_7g_db",
    "s21_8g_db",
    "s21_9g_db",
    "passband_min_s21_db",
    "passband_ripple_db",
    "worst_s11_6_8_db",
    "worst_s22_6_8_db",
]

TARGETS = {
    "s21_5g_db": -25.0,
    "s21_6g_db": -5.0,
    "s21_8g_db": -5.0,
    "passband_min_s21_db": -5.0,
    "passband_ripple_db": 4.0,
    "worst_s11_6_8_db": -6.0,
    "worst_s22_6_8_db": -6.0,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def read_seed_defaults(path: Path) -> dict[str, float | str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    params = data["parameters"]
    gaps = list(params["gaps_mm"])
    defaults: dict[str, float | str] = {
        "L_mm": float(params["resonator_l_mm"]),
        "tap_mm": float(params["tap_from_bottom_mm"]),
        "Egap_mm": float(params["end_gap_mm"]),
        "W0_mm": float(params["w0_mm"]),
        "feed_len_mm": float(params["feed_len_mm"]),
        "feed_taper_len_mm": float(params["feed_taper_len_mm"]),
        "feed_tip_w_mm": float(params["feed_tip_w_mm"]),
        "feed_overlap_mm": float(params["feed_overlap_mm"]),
        "via_diameter_mm": float(params["via_diameter_mm"]),
        "metal_layer": str(params["metal_layer"]),
        "via_layer": str(params["via_layer"]),
    }
    for idx, value in enumerate(gaps, start=1):
        defaults[f"S{idx}_mm"] = float(value)
    return defaults


def parse_float(value: str | float | int | None) -> float:
    if value is None:
        return float("nan")
    text = str(value).strip()
    return float(text) if text else float("nan")


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.6g}"


def normalize_params(row: dict[str, str], defaults: dict[str, float | str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key in PARAM_COLUMNS:
        raw = row.get(key, "")
        value = parse_float(raw) if str(raw).strip() else float(defaults[key])
        normalized[key] = fmt(value)
    normalized["metal_layer"] = row.get("metal_layer", str(defaults["metal_layer"])).strip() or str(defaults["metal_layer"])
    normalized["via_layer"] = row.get("via_layer", str(defaults["via_layer"])).strip() or str(defaults["via_layer"])
    return normalized


def geometry_key(row: dict[str, str]) -> str:
    return "|".join(f"{parse_float(row[key]):.5f}" for key in PARAM_COLUMNS)


def compute_margins(row: dict[str, str]) -> dict[str, float]:
    s21_5 = parse_float(row["s21_5g_db"])
    s21_6 = parse_float(row["s21_6g_db"])
    s21_8 = parse_float(row["s21_8g_db"])
    pass_min = parse_float(row["passband_min_s21_db"])
    ripple = parse_float(row["passband_ripple_db"])
    worst_s11 = parse_float(row["worst_s11_6_8_db"])
    worst_s22 = parse_float(row["worst_s22_6_8_db"])
    return {
        "margin_s21_5g_db": TARGETS["s21_5g_db"] - s21_5,
        "margin_s21_6g_db": s21_6 - TARGETS["s21_6g_db"],
        "margin_s21_8g_db": s21_8 - TARGETS["s21_8g_db"],
        "margin_passband_min_db": pass_min - TARGETS["passband_min_s21_db"],
        "margin_ripple_db": TARGETS["passband_ripple_db"] - ripple,
        "margin_s11_db": TARGETS["worst_s11_6_8_db"] - worst_s11,
        "margin_s22_db": TARGETS["worst_s22_6_8_db"] - worst_s22,
    }


def objective(row: dict[str, str], margins: dict[str, float]) -> float:
    hard_keys = [
        "margin_s21_5g_db",
        "margin_s21_6g_db",
        "margin_s21_8g_db",
        "margin_passband_min_db",
        "margin_ripple_db",
    ]
    hard_violation = sum(max(0.0, -margins[key]) ** 2 for key in hard_keys)
    rl_violation = max(0.0, -margins["margin_s11_db"]) ** 2 + max(0.0, -margins["margin_s22_db"]) ** 2
    worst_return = max(parse_float(row["worst_s11_6_8_db"]), parse_float(row["worst_s22_6_8_db"]))
    ripple = parse_float(row["passband_ripple_db"])
    stop_margin = margins["margin_s21_5g_db"]
    edge_margin = min(margins["margin_s21_6g_db"], margins["margin_s21_8g_db"])
    return (
        20.0
        - 18.0 * hard_violation
        - 10.0 * rl_violation
        + 1.15 * (-worst_return)
        - 0.65 * ripple
        + 0.25 * min(stop_margin, 4.0)
        + 0.35 * min(edge_margin, 4.0)
    )


def plan_index(plan_paths: list[Path], defaults: dict[str, float | str]) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for path in plan_paths:
        for row in read_csv(path):
            name = row["name"].strip()
            normalized = normalize_params(row, defaults)
            normalized["candidate"] = name
            normalized["plan"] = str(path)
            normalized["plan_notes"] = row.get("notes", "")
            rows[name] = normalized
    return rows


def build_rows(summary_paths: list[Path], plans: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for summary_path in summary_paths:
        round_name = summary_path.parent.name
        for summary in read_csv(summary_path):
            candidate = summary["candidate"].strip()
            if candidate not in plans:
                continue
            joined = {
                "round": round_name,
                "candidate": candidate,
                "cell": summary.get("cell", ""),
                "status": summary.get("status", ""),
                "target_profile": summary.get("target_profile", ""),
                "notes": summary.get("notes", plans[candidate].get("plan_notes", "")),
                **{key: plans[candidate][key] for key in PARAM_COLUMNS},
                "metal_layer": plans[candidate]["metal_layer"],
                "via_layer": plans[candidate]["via_layer"],
                **{key: summary.get(key, "") for key in METRIC_COLUMNS},
            }
            margins = compute_margins(joined)
            joined.update({key: fmt(value) for key, value in margins.items()})
            joined["hard_constraints_ok"] = str(
                all(value >= 0.0 for key, value in margins.items() if key not in {"margin_s11_db", "margin_s22_db"})
            )
            joined["rl6_ok"] = str(margins["margin_s11_db"] >= 0.0 and margins["margin_s22_db"] >= 0.0)
            joined["min_constraint_margin_db"] = fmt(min(margins.values()))
            joined["objective_score"] = fmt(objective(joined, margins))
            joined["geometry_key"] = geometry_key(joined)
            rows.append(joined)
    return rows


def write_dataset(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        raise SystemExit("No joined rows found. Check plan and summary globs.")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Join FR4 7th-order interdigital plans and ADS sweep summaries.")
    parser.add_argument(
        "--seed",
        type=Path,
        default=root / "projects" / "bfp_6_8g_i7_fr4" / "layouts" / "interdigital_7o_fr4_210um_round3" / "i7_fr4_r3_base_params.json",
    )
    parser.add_argument("--plan-glob", default="projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round*.csv")
    parser.add_argument("--summary-glob", default="projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/sweep_summary.csv")
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_7o_fr4_training_dataset.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    defaults = read_seed_defaults(args.seed)
    plan_paths = sorted(root.glob(args.plan_glob))
    summary_paths = sorted(root.glob(args.summary_glob))
    plans = plan_index(plan_paths, defaults)
    rows = build_rows(summary_paths, plans)
    rows.sort(key=lambda row: parse_float(row["objective_score"]), reverse=True)
    write_dataset(rows, args.out)
    unique = len({row["geometry_key"] for row in rows})
    print(f"Wrote {len(rows)} measurements / {unique} unique geometries: {args.out}")
    print("Top rows:")
    for row in rows[:8]:
        print(
            f"  {row['candidate']}: objective={row['objective_score']} "
            f"S21@5={row['s21_5g_db']} S21@8={row['s21_8g_db']} "
            f"S11={row['worst_s11_6_8_db']} S22={row['worst_s22_6_8_db']}"
        )


if __name__ == "__main__":
    main()




