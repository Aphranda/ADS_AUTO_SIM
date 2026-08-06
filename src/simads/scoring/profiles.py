"""Config-backed scoring profile loading."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


SCORING_SYSTEM_DIRS = {
    "filter": "filters",
    "connector": "connectors",
}


@dataclass(frozen=True)
class ScoringProfile:
    system: str
    profile_id: str
    score_version: str
    data: dict[str, Any]
    path: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_scoring_profile_path(system: str, profile_id: str, *, root: Path | None = None) -> Path:
    try:
        system_dir = SCORING_SYSTEM_DIRS[system]
    except KeyError as exc:
        raise ValueError(f"unknown scoring system: {system}") from exc
    return (root or repo_root()) / "config" / "scoring" / system_dir / f"{profile_id}.json"


def load_scoring_profile(
    system: str,
    profile_id: str,
    *,
    root: Path | None = None,
    path: Path | None = None,
) -> ScoringProfile:
    config_path = path or default_scoring_profile_path(system, profile_id, root=root)
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"scoring profile must be a JSON object: {config_path}")
    actual_system = str(data.get("scoring_system", system))
    actual_profile_id = str(data.get("profile_id", profile_id))
    if actual_system != system:
        raise ValueError(f"scoring profile system mismatch: expected {system}, got {actual_system}")
    if actual_profile_id != profile_id:
        raise ValueError(f"scoring profile id mismatch: expected {profile_id}, got {actual_profile_id}")
    score_version = str(data.get("score_version", ""))
    if not score_version:
        raise ValueError(f"scoring profile missing score_version: {config_path}")
    return ScoringProfile(
        system=actual_system,
        profile_id=actual_profile_id,
        score_version=score_version,
        data=data,
        path=config_path,
    )


def as_float(mapping: dict[str, Any], key: str, default: float) -> float:
    value = mapping.get(key, default)
    return default if value is None else float(value)


def nested_float(data: dict[str, Any], section: str, key: str, default: float) -> float:
    value = data.get(section)
    if not isinstance(value, dict):
        return default
    return as_float(value, key, default)


__all__ = [
    "SCORING_SYSTEM_DIRS",
    "ScoringProfile",
    "as_float",
    "default_scoring_profile_path",
    "load_scoring_profile",
    "nested_float",
    "repo_root",
]
