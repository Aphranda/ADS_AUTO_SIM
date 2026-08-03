import json
from pathlib import Path

import pytest

from simads.runtime.baseline import (
    FREEZE_LOCK_NAME,
    baseline_id,
    build_baseline_entry,
    build_baseline_index,
    read_baseline_index,
    validate_baseline_index,
    write_baseline_index,
    write_baseline_summary_csv,
)


def test_baseline_id_sanitizes_parts() -> None:
    assert (
        baseline_id("proj A", "round/13", "cand:1", "ads rfpro", "label#x")
        == "proj_A_round_13_cand_1_ads_rfpro_label_x"
    )


def test_build_baseline_entry_records_artifact_hash(tmp_path: Path) -> None:
    artifact = tmp_path / "trace.csv"
    artifact.write_text("freq,s21\n6,-3\n", encoding="utf-8")

    entry = build_baseline_entry(
        project_id="project_a",
        round_id="round13",
        candidate_id="candidate_a",
        backend="ads_rfpro",
        label="ads_round13_rfpro",
        source_kind="ads_run",
        source_run_id="run1",
        metrics={"status": "TUNE", "s21_7g_db": "-3.0"},
        artifacts={"ads_trace": artifact},
        tags=["baseline"],
        producer="pytest",
    )

    artifact_entry = entry.artifacts[0]
    assert artifact_entry["type"] == "ads_trace"
    assert artifact_entry["exists"] is True
    assert artifact_entry["hash"]
    assert entry.frozen is True
    assert entry.immutable is True


def test_write_baseline_index_creates_lock_and_is_idempotent(tmp_path: Path) -> None:
    artifact = tmp_path / "trace.csv"
    artifact.write_text("freq,s21\n6,-3\n", encoding="utf-8")
    entry = build_baseline_entry(
        project_id="project_a",
        round_id="round13",
        candidate_id="candidate_a",
        backend="ads_rfpro",
        label="ads_round13_rfpro",
        source_kind="ads_run",
        source_run_id="run1",
        metrics={"status": "TUNE"},
        artifacts={"ads_trace": artifact},
    )
    index = build_baseline_index(project_id="project_a", entries=[entry])
    index_path = tmp_path / "baselines" / "baseline_index.json"

    write_baseline_index(index_path, index)
    first = json.loads(index_path.read_text(encoding="utf-8"))
    mutated_metadata = {**index, "created_at": "2099-01-01T00:00:00+00:00"}
    write_baseline_index(index_path, mutated_metadata)

    assert (index_path.parent / FREEZE_LOCK_NAME).exists()
    assert read_baseline_index(index_path) == first


def test_write_baseline_index_refuses_artifact_hash_mutation(tmp_path: Path) -> None:
    artifact = tmp_path / "trace.csv"
    artifact.write_text("freq,s21\n6,-3\n", encoding="utf-8")

    def make_index() -> dict:
        entry = build_baseline_entry(
            project_id="project_a",
            round_id="round13",
            candidate_id="candidate_a",
            backend="ads_rfpro",
            label="ads_round13_rfpro",
            source_kind="ads_run",
            source_run_id="run1",
            metrics={"status": "TUNE"},
            artifacts={"ads_trace": artifact},
        )
        return build_baseline_index(project_id="project_a", entries=[entry])

    index_path = tmp_path / "baselines" / "baseline_index.json"
    write_baseline_index(index_path, make_index())
    artifact.write_text("freq,s21\n6,-9\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="baseline artifact hashes changed"):
        write_baseline_index(index_path, make_index())


def test_validate_baseline_index_catches_hash_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "trace.csv"
    artifact.write_text("freq,s21\n6,-3\n", encoding="utf-8")
    entry = build_baseline_entry(
        project_id="project_a",
        round_id="round13",
        candidate_id="candidate_a",
        backend="ads_rfpro",
        label="ads_round13_rfpro",
        source_kind="ads_run",
        source_run_id="run1",
        metrics={"status": "TUNE"},
        artifacts={"ads_trace": artifact},
    )
    index_path = tmp_path / "baseline_index.json"
    write_baseline_index(index_path, build_baseline_index(project_id="project_a", entries=[entry]))

    artifact.write_text("freq,s21\n6,-9\n", encoding="utf-8")

    errors = validate_baseline_index(index_path)
    assert len(errors) == 1
    assert "hash mismatch" in errors[0]


def test_write_baseline_summary_csv(tmp_path: Path) -> None:
    artifact = tmp_path / "trace.csv"
    artifact.write_text("freq,s21\n7,-3\n", encoding="utf-8")
    entry = build_baseline_entry(
        project_id="project_a",
        round_id="round13",
        candidate_id="candidate_a",
        backend="ads_rfpro",
        label="ads_round13_rfpro",
        source_kind="ads_run",
        source_run_id="run1",
        metrics={"status": "TUNE", "s21_7g_db": "-3.0"},
        artifacts={"ads_trace": artifact},
    )

    summary_path = write_baseline_summary_csv(
        tmp_path / "baseline_summary.csv",
        build_baseline_index(project_id="project_a", entries=[entry]),
    )

    text = summary_path.read_text(encoding="utf-8")
    assert "baseline_id,backend,label" in text
    assert "-3.0" in text
