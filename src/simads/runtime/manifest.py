"""Manifest and run-state helpers for ADS automation runs."""

from __future__ import annotations

import hashlib
import json
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .state_machine import validate_state_fields


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_id(value: str) -> str:
    value = value.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def create_run_id(project_id: str, round_id: str, candidate_id: str, profile_id: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return "_".join(safe_id(part) for part in [project_id, round_id, candidate_id, profile_id, stamp] if part)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2, default=json_default)
        fp.write("\n")


def artifact_entry(kind: str, path: Path | None, *, producer: str | None = None) -> dict[str, Any]:
    if path is None:
        return {"type": kind, "path": None, "exists": False, "hash": None, "producer": producer}
    return {
        "type": kind,
        "path": str(path),
        "exists": path.exists(),
        "hash": sha256_file(path),
        "producer": producer,
    }


def write_state(
    path: Path,
    *,
    run_id: str,
    stage: str,
    status: str,
    candidate_id: str,
    profile_id: str,
    failed_step: str | None = None,
    error_class: str | None = None,
    message: str | None = None,
    elapsed_s: float | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    validate_state_fields(stage, status, error_class)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "candidate_id": candidate_id,
        "profile_id": profile_id,
        "stage": stage,
        "status": status,
        "failed_step": failed_step,
        "error_class": error_class,
        "message": message,
        "elapsed_s": round(elapsed_s, 3) if elapsed_s is not None else None,
        "updated_at": now_iso(),
    }
    if extra:
        payload["extra"] = extra
    write_json(path, payload)


def write_run_manifest(path: Path, payload: dict[str, Any]) -> None:
    stage = payload.get("stage")
    status = payload.get("status")
    error_class = payload.get("error_class")
    if isinstance(stage, str) and isinstance(status, str):
        validate_state_fields(stage, status, error_class if isinstance(error_class, str) else None)
    payload = {"schema_version": "1.0", **payload, "updated_at": now_iso()}
    write_json(path, payload)


def write_artifact_manifest(path: Path, *, run_id: str, artifacts: list[dict[str, Any]]) -> None:
    write_json(
        path,
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "artifacts": artifacts,
            "updated_at": now_iso(),
        },
    )


def classify_exception(exc: BaseException) -> str:
    name = exc.__class__.__name__
    text = str(exc).lower()
    if isinstance(exc, FileNotFoundError):
        if "python" in text or "hpeesof" in text:
            return "ENV_ERROR"
        if "workspace" in text or "library" in text or "template" in text or "substrate" in text:
            return "PROFILE_ERROR"
        return "DATA_ERROR"
    if "timeout" in text:
        return "TIMEOUT"
    if "dxf" in text or "layout" in text or "port" in text:
        return "LAYOUT_ERROR"
    if "rfpro" in text or "fem" in text:
        return "RFPRO_ERROR"
    if "score" in text or "target profile" in text:
        return "SCORE_ERROR"
    if "safety" in name.lower() or "refused" in text or "protected" in text:
        return "SAFETY_ERROR"
    if name == "CalledProcessError":
        return "SUBPROCESS_ERROR"
    return "UNKNOWN_ERROR"


def exception_summary(exc: BaseException) -> dict[str, str]:
    return {
        "type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": "".join(traceback.format_exception(exc)).strip(),
    }
