"""Build compact ADS/HFSS verdict summaries from existing result artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


KEY_METRICS = (
    "status",
    "s21_5g_db",
    "s21_6g_db",
    "s21_7g_db",
    "s21_8g_db",
    "s21_9g_db",
    "passband_min_s21_db",
    "passband_ripple_db",
    "worst_s11_6_8_db",
    "worst_s22_6_8_db",
)


def read_first_csv_row(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows[0]


def metric_subset(row: dict[str, str]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for key in KEY_METRICS:
        if key not in row:
            continue
        value = row[key]
        if key == "status":
            metrics[key] = value
        else:
            metrics[key] = float(value)
    return metrics


def read_compare_summary(path: Path) -> dict[str, dict[str, float | str]]:
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    summary: dict[str, dict[str, float | str]] = {}
    for row in rows:
        sparam = row.get("sparam")
        if not sparam:
            continue
        summary[sparam.lower()] = {
            key: (float(value) if key != "sparam" and value not in {"", "nan"} else value)
            for key, value in row.items()
        }
    return summary


def classify_verdict(ads_metrics: dict[str, Any], hfss_metrics: dict[str, Any]) -> str:
    if ads_metrics.get("status") == "PASS" and hfss_metrics.get("status") == "PASS":
        return "release_candidate"
    if ads_metrics.get("status") == "FAIL" or hfss_metrics.get("status") == "FAIL":
        return "reject"
    return "needs_tuning"


def build_verdict_summary(
    *,
    candidate_id: str,
    ads_score_csv: Path,
    hfss_score_csv: Path,
    compare_summary_csv: Path,
    compare_svg: Path | None = None,
    hfss_run_manifest: Path | None = None,
    compare_run_manifest: Path | None = None,
) -> dict[str, Any]:
    ads_row = read_first_csv_row(ads_score_csv)
    hfss_row = read_first_csv_row(hfss_score_csv)
    ads_metrics = metric_subset(ads_row)
    hfss_metrics = metric_subset(hfss_row)
    compare = read_compare_summary(compare_summary_csv)
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "verdict": classify_verdict(ads_metrics, hfss_metrics),
        "ads": {
            "score_csv": str(ads_score_csv),
            "metrics": ads_metrics,
        },
        "hfss": {
            "score_csv": str(hfss_score_csv),
            "run_manifest": str(hfss_run_manifest) if hfss_run_manifest is not None else None,
            "metrics": hfss_metrics,
        },
        "compare": {
            "summary_csv": str(compare_summary_csv),
            "svg": str(compare_svg) if compare_svg is not None else None,
            "run_manifest": str(compare_run_manifest) if compare_run_manifest is not None else None,
            "metrics": compare,
        },
    }


def write_verdict_summary(path: Path, summary: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize an ADS/HFSS verdict from existing score and compare artifacts.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--ads-score", type=Path, required=True)
    parser.add_argument("--hfss-score", type=Path, required=True)
    parser.add_argument("--compare-summary", type=Path, required=True)
    parser.add_argument("--compare-svg", type=Path, default=None)
    parser.add_argument("--hfss-run-manifest", type=Path, default=None)
    parser.add_argument("--compare-run-manifest", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_verdict_summary(
        candidate_id=args.candidate_id,
        ads_score_csv=args.ads_score,
        hfss_score_csv=args.hfss_score,
        compare_summary_csv=args.compare_summary,
        compare_svg=args.compare_svg,
        hfss_run_manifest=args.hfss_run_manifest,
        compare_run_manifest=args.compare_run_manifest,
    )
    print(write_verdict_summary(args.out, summary))


if __name__ == "__main__":
    main()

