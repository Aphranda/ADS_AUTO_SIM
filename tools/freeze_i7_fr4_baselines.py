#!/usr/bin/env python3
"""Register immutable baselines for the i7 FR4 round13 L555 taper verdict set."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.runtime import (
    build_baseline_entry,
    build_baseline_index,
    read_baseline_index,
    read_single_csv_row,
    validate_baseline_index,
    write_baseline_index,
    write_baseline_summary_csv,
)
from simads.runtime.manifest import artifact_entry

PROJECT_ID = "bfp_6_8g_i7_fr4"
ROUND_ID = "round13"
CANDIDATE_ID = "i7_fr4_r13_retest_base_l555_taper"
BASELINE_DIR = Path("projects") / PROJECT_ID / "baselines" / "i7_fr4_r13_l555_taper"


def repo_path(relative: str | Path) -> Path:
    return _SIM_ROOT / relative


def rel_path(relative: str | Path) -> Path:
    return Path(relative)


def checked_artifacts(paths: dict[str, Path], *, producer: str) -> dict[str, Path]:
    missing = [str(path) for path in paths.values() if not repo_path(path).exists()]
    if missing:
        raise FileNotFoundError("missing baseline artifacts:\n" + "\n".join(missing))
    return paths


def repo_relative_artifacts(paths: dict[str, Path], *, producer: str) -> list[dict[str, object]]:
    artifacts: list[dict[str, object]] = []
    for kind, path in paths.items():
        absolute = repo_path(path)
        item = artifact_entry(kind, absolute, producer=producer)
        item["path"] = str(path)
        artifacts.append(item)
    return artifacts


def freeze_entry(
    *,
    backend: str,
    label: str,
    source_kind: str,
    source_run_id: str | None,
    metrics: dict[str, str],
    artifacts: dict[str, Path],
    tags: list[str],
    notes: str,
    producer: str,
):
    entry = build_baseline_entry(
        project_id=PROJECT_ID,
        round_id=ROUND_ID,
        candidate_id=CANDIDATE_ID,
        backend=backend,
        label=label,
        source_kind=source_kind,
        source_run_id=source_run_id,
        metrics=metrics,
        artifacts={},
        tags=tags,
        notes=notes,
        producer=producer,
    )
    return type(entry)(
        **{
            **entry.to_dict(),
            "artifacts": repo_relative_artifacts(artifacts, producer=producer),
        }
    )


def build_index() -> dict[str, object]:
    layout_dir = rel_path(
        Path("projects")
        / PROJECT_ID
        / "layouts"
        / "interdigital_7o_fr4_210um_round13_retest_4to10_40"
    )
    ads_dir = rel_path(
        Path("projects")
        / PROJECT_ID
        / "results"
        / "interdigital_7o_fr4_210um_round13_retest_4to10_40"
    )
    ads_run_dir = (
        ads_dir
        / "runs"
        / "bfp_6_8g_i7_fr4_round13_i7_fr4_r13_retest_base_l555_taper_home_simads_em_parallel_20260802_141512"
    )
    hfss_auto_dir = rel_path(Path("projects") / PROJECT_ID / "results" / "hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd")
    hfss_manual_dir = rel_path(Path("projects") / PROJECT_ID / "results" / "hfss_verdict_i7_fr4_r13_manual_saved")

    ads_score = ads_dir / "i7_fr4_r13_retest_base_l555_taper_mm_coords_score.csv"
    hfss_auto_score = hfss_auto_dir / "i7_fr4_r13_retest_base_l555_taper_hfss_score.csv"
    hfss_manual_score = hfss_manual_dir / "i7_fr4_r13_retest_base_l555_taper_hfss_manual_saved_score.csv"
    ads_metrics = read_single_csv_row(repo_path(ads_score))
    hfss_auto_metrics = read_single_csv_row(repo_path(hfss_auto_score))
    hfss_manual_metrics = read_single_csv_row(repo_path(hfss_manual_score))

    entries = [
        freeze_entry(
            backend="ads_rfpro",
            label="ads_round13_rfpro",
            source_kind="ads_run",
            source_run_id=ads_metrics.get("run_id"),
            metrics=ads_metrics,
            artifacts=checked_artifacts(
                {
                    "layout_json": layout_dir / "i7_fr4_r13_retest_base_l555_taper_layout.json",
                    "params": layout_dir / "i7_fr4_r13_retest_base_l555_taper_params.json",
                    "dxf": layout_dir / "i7_fr4_r13_retest_base_l555_taper_mm_coords.dxf",
                    "layout_svg": layout_dir / "i7_fr4_r13_retest_base_l555_taper.svg",
                    "drc": layout_dir / "i7_fr4_r13_retest_base_l555_taper_drc.txt",
                    "tuning_table": layout_dir / "i7_fr4_r13_retest_base_l555_taper_tuning_table.csv",
                    "ads_trace": ads_dir / "i7_fr4_r13_retest_base_l555_taper_mm_coords_rfpro.csv",
                    "score": ads_score,
                    "fem_txt": ads_dir / "i7_fr4_r13_retest_base_l555_taper_mm_coords_FEM_a_full.csv",
                    "log": ads_dir / "i7_fr4_r13_retest_base_l555_taper_mm_coords_flow.log",
                    "svg": ads_dir / "svg" / "i7_fr4_r13_retest_base_l555_taper_s_curves.svg",
                    "run_manifest": ads_run_dir / "run_manifest.json",
                    "artifact_manifest": ads_run_dir / "artifact_manifest.json",
                    "state": ads_run_dir / "state.json",
                },
                producer="tools/run_ads_filter_sweep_parallel.py",
            ),
            tags=["baseline", "round13", "ads", "rfpro", "fr4_210um"],
            notes="ADS/RFPro round13 retest baseline for the L555 taper geometry.",
            producer="tools/freeze_i7_fr4_baselines.py",
        ),
        freeze_entry(
            backend="hfss3dlayout",
            label="hfss_aedt_edge_port_gnd",
            source_kind="hfss_verdict",
            source_run_id=None,
            metrics=hfss_auto_metrics,
            artifacts=checked_artifacts(
                {
                    "s2p": hfss_auto_dir / "i7_fr4_r13_retest_base_l555_taper_hfss.s2p",
                    "score": hfss_auto_score,
                    "trace_csv": hfss_auto_dir / "i7_fr4_r13_retest_base_l555_taper_hfss_trace.csv",
                    "summary": hfss_auto_dir / "svg" / "i7_fr4_r13_retest_base_l555_taper_hfss_plot_summary.csv",
                    "svg": hfss_auto_dir / "svg" / "i7_fr4_r13_retest_base_l555_taper_hfss_s_curves.svg",
                },
                producer="tools/hfss/run_hfss_verdict.py",
            ),
            tags=["baseline", "round13", "hfss", "aedt-edge", "port-edges-gnd", "fr4_210um"],
            notes="HFSS automatic AEDT edge-port verdict with explicit finite GND reference.",
            producer="tools/freeze_i7_fr4_baselines.py",
        ),
        freeze_entry(
            backend="hfss3dlayout_manual",
            label="hfss_manual_port_saved",
            source_kind="hfss_manual_verdict",
            source_run_id=None,
            metrics=hfss_manual_metrics,
            artifacts=checked_artifacts(
                {
                    "s2p": hfss_manual_dir / "i7_fr4_r13_retest_base_l555_taper_hfss_manual_saved.s2p",
                    "score": hfss_manual_score,
                    "trace_csv": hfss_manual_dir / "i7_fr4_r13_retest_base_l555_taper_hfss_manual_saved_trace.csv",
                    "summary": hfss_manual_dir
                    / "svg"
                    / "i7_fr4_r13_retest_base_l555_taper_hfss_manual_saved_plot_summary.csv",
                    "svg": hfss_manual_dir
                    / "svg"
                    / "i7_fr4_r13_retest_base_l555_taper_hfss_manual_saved_s_curves.svg",
                },
                producer="manual HFSS port selection + exported result",
            ),
            tags=["baseline", "round13", "hfss", "manual-port", "fr4_210um"],
            notes="HFSS verdict exported after manual port creation by selecting the signal edge and GND reference edge.",
            producer="tools/freeze_i7_fr4_baselines.py",
        ),
    ]

    return build_baseline_index(
        project_id=PROJECT_ID,
        entries=entries,
        policy="immutable_artifact_hashes_no_silent_overwrite",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze the i7 FR4 round13 L555 taper ADS/HFSS baselines.")
    parser.add_argument("--index", type=Path, default=BASELINE_DIR / "baseline_index.json")
    parser.add_argument("--summary", type=Path, default=BASELINE_DIR / "baseline_summary.csv")
    parser.add_argument("--check", action="store_true", help="Validate the existing baseline index only.")
    parser.add_argument("--allow-update", action="store_true", help="Explicitly rewrite the baseline index.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index_path = repo_path(args.index) if not args.index.is_absolute() else args.index
    summary_path = repo_path(args.summary) if not args.summary.is_absolute() else args.summary

    if args.check:
        if not index_path.exists():
            raise SystemExit(f"baseline index does not exist: {index_path}")
        errors = validate_baseline_index(index_path)
        if errors:
            raise SystemExit("baseline validation failed:\n" + "\n".join(errors))
        print(f"Baseline index is valid: {index_path}")
        return

    index = build_index()
    write_baseline_index(index_path, index, allow_update=args.allow_update)
    current_index = read_baseline_index(index_path)
    errors = validate_baseline_index(index_path)
    if errors:
        raise SystemExit("baseline validation failed:\n" + "\n".join(errors))
    write_baseline_summary_csv(summary_path, current_index)
    print(f"Frozen baseline index: {index_path}")
    print(f"Baseline summary: {summary_path}")


if __name__ == "__main__":
    main()
