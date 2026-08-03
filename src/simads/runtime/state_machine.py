"""Run state machine definitions for simulator automation flows."""

from __future__ import annotations

from dataclasses import dataclass

STATE_MACHINE_VERSION = "sim_run_state_machine_v2"

STAGES = (
    "planned",
    "layout_ready",
    "geometry_built",
    "ports_ready",
    "setup_ready",
    "results_exported",
    "ads_imported",
    "emsetup_ready",
    "rfpro_ready",
    "sim_running",
    "dataset_exported",
    "scored",
    "reported",
    "completed",
    "failed",
)

STATUSES = (
    "planned",
    "running",
    "completed",
    "failed",
    "skipped",
)

TERMINAL_STATUSES = ("completed", "failed", "skipped")

ERROR_CLASSES = (
    "ENV_ERROR",
    "PROFILE_ERROR",
    "DATA_ERROR",
    "LAYOUT_ERROR",
    "EMSETUP_ERROR",
    "RFPRO_ERROR",
    "SCORE_ERROR",
    "SAFETY_ERROR",
    "TIMEOUT",
    "SUBPROCESS_ERROR",
    "UNKNOWN_ERROR",
)

STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES)}

RESUME_STAGE_BY_FAILED_STEP = {
    "1. DXF import and P1/P2 pins": "ads_imported",
    "2. Clone/patch FEM setup": "emsetup_ready",
    "3. RFPro FEM": "sim_running",
    "4a. Export FEM fitted dataset TXT": "dataset_exported",
    "4. Score S-parameters": "scored",
    "run_ads_filter_candidate.py": "planned",
    "HFSS build geometry": "geometry_built",
    "HFSS create ports": "ports_ready",
    "HFSS setup sweep": "setup_ready",
    "HFSS solve": "sim_running",
    "HFSS export touchstone": "results_exported",
    "HFSS score S-parameters": "scored",
    "run_hfss3dlayout_filter_verdict.py": "planned",
}


@dataclass(frozen=True)
class StateValidation:
    ok: bool
    message: str


def validate_stage(stage: str) -> StateValidation:
    if stage in STAGES:
        return StateValidation(True, "")
    return StateValidation(False, f"unknown run stage: {stage!r}")


def validate_status(status: str) -> StateValidation:
    if status in STATUSES:
        return StateValidation(True, "")
    return StateValidation(False, f"unknown run status: {status!r}")


def validate_error_class(error_class: str | None) -> StateValidation:
    if error_class in (None, "") or error_class in ERROR_CLASSES:
        return StateValidation(True, "")
    return StateValidation(False, f"unknown error class: {error_class!r}")


def validate_state_fields(stage: str, status: str, error_class: str | None = None) -> None:
    for result in (validate_stage(stage), validate_status(status), validate_error_class(error_class)):
        if not result.ok:
            raise ValueError(result.message)


def is_terminal_status(status: str) -> bool:
    validate_status(status)
    return status in TERMINAL_STATUSES


def resume_stage_for_failed_step(failed_step: str | None) -> str:
    if not failed_step:
        return "planned"
    return RESUME_STAGE_BY_FAILED_STEP.get(failed_step, "planned")


__all__ = [
    "ERROR_CLASSES",
    "RESUME_STAGE_BY_FAILED_STEP",
    "STAGES",
    "STAGE_ORDER",
    "STATE_MACHINE_VERSION",
    "STATUSES",
    "TERMINAL_STATUSES",
    "StateValidation",
    "is_terminal_status",
    "resume_stage_for_failed_step",
    "validate_error_class",
    "validate_stage",
    "validate_state_fields",
    "validate_status",
]
