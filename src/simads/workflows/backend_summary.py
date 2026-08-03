"""Build backend-neutral summaries from run manifests."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SUMMARY_FIELDS = [
    "candidate",
    "backend",
    "simulator",
    "run_id",
    "status",
    "stage",
    "profile_id",
    "pipeline_id",
    "project_id",
    "round_id",
    "score_path",
    "trace_path",
    "s2p_path",
    "run_dir",
    "elapsed_s",
    "error_class",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def backend_from_manifest(manifest: dict[str, Any]) -> str:
    simulator = str(manifest.get("simulator") or "")
    if simulator == "hfss3dlayout":
        return "hfss3dlayout"
    profile_snapshot = manifest.get("profile_snapshot")
    if isinstance(profile_snapshot, dict) and profile_snapshot.get("right_backend") == "hfss":
        return "compare"
    return "ads_rfpro"


def output_path(manifest: dict[str, Any], *keys: str) -> str:
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        return ""
    for key in keys:
        value = outputs.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def row_from_run_dir(run_dir: Path) -> dict[str, str] | None:
    manifest = read_json(run_dir / "run_manifest.json")
    if not manifest:
        return None
    state = read_json(run_dir / "state.json")
    return {
        "candidate": str(manifest.get("candidate_id") or state.get("candidate_id") or ""),
        "backend": backend_from_manifest(manifest),
        "simulator": str(manifest.get("simulator") or ""),
        "run_id": str(manifest.get("run_id") or state.get("run_id") or run_dir.name),
        "status": str(manifest.get("status") or state.get("status") or ""),
        "stage": str(manifest.get("stage") or state.get("stage") or ""),
        "profile_id": str(manifest.get("profile_id") or state.get("profile_id") or ""),
        "pipeline_id": str(manifest.get("pipeline_id") or ""),
        "project_id": str(manifest.get("project_id") or ""),
        "round_id": str(manifest.get("round_id") or ""),
        "score_path": output_path(manifest, "score_csv", "score", "summary_csv"),
        "trace_path": output_path(manifest, "trace_csv", "compare_csv"),
        "s2p_path": output_path(manifest, "s2p"),
        "run_dir": str(run_dir),
        "elapsed_s": str(manifest.get("elapsed_s") or state.get("elapsed_s") or ""),
        "error_class": str(manifest.get("error_class") or state.get("error_class") or ""),
    }


def discover_run_dirs(paths: list[Path]) -> list[Path]:
    run_dirs: list[Path] = []
    for path in paths:
        if (path / "run_manifest.json").exists():
            run_dirs.append(path)
            continue
        if path.exists():
            run_dirs.extend(sorted(item.parent for item in path.rglob("run_manifest.json")))
    return sorted(dict.fromkeys(run_dirs))


def build_backend_summary(paths: list[Path]) -> list[dict[str, str]]:
    rows = [row for run_dir in discover_run_dirs(paths) if (row := row_from_run_dir(run_dir)) is not None]
    return sorted(rows, key=lambda row: (row["candidate"], row["backend"], row["run_id"]))


def write_backend_summary(path: Path, rows: list[dict[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


__all__ = [
    "SUMMARY_FIELDS",
    "backend_from_manifest",
    "build_backend_summary",
    "discover_run_dirs",
    "row_from_run_dir",
    "write_backend_summary",
]
