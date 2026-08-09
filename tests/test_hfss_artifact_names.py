from pathlib import Path

import pytest

from simads.hfss.artifact_names import (
    event_log_path_for_json,
    is_local_runtime_json_name,
    is_trackable_json_name,
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
    assert not is_local_runtime_json_name("bfp_core_y_offset_p0p10_summary.json")
