"""HFSS project path and action planning helpers."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simads.hfss_contracts import (
    HFSS_PROJECT_ACTION_ADD,
    HFSS_PROJECT_ACTIONS,
    HFSS_PROJECT_MODEL_PER_DESIGN,
    HFSS_PROJECT_MODEL_SINGLE_AEDT,
    HFSS_PROJECT_MODELS,
)
from simads.hfss.layout_io import configured_layout_id


@dataclass(frozen=True)
class HfssProjectPlan:
    project_path: Path
    design: str
    project_model: str
    project_action: str
    reuse_project: bool
    init_project: str | None

    @property
    def lock_project(self) -> str | None:
        return self.init_project

    def ensure_directories(self, out_dir: Path) -> None:
        self.project_path.parent.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

    def to_contract(self) -> dict[str, Any]:
        return {
            "project_model": self.project_model,
            "project_action": self.project_action,
            "reuse_project": self.reuse_project,
            "project": str(self.project_path),
            "design": self.design,
            "init_project": self.init_project,
        }


def default_project_name(layout: dict[str, Any]) -> str:
    return f"{configured_layout_id(layout)}_hfss_verdict"


def resolve_project_path(args: argparse.Namespace, layout: dict[str, Any]) -> Path:
    if args.project:
        return Path(args.project)
    project_name = args.project_name or default_project_name(layout)
    return Path(args.workspace_dir) / f"{project_name}.aedt"


def resolve_hfss_project_plan(args: argparse.Namespace, layout: dict[str, Any]) -> HfssProjectPlan:
    project_model = str(getattr(args, "project_model", HFSS_PROJECT_MODEL_PER_DESIGN))
    project_action = str(getattr(args, "project_action", "new"))
    if project_model not in HFSS_PROJECT_MODELS:
        raise ValueError(f"unsupported HFSS project model: {project_model}")
    if project_action not in HFSS_PROJECT_ACTIONS:
        raise ValueError(f"unsupported HFSS project action: {project_action}")
    if project_action == HFSS_PROJECT_ACTION_ADD and getattr(args, "project", None) is None and getattr(args, "project_name", None) is None:
        raise ValueError("--project-action add requires --project or --project-name to identify the project space")

    project_path = resolve_project_path(args, layout)
    reuse_project = bool(getattr(args, "reuse_project", False) or project_action == HFSS_PROJECT_ACTION_ADD)
    init_project = str(project_path) if reuse_project and project_path.exists() else None
    return HfssProjectPlan(
        project_path=project_path,
        design=str(getattr(args, "design", "HFSSDesign")),
        project_model=project_model,
        project_action=project_action,
        reuse_project=reuse_project,
        init_project=init_project,
    )


__all__ = [
    "HFSS_PROJECT_ACTION_ADD",
    "HFSS_PROJECT_ACTIONS",
    "HFSS_PROJECT_MODEL_PER_DESIGN",
    "HFSS_PROJECT_MODEL_SINGLE_AEDT",
    "HFSS_PROJECT_MODELS",
    "HfssProjectPlan",
    "default_project_name",
    "resolve_hfss_project_plan",
    "resolve_project_path",
]
