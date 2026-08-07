"""Unified scoring interface for filter and connector S-parameter results."""

from __future__ import annotations

from pathlib import Path

from . import score_vectors
from .connector import ConnectorScoreProfile, read_s2p, read_s2p_db, score_s2p
from .profiles import ScoringProfile, load_scoring_profile
from .sp8t import Sp8tFourPortScoreProfile, score_touchstone as score_sp8t_touchstone


def _connector_profile(profile: ScoringProfile) -> ConnectorScoreProfile:
    return ConnectorScoreProfile.from_config(profile.data)


def _sp8t_profile(profile: ScoringProfile) -> Sp8tFourPortScoreProfile:
    return Sp8tFourPortScoreProfile.from_config(profile.data)


def _score_filter_s2p(path: Path, profile: ScoringProfile) -> dict[str, str]:
    samples = read_s2p_db(path)
    if not samples:
        raise ValueError(f"no S-parameter samples found in {path}")
    freq = [row[0] for row in samples]
    traces = {
        "s11": [row[1] for row in samples],
        "s21": [row[2] for row in samples],
        "s12": [row[3] for row in samples],
        "s22": [row[4] for row in samples],
    }
    targets = profile.data.get("targets")
    if not isinstance(targets, dict):
        raise ValueError(f"filter scoring profile missing targets: {profile.path}")
    frequency = profile.data.get("frequency_ghz")
    if frequency is not None and not isinstance(frequency, dict):
        raise ValueError(f"filter scoring profile frequency_ghz must be an object: {profile.path}")
    row = score_vectors(
        freq,
        traces,
        str(path),
        {key: float(value) for key, value in targets.items()},
        profile.profile_id,
        {key: float(value) for key, value in frequency.items()} if isinstance(frequency, dict) else None,
    )
    row["score_version"] = profile.score_version
    row["scoring_system"] = profile.system
    row["scoring_profile_path"] = str(profile.path)
    return row


def score_sparameter_file(
    path: Path,
    *,
    system: str,
    profile_id: str,
    profile_path: Path | None = None,
    baseline_path: Path | None = None,
) -> dict[str, str]:
    profile = load_scoring_profile(system, profile_id, path=profile_path)
    if system == "filter":
        if baseline_path is not None:
            raise ValueError("filter scoring does not accept a baseline_path")
        return _score_filter_s2p(path, profile)
    if system == "connector":
        mode = profile.data.get("mode") if isinstance(profile.data.get("mode"), dict) else {}
        if mode.get("baseline_required") and baseline_path is None:
            raise ValueError(f"connector scoring profile requires --baseline-s2p: {profile.profile_id}")
        row = score_s2p(path, _connector_profile(profile), baseline_path=baseline_path)
        row["score_version"] = profile.score_version
        row["scoring_system"] = profile.system
        row["scoring_profile_path"] = str(profile.path)
        return row
    if system == "sp8t":
        row = score_sp8t_touchstone(path, _sp8t_profile(profile), baseline_path=baseline_path)
        row["score_version"] = profile.score_version
        row["scoring_system"] = profile.system
        row["scoring_profile_path"] = str(profile.path)
        return row
    raise ValueError(f"unknown scoring system: {system}")


def score_sparameter_files(
    paths: list[Path],
    *,
    system: str,
    profile_id: str,
    profile_path: Path | None = None,
    baseline_path: Path | None = None,
) -> list[dict[str, str]]:
    return [
        score_sparameter_file(
            path,
            system=system,
            profile_id=profile_id,
            profile_path=profile_path,
            baseline_path=baseline_path,
        )
        for path in paths
    ]


__all__ = ["score_sparameter_file", "score_sparameter_files"]
