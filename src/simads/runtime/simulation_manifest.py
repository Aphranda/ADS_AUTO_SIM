"""Build manifest payloads for simulator workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from simads.domain import SimulationResultSpec, StackupSpec, SweepSpec

from .manifest import artifact_entry, create_run_id, write_artifact_manifest, write_run_manifest, write_state


@dataclass(frozen=True)
class SimulationRunContext:
    project_id: str
    round_id: str
    candidate_id: str
    profile_id: str
    simulator: str
    run_id: str | None = None
    run_dir: Path | None = None
    device_id: str | None = None
    pipeline_id: str | None = None
    pipeline_snapshot: dict[str, Any] | None = None
    profile_snapshot: dict[str, Any] | None = None

    def resolved_run_id(self) -> str:
        return self.run_id or create_run_id(self.project_id, self.round_id, self.candidate_id, self.profile_id)

    def resolved_run_dir(self, repo_root: Path, run_id: str | None = None) -> Path:
        rid = run_id or self.resolved_run_id()
        return self.run_dir or repo_root / "projects" / self.project_id / "runs" / rid


@dataclass(frozen=True)
class SimulationManifestPayload:
    context: SimulationRunContext
    sweep: SweepSpec
    stackup: StackupSpec | None = None
    inputs: dict[str, str | None] = field(default_factory=dict)
    outputs: dict[str, str | None] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)
    result: SimulationResultSpec | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def build_run_manifest(
        self,
        *,
        run_id: str,
        status: str,
        stage: str,
        error_class: str | None = None,
        elapsed_s: float | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "run_id": run_id,
            "project_id": self.context.project_id,
            "round_id": self.context.round_id,
            "candidate_id": self.context.candidate_id,
            "device_id": self.context.device_id,
            "pipeline_id": self.context.pipeline_id,
            "pipeline_snapshot": self.context.pipeline_snapshot,
            "profile_id": self.context.profile_id,
            "profile_snapshot": self.context.profile_snapshot or {},
            "simulator": self.context.simulator,
            "sweep": self.sweep.to_dict(),
            "stackup": self.stackup.to_dict() if self.stackup else None,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "flags": self.flags,
            "result": self.result.to_dict() if self.result else None,
            "status": status,
            "stage": stage,
            "error_class": error_class,
        }
        if elapsed_s is not None:
            payload["elapsed_s"] = round(elapsed_s, 3)
        if self.extra:
            payload["extra"] = self.extra
        return payload


def build_simulation_artifacts(
    *,
    layout_json: Path | None = None,
    project_file: Path | None = None,
    s2p: Path | None = None,
    trace_csv: Path | None = None,
    score_csv: Path | None = None,
    svg: Path | None = None,
    summary_csv: Path | None = None,
    log_file: Path | None = None,
    state: Path | None = None,
    producer: str | None = None,
    extra: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    artifacts = [
        artifact_entry("layout_json", layout_json, producer=producer),
        artifact_entry("project_file", project_file, producer=producer),
        artifact_entry("s2p", s2p, producer=producer),
        artifact_entry("trace_csv", trace_csv, producer=producer),
        artifact_entry("score", score_csv, producer=producer),
        artifact_entry("svg", svg, producer=producer),
        artifact_entry("summary", summary_csv, producer=producer),
        artifact_entry("log", log_file, producer=producer),
        artifact_entry("state", state, producer=producer),
    ]
    if extra:
        artifacts.extend(extra)
    return artifacts


def write_simulation_manifests(
    *,
    run_dir: Path,
    run_id: str,
    payload: SimulationManifestPayload,
    artifacts: list[dict[str, Any]],
    status: str,
    stage: str,
    error_class: str | None = None,
    elapsed_s: float | None = None,
    message: str | None = None,
) -> dict[str, Path]:
    state_path = run_dir / "state.json"
    run_manifest_path = run_dir / "run_manifest.json"
    artifact_manifest_path = run_dir / "artifact_manifest.json"
    write_state(
        state_path,
        run_id=run_id,
        stage=stage,
        status=status,
        candidate_id=payload.context.candidate_id,
        profile_id=payload.context.profile_id,
        error_class=error_class,
        message=message,
        elapsed_s=elapsed_s,
    )
    refreshed_artifacts = [
        artifact_entry("state", state_path, producer=item.get("producer"))
        if item.get("type") == "state" and item.get("path") == str(state_path)
        else item
        for item in artifacts
    ]
    write_artifact_manifest(artifact_manifest_path, run_id=run_id, artifacts=refreshed_artifacts)
    run_manifest = payload.build_run_manifest(
        run_id=run_id,
        status=status,
        stage=stage,
        error_class=error_class,
        elapsed_s=elapsed_s,
    )
    run_manifest.setdefault("outputs", {})
    run_manifest["outputs"] = {
        **run_manifest["outputs"],
        "state": str(state_path),
        "artifact_manifest": str(artifact_manifest_path),
    }
    write_run_manifest(run_manifest_path, run_manifest)
    return {
        "state": state_path,
        "run_manifest": run_manifest_path,
        "artifact_manifest": artifact_manifest_path,
    }


__all__ = [
    "SimulationManifestPayload",
    "SimulationRunContext",
    "build_simulation_artifacts",
    "write_simulation_manifests",
]
