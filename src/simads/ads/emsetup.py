"""EM setup clone planning helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from simads.ads.workspace import AdsCellRef, AdsCommandPlan
from simads.config import AdsProfile

DEFAULT_SETUP_VIEW = "em%Setup"


@dataclass(frozen=True)
class EmSetupClonePlan:
    profile_id: str
    template: AdsCellRef
    target: AdsCellRef
    params_path: Path | None = None
    substrate_library: str | None = None
    start_ghz: float = 4.0
    stop_ghz: float = 10.0
    points_text: str = "121"
    overwrite: bool = True
    force: bool = False

    def to_manifest(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "workspace": str(self.target.workspace),
            "library": self.target.library,
            "template_cell": self.template.cell,
            "target_cell": self.target.cell,
            "setup_view": self.target.view,
            "params_path": str(self.params_path) if self.params_path else None,
            "substrate_library": self.substrate_library,
            "start_ghz": self.start_ghz,
            "stop_ghz": self.stop_ghz,
            "points_text": self.points_text,
            "overwrite": self.overwrite,
            "force": self.force,
        }


def build_emsetup_clone_plan(
    profile: AdsProfile,
    *,
    target_cell: str,
    template_cell: str | None = None,
    setup_view: str | None = None,
    params_path: Path | None = None,
    start_ghz: float = 4.0,
    stop_ghz: float = 10.0,
    points_text: str = "121",
    overwrite: bool = True,
    force: bool = False,
) -> EmSetupClonePlan:
    view = setup_view or profile.setup_view or DEFAULT_SETUP_VIEW
    return EmSetupClonePlan(
        profile_id=profile.name,
        template=AdsCellRef(profile.workspace, profile.library, template_cell or profile.template_cell, view),
        target=AdsCellRef(profile.workspace, profile.library, target_cell, view),
        params_path=params_path,
        substrate_library=profile.substrate_library,
        start_ghz=start_ghz,
        stop_ghz=stop_ghz,
        points_text=points_text,
        overwrite=overwrite,
        force=force,
    )


def build_clone_command(
    plan: EmSetupClonePlan,
    *,
    ads_python: Path,
    script: Path,
) -> AdsCommandPlan:
    args = [
        "--workspace",
        str(plan.target.workspace),
        "--library",
        plan.target.library,
        "--template-cell",
        plan.template.cell,
        "--target-cell",
        plan.target.cell,
        "--setup-view",
        plan.target.view,
        "--start-ghz",
        f"{plan.start_ghz:g}",
        "--stop-ghz",
        f"{plan.stop_ghz:g}",
        "--points-text",
        plan.points_text,
    ]
    if plan.params_path:
        args.extend(["--params", str(plan.params_path)])
    if plan.substrate_library:
        args.extend(["--substrate-library", plan.substrate_library])
    if plan.overwrite:
        args.append("--overwrite")
    if plan.force:
        args.append("--force")
    return AdsCommandPlan("ads_clone_emsetup_template", ads_python, script, tuple(args), cwd=script.parents[1])
