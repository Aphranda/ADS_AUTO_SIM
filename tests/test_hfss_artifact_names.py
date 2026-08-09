from pathlib import Path

import pytest

from simads.hfss.artifact_names import (
    event_log_path_for_json,
    is_local_runtime_json_name,
    is_runtime_artifact_path,
    is_trackable_json_name,
    json_artifact_class,
    json_artifact_name,
    json_artifact_path,
    normalize_artifact_stem,
)


def test_json_artifact_name_normalizes_stem_and_applies_registered_suffix() -> None:
    assert normalize_artifact_stem("BFP Core Y Offset +0.10") == "bfp_core_y_offset_0_10"
    assert json_artifact_name("BFP Core Y Offset +0.10", "layout") == "bfp_core_y_offset_0_10_layout.json"
    assert json_artifact_path(Path("out"), "Run Existing", "run_log") == Path("out/run_existing_run_log.json")


def test_json_artifact_name_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="unknown JSON artifact kind"):
        json_artifact_name("demo", "temporary")


def test_event_log_path_uses_events_suffix_and_strips_runtime_json_suffix() -> None:
    assert event_log_path_for_json(Path("results/run_existing_run_log.json")) == Path("results/run_existing_events.jsonl")
    assert event_log_path_for_json(Path("results/export_only.json")) == Path("results/export_only_events.jsonl")


def test_json_name_classification_splits_trackable_and_runtime_outputs() -> None:
    assert is_trackable_json_name("bfp_core_y_offset_p0p10_layout.json")
    assert is_trackable_json_name("simulation_manifest.json")
    assert is_trackable_json_name("rf_in_cutout_metrics.json")
    assert not is_trackable_json_name("run_existing_run_log.json")

    assert is_local_runtime_json_name("run_existing_run_log.json")
    assert is_local_runtime_json_name("replace_dry_run_log.json")
    assert is_local_runtime_json_name("inspect_ports.json")
    assert is_local_runtime_json_name("bfp_api_layout_api_extract_raw.json")
    assert is_local_runtime_json_name("extract_layout.json")
    assert is_local_runtime_json_name("extract_layout_distilled.json")
    assert not is_local_runtime_json_name("bfp_core_y_offset_p0p10_summary.json")


def test_path_classification_uses_directory_context() -> None:
    assert json_artifact_class("config/optimizer/i7_fr4_deterministic_variant_probe.json") == "trackable_config_json"
    assert not is_runtime_artifact_path("config/optimizer/i7_fr4_deterministic_variant_probe.json")

    assert json_artifact_class("tools/hfss/script_classes.json") == "trackable_config_json"
    assert (
        json_artifact_class("projects/demo/results/baselines/demo_baseline_freeze_20260809.json")
        == "trackable_json"
    )
    assert json_artifact_class("projects/demo/reports/demo_fullband_metrics_20260809.json") == "trackable_json"
    assert json_artifact_class("projects/demo/results/measurement_compare/demo_vs_measured_batch.json") == "trackable_json"
    assert json_artifact_class("projects/demo/results/saved_launch_design_compare.json") == "trackable_json"
    assert json_artifact_class("projects/demo/layouts/extracted/demo_api_layout_full.json") == "trackable_json"
    assert json_artifact_class("projects/demo/layouts/rf_in_cutout/demo_api_layout_full.json") == "trackable_json"

    assert json_artifact_class("projects/demo/results/run_candidate.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/reports/inspect_ports.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/reports/single_candidate_solve_20260809.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/results/export_report.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/results/extract_layout.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/runs/run_001/run_manifest.json") == "trackable_json"
    assert json_artifact_class("projects/demo/results/aedb_saved_geometry_hints.json") == "local_runtime_json"
    assert json_artifact_class("projects/demo/results/candidate_metrics.json") == "trackable_json"
    assert json_artifact_class("projects/demo/results/candidate_summary.json") == "trackable_json"
