"""Immutable baseline index helpers."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import artifact_entry, now_iso, safe_id, sha256_file, write_json

BASELINE_SCHEMA_VERSION = "1.0"
FREEZE_LOCK_NAME = ".baseline_freeze.lock"


@dataclass(frozen=True)
class BaselineEntry:
    baseline_id: str
    project_id: str
    round_id: str
    candidate_id: str
    backend: str
    label: str
    source_kind: str
    source_run_id: str | None = None
    metrics: dict[str, str] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    notes: str | None = None
    frozen: bool = True
    immutable: bool = True
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "project_id": self.project_id,
            "round_id": self.round_id,
            "candidate_id": self.candidate_id,
            "backend": self.backend,
            "label": self.label,
            "source_kind": self.source_kind,
            "source_run_id": self.source_run_id,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "tags": self.tags,
            "notes": self.notes,
            "frozen": self.frozen,
            "immutable": self.immutable,
            "created_at": self.created_at,
        }


def baseline_id(project_id: str, round_id: str, candidate_id: str, backend: str, label: str) -> str:
    return "_".join(safe_id(part) for part in [project_id, round_id, candidate_id, backend, label] if part)


def read_single_csv_row(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.DictReader(fp))
    if len(rows) != 1:
        raise ValueError(f"expected exactly one CSV row in {path}, got {len(rows)}")
    return rows[0]


def baseline_artifacts(paths: dict[str, Path | None], *, producer: str | None = None) -> list[dict[str, Any]]:
    return [artifact_entry(kind, path, producer=producer) for kind, path in paths.items()]


def build_baseline_entry(
    *,
    project_id: str,
    round_id: str,
    candidate_id: str,
    backend: str,
    label: str,
    source_kind: str,
    source_run_id: str | None,
    metrics: dict[str, str],
    artifacts: dict[str, Path | None],
    tags: list[str] | None = None,
    notes: str | None = None,
    producer: str | None = None,
) -> BaselineEntry:
    return BaselineEntry(
        baseline_id=baseline_id(project_id, round_id, candidate_id, backend, label),
        project_id=project_id,
        round_id=round_id,
        candidate_id=candidate_id,
        backend=backend,
        label=label,
        source_kind=source_kind,
        source_run_id=source_run_id,
        metrics=metrics,
        artifacts=baseline_artifacts(artifacts, producer=producer),
        tags=tags or [],
        notes=notes,
    )


def build_baseline_index(
    *,
    project_id: str,
    entries: list[BaselineEntry],
    policy: str = "immutable_artifact_hashes",
) -> dict[str, Any]:
    ids = [entry.baseline_id for entry in entries]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise ValueError(f"duplicate baseline ids: {duplicates}")
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "project_id": project_id,
        "policy": policy,
        "frozen": True,
        "immutable": True,
        "created_at": now_iso(),
        "entries": [entry.to_dict() for entry in entries],
    }


def read_baseline_index(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_fingerprint(entry: dict[str, Any]) -> dict[str, str | None]:
    return {str(item.get("type")): item.get("hash") for item in entry.get("artifacts", [])}


def assert_no_baseline_mutation(existing: dict[str, Any], new: dict[str, Any]) -> None:
    existing_entries = {entry["baseline_id"]: entry for entry in existing.get("entries", [])}
    for entry in new.get("entries", []):
        baseline = existing_entries.get(entry["baseline_id"])
        if baseline is None:
            continue
        old_fp = artifact_fingerprint(baseline)
        new_fp = artifact_fingerprint(entry)
        if old_fp != new_fp:
            raise RuntimeError(
                f"baseline artifact hashes changed for {entry['baseline_id']}; "
                "refusing to overwrite frozen baseline index"
            )


def write_baseline_index(path: Path, index: dict[str, Any], *, allow_update: bool = False) -> Path:
    if path.exists() and not allow_update:
        existing = read_baseline_index(path)
        assert_no_baseline_mutation(existing, index)
        lock = path.parent / FREEZE_LOCK_NAME
        if not lock.exists():
            lock.write_text(
                "SIMADS baseline directory is frozen. Do not overwrite artifacts referenced by baseline_index.json.\n",
                encoding="utf-8",
            )
        return path
    write_json(path, index)
    lock = path.parent / FREEZE_LOCK_NAME
    if not lock.exists():
        lock.write_text(
            "SIMADS baseline directory is frozen. Do not overwrite artifacts referenced by baseline_index.json.\n",
            encoding="utf-8",
        )
    return path


def validate_baseline_index(path: Path) -> list[str]:
    index = read_baseline_index(path)
    errors: list[str] = []
    for entry in index.get("entries", []):
        for artifact in entry.get("artifacts", []):
            artifact_path = artifact.get("path")
            if artifact_path is None:
                if artifact.get("exists"):
                    errors.append(f"{entry['baseline_id']}:{artifact.get('type')} has null path but exists=true")
                continue
            path_obj = Path(artifact_path)
            if not path_obj.exists():
                errors.append(f"{entry['baseline_id']}:{artifact.get('type')} missing: {artifact_path}")
                continue
            expected_hash = artifact.get("hash")
            actual_hash = sha256_file(path_obj)
            if expected_hash != actual_hash:
                errors.append(
                    f"{entry['baseline_id']}:{artifact.get('type')} hash mismatch: "
                    f"expected={expected_hash} actual={actual_hash}"
                )
    return errors


def write_baseline_summary_csv(path: Path, index: dict[str, Any]) -> Path:
    rows: list[dict[str, str]] = []
    for entry in index.get("entries", []):
        metrics = entry.get("metrics", {})
        rows.append(
            {
                "baseline_id": entry["baseline_id"],
                "backend": entry["backend"],
                "label": entry["label"],
                "candidate_id": entry["candidate_id"],
                "source_run_id": entry.get("source_run_id") or "",
                "status": metrics.get("status", ""),
                "s21_5g_db": metrics.get("s21_5g_db", ""),
                "s21_6g_db": metrics.get("s21_6g_db", ""),
                "s21_7g_db": metrics.get("s21_7g_db", ""),
                "s21_8g_db": metrics.get("s21_8g_db", ""),
                "s21_9g_db": metrics.get("s21_9g_db", ""),
                "passband_min_s21_db": metrics.get("passband_min_s21_db", ""),
                "passband_ripple_db": metrics.get("passband_ripple_db", ""),
                "worst_s11_6_8_db": metrics.get("worst_s11_6_8_db", ""),
                "worst_s22_6_8_db": metrics.get("worst_s22_6_8_db", ""),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]) if rows else ["baseline_id"])
        writer.writeheader()
        writer.writerows(rows)
    return path


__all__ = [
    "BaselineEntry",
    "assert_no_baseline_mutation",
    "baseline_artifacts",
    "baseline_id",
    "build_baseline_entry",
    "build_baseline_index",
    "read_baseline_index",
    "read_single_csv_row",
    "validate_baseline_index",
    "write_baseline_index",
    "write_baseline_summary_csv",
]
