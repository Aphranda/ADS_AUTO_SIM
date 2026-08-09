"""Standard names for HFSS JSON and JSONL artifacts."""

from __future__ import annotations

from pathlib import Path
from pathlib import PurePosixPath
import re


TRACKED_JSON_KINDS = frozenset(
    {
        "layout",
        "params",
        "summary",
        "metrics",
        "manifest",
        "comparison",
        "score_summary",
    }
)

LOCAL_RUNTIME_JSON_KINDS = frozenset(
    {
        "run_log",
        "dry_run_log",
        "execute_log",
        "operation_log",
        "owner",
        "diagnostic",
        "inspect",
        "probe",
        "api_extract_raw",
    }
)

JSON_KIND_SUFFIXES = {
    "layout": "_layout.json",
    "params": "_params.json",
    "summary": "_summary.json",
    "metrics": "_metrics.json",
    "manifest": "_manifest.json",
    "comparison": "_comparison.json",
    "score_summary": "_score_summary.json",
    "run_log": "_run_log.json",
    "dry_run_log": "_dry_run_log.json",
    "execute_log": "_execute_log.json",
    "operation_log": "_operation_log.json",
    "owner": "_owner.json",
    "diagnostic": "_diagnostic.json",
    "inspect": "_inspect.json",
    "probe": "_probe.json",
    "api_extract_raw": "_api_extract_raw.json",
}

FIXED_TRACKED_JSON_NAMES = frozenset(
    {
        "artifact_manifest.json",
        "baseline_index.json",
        "baseline_manifest.json",
        "run_manifest.json",
        "simulation_manifest.json",
        "state.json",
    }
)

LOCAL_RUNTIME_JSON_SUFFIXES = tuple(
    JSON_KIND_SUFFIXES[kind] for kind in sorted(LOCAL_RUNTIME_JSON_KINDS)
)

TRACKED_JSON_SUFFIXES = tuple(JSON_KIND_SUFFIXES[kind] for kind in sorted(TRACKED_JSON_KINDS))


def normalize_artifact_stem(stem: str) -> str:
    """Return a filesystem-friendly snake_case artifact stem."""

    normalized = re.sub(r"[^A-Za-z0-9]+", "_", str(stem)).strip("_").lower()
    return re.sub(r"_+", "_", normalized) or "artifact"


def json_artifact_name(stem: str, kind: str) -> str:
    """Build a JSON filename with a registered semantic suffix."""

    try:
        suffix = JSON_KIND_SUFFIXES[kind]
    except KeyError as exc:
        choices = ", ".join(sorted(JSON_KIND_SUFFIXES))
        raise ValueError(f"unknown JSON artifact kind {kind!r}; expected one of: {choices}") from exc
    return f"{normalize_artifact_stem(stem)}{suffix}"


def json_artifact_path(directory: str | Path, stem: str, kind: str) -> Path:
    """Build a JSON artifact path in ``directory``."""

    return Path(directory) / json_artifact_name(stem, kind)


def event_log_path_for_json(output: str | Path) -> Path:
    """Return the local JSONL lifecycle stream path next to a JSON output.

    JSON artifact classification is based on the ``*.json`` filename suffixes
    above. This sidecar is only an append-friendly local event stream and is
    always ignored by Git.
    """

    path = Path(output)
    stem = path.stem if path.suffix.lower() == ".json" else path.name
    for suffix in LOCAL_RUNTIME_JSON_SUFFIXES:
        suffix_stem = suffix.removesuffix(".json")
        if stem.endswith(suffix_stem):
            stem = stem[: -len(suffix_stem)] or stem
            break
    return path.with_name(f"{stem}_events.jsonl")


def is_local_runtime_json_name(name: str | Path) -> bool:
    """Classify JSON names that should stay local and be ignored by Git."""

    filename = Path(name).name.lower()
    if not filename.endswith(".json"):
        return False
    if filename.startswith("inspect_"):
        return True
    if filename == "extract_layout.json":
        return True
    return filename.endswith(LOCAL_RUNTIME_JSON_SUFFIXES) or "dry_run" in filename or "execute" in filename


def is_trackable_json_name(name: str | Path) -> bool:
    """Classify JSON names that can be tracked when the directory is curated."""

    filename = Path(name).name.lower()
    if filename in FIXED_TRACKED_JSON_NAMES:
        return True
    return filename.endswith(TRACKED_JSON_SUFFIXES)


def _artifact_parts(path: str | Path) -> tuple[str, ...]:
    return PurePosixPath(str(path).replace("\\", "/")).parts


def _has_part(path: str | Path, name: str) -> bool:
    return name in _artifact_parts(path)


def is_runtime_artifact_path(path: str | Path) -> bool:
    """Return true for local runtime JSON/JSONL paths, using directory context."""

    parts = _artifact_parts(path)
    filename = parts[-1].lower() if parts else str(path).lower()
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix == ".jsonl":
        return True
    if ".simads" in parts:
        return True
    if not filename.endswith(".json"):
        return False
    if "config" in parts:
        return False
    if is_trackable_json_name(filename):
        return False

    stem = filename.removesuffix(".json")
    in_runtime_tree = (
        ("projects" in parts and any(part in {"reports", "results", "runs"} for part in parts))
        or ("projects" in parts and "simulations" in parts)
        or ("archive" in parts and "results" in parts)
    )
    if not in_runtime_tree:
        return is_local_runtime_json_name(filename)
    if is_local_runtime_json_name(filename):
        return True
    if stem in {"run", "export_only"}:
        return True
    if stem.startswith(("run_", "replace_", "inspect_", "export_only_")):
        return True
    if any(token in stem for token in ("_dry_run", "_execute", "_nosave", "_probe", "_diag")):
        return True
    if stem.endswith(("_hints", "_inspect", "_probe", "_diagnosis")):
        return True
    return False


def json_artifact_class(path: str | Path) -> str:
    """Classify an artifact path for Git tracking decisions."""

    parts = _artifact_parts(path)
    filename = parts[-1].lower() if parts else str(path).lower()
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix == ".jsonl":
        return "local_runtime_event_stream"
    if suffix != ".json":
        return "other"
    if is_runtime_artifact_path(path):
        return "local_runtime_json"
    if "config" in parts:
        return "trackable_config_json"
    if is_trackable_json_name(filename):
        return "trackable_json"
    return "legacy_or_unclear_json"


__all__ = [
    "FIXED_TRACKED_JSON_NAMES",
    "JSON_KIND_SUFFIXES",
    "LOCAL_RUNTIME_JSON_KINDS",
    "LOCAL_RUNTIME_JSON_SUFFIXES",
    "TRACKED_JSON_KINDS",
    "TRACKED_JSON_SUFFIXES",
    "event_log_path_for_json",
    "is_local_runtime_json_name",
    "is_runtime_artifact_path",
    "is_trackable_json_name",
    "json_artifact_class",
    "json_artifact_name",
    "json_artifact_path",
    "normalize_artifact_stem",
]
