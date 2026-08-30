#!/usr/bin/env python3
"""Generate TX_BAND1 MCFIL fine-tune candidates from HFSS score feedback."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_PARAMS = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil" / "tx_band1_mcfil_r0_params.json"
DEFAULT_OUT_DIR = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil_iter" / "round1"
DEFAULT_FEEDBACK = (
    REPO_ROOT
    / "projects"
    / "RFSOC_RF"
    / "hfss_runs"
    / "tx_band1_mcfil_alumina_bb_14_23g"
    / "tx_band1_mcfil_r0_tx_score.csv"
)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def load_feedback(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def torch_available() -> bool:
    try:
        import torch  # noqa: F401
    except Exception:
        return False
    return True


def cnn_status(feedback_rows: list[dict[str, str]], min_samples: int) -> dict[str, Any]:
    return {
        "model": "TxBandMcfilSectionCnn",
        "input_shape": "5 coupled sections x [length, gap, mean_width, outer_flag]",
        "torch_available": torch_available(),
        "training_samples": len(feedback_rows),
        "min_samples_for_training": min_samples,
        "mode": "trained_ranker" if len(feedback_rows) >= min_samples and torch_available() else "cold_start_score_feedback",
        "note": "CNN ranking is enabled after enough HFSS-scored MCFIL samples exist; cold-start uses score-informed physics priors.",
    }


def _set_tuning(params: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(params))
    data["layout_id"] = spec["name"]
    data["ports"] = {
        "status": "confirmed",
        "p1_source_entity": 2,
        "p2_source_entity": 9,
        "review_note": "Confirmed TX_BAND1 MCFIL ports: P1 on right lower strip, P2 on left upper strip.",
    }
    data.setdefault("global_parameters", {})["x_offset_mm"] = float(spec.get("x_offset_mm", 0.0))
    data.setdefault("global_parameters", {})["y_offset_mm"] = float(spec.get("y_offset_mm", 0.0))
    data["iteration"] = {
        "round": "round1",
        "source": "tools/make_tx_band_mcfil_iteration.py",
        "feedback_source": spec.get("feedback_source"),
        "strategy": spec["strategy"],
        "cnn_mode": spec["cnn_mode"],
        "notes": spec["notes"],
    }
    for section in data["coupled_sections"]:
        idx = int(section["section"])
        section_tuning = section.setdefault("tuning", {})
        section_tuning["length_delta_mm"] = float(spec["length_delta_mm"][idx - 1])
        section_tuning["width_delta_mm"] = float(spec["width_delta_mm"][idx - 1])
        section_tuning["gap_delta_mm"] = float(spec["gap_delta_mm"][idx - 1])
        section_tuning["x_delta_mm"] = 0.0
        section_tuning["y_delta_mm"] = 0.0
    return data


def min_gap_after_tuning(params: dict[str, Any]) -> float:
    gaps: list[float] = []
    for section in params["coupled_sections"]:
        base_gaps = section.get("coupling_gaps_mm") or []
        delta = float(section.get("tuning", {}).get("gap_delta_mm", 0.0))
        gaps.extend(float(gap) + delta for gap in base_gaps)
    return min(gaps) if gaps else 0.0


def candidate_specs(cnn_mode: str, feedback_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    feedback_source = feedback_rows[-1].get("trace_csv", "") if feedback_rows else ""
    return [
        {
            "name": "tx_band1_mcfil_r1_cnn001_len_p035_gap_m010",
            "strategy": "score_feedback_lengthen_peak_high_mild_coupling",
            "cnn_mode": cnn_mode,
            "feedback_source": feedback_source,
            "length_delta_mm": [0.035, 0.035, 0.035, 0.035, 0.035],
            "width_delta_mm": [0.0, 0.0, 0.0, 0.0, 0.0],
            "gap_delta_mm": [-0.010, -0.015, -0.020, -0.015, -0.010],
            "notes": "Mild all-section length increase to pull peak down; modest gap reduction to lift the weak low passband edge.",
        },
        {
            "name": "tx_band1_mcfil_r1_cnn002_len_p055_gap_m020",
            "strategy": "score_feedback_center_shift_with_bandwidth",
            "cnn_mode": cnn_mode,
            "feedback_source": feedback_source,
            "length_delta_mm": [0.055, 0.055, 0.055, 0.055, 0.055],
            "width_delta_mm": [0.0, 0.0, 0.0, 0.0, 0.0],
            "gap_delta_mm": [-0.020, -0.030, -0.040, -0.030, -0.020],
            "notes": "Primary R1 candidate: peak was high at 19.25 GHz, so lengthen about 4 percent and increase coupling.",
        },
        {
            "name": "tx_band1_mcfil_r1_cnn003_len_p075_gap_m025",
            "strategy": "score_feedback_aggressive_lower_shift",
            "cnn_mode": cnn_mode,
            "feedback_source": feedback_source,
            "length_delta_mm": [0.075, 0.075, 0.075, 0.075, 0.075],
            "width_delta_mm": [0.0, 0.0, 0.0, 0.0, 0.0],
            "gap_delta_mm": [-0.025, -0.035, -0.045, -0.035, -0.025],
            "notes": "Aggressive center-frequency pull-down; still keeps the tightest original outer gaps above 39 um.",
        },
        {
            "name": "tx_band1_mcfil_r1_cnn004_len_p055_gap_m020_w_p008",
            "strategy": "score_feedback_match_and_bandwidth",
            "cnn_mode": cnn_mode,
            "feedback_source": feedback_source,
            "length_delta_mm": [0.055, 0.055, 0.055, 0.055, 0.055],
            "width_delta_mm": [0.008, 0.005, 0.004, 0.005, 0.008],
            "gap_delta_mm": [-0.020, -0.030, -0.040, -0.030, -0.020],
            "notes": "Same center shift as cnn002 plus slight outer width increase to probe port/match sensitivity.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_layout(params_path: Path, out_dir: Path, layout_id: str) -> None:
    script = REPO_ROOT / "tools" / "hfss" / "build_mcfil_dxf_hfss_layout.py"
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--params-in",
            str(params_path),
            "--layout-id",
            layout_id,
            "--out-dir",
            str(out_dir),
        ],
        cwd=REPO_ROOT,
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create score/CNN-feedback TX_BAND1 MCFIL tuning candidates.")
    parser.add_argument("--base-params", type=Path, default=BASE_PARAMS)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--min-cnn-samples", type=int, default=5)
    parser.add_argument("--no-build-layouts", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = load_json(args.base_params)
    feedback_rows = load_feedback(args.feedback)
    cnn = cnn_status(feedback_rows, args.min_cnn_samples)
    specs = candidate_specs(str(cnn["mode"]), feedback_rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plan_rows: list[dict[str, Any]] = []
    for rank, spec in enumerate(specs, start=1):
        params = _set_tuning(base, spec)
        min_gap = min_gap_after_tuning(params)
        if min_gap < 0.015:
            raise ValueError(f"{spec['name']} violates min gap guard: {min_gap:.6g} mm")
        candidate_params = args.out_dir / f"{spec['name']}_seed_params.json"
        candidate_params.write_text(json.dumps(params, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not args.no_build_layouts:
            build_layout(candidate_params, args.out_dir, spec["name"])
        plan_rows.append(
            {
                "rank": rank,
                "candidate": spec["name"],
                "layout_json": str(args.out_dir / f"{spec['name']}_layout.json"),
                "params_json": str(args.out_dir / f"{spec['name']}_params.json"),
                "min_gap_mm": f"{min_gap:.6g}",
                "strategy": spec["strategy"],
                "cnn_mode": spec["cnn_mode"],
                "length_delta_mm": ";".join(f"{item:.6g}" for item in spec["length_delta_mm"]),
                "gap_delta_mm": ";".join(f"{item:.6g}" for item in spec["gap_delta_mm"]),
                "width_delta_mm": ";".join(f"{item:.6g}" for item in spec["width_delta_mm"]),
                "notes": spec["notes"],
            }
        )
    write_csv(args.out_dir / "tx_band1_mcfil_round1_candidate_plan.csv", plan_rows)
    (args.out_dir / "tx_band1_mcfil_round1_cnn_status.json").write_text(
        json.dumps(cnn, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(args.out_dir), "candidates": len(plan_rows), "cnn": cnn}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
