from argparse import Namespace
from pathlib import Path

import pytest

from simads.hfss.project import default_project_name, resolve_hfss_project_plan, resolve_project_path


def _args(tmp_path: Path, **overrides) -> Namespace:
    data = {
        "workspace_dir": tmp_path / "workspace",
        "project": None,
        "project_name": None,
        "project_model": "per_design_project",
        "project_action": "new",
        "reuse_project": False,
        "design": "HFSS_UNIT",
    }
    data.update(overrides)
    return Namespace(**data)


def _layout() -> dict:
    return {"layout_id": "unit_layout", "metadata": {}, "ports": [], "shapes": []}


def test_project_plan_defaults_to_new_layout_named_project(tmp_path: Path) -> None:
    args = _args(tmp_path)

    plan = resolve_hfss_project_plan(args, _layout())

    assert default_project_name(_layout()) == "unit_layout_hfss_verdict"
    assert resolve_project_path(args, _layout()) == tmp_path / "workspace" / "unit_layout_hfss_verdict.aedt"
    assert plan.project_path == tmp_path / "workspace" / "unit_layout_hfss_verdict.aedt"
    assert plan.design == "HFSS_UNIT"
    assert plan.reuse_project is False
    assert plan.init_project is None
    assert plan.lock_project is None
    assert plan.to_contract()["init_project"] is None


def test_project_plan_reuses_existing_project_when_requested(tmp_path: Path) -> None:
    project = tmp_path / "workspace" / "shared.aedt"
    project.parent.mkdir(parents=True)
    project.write_text("placeholder", encoding="utf-8")
    args = _args(tmp_path, project=project, reuse_project=True)

    plan = resolve_hfss_project_plan(args, _layout())

    assert plan.project_path == project
    assert plan.reuse_project is True
    assert plan.init_project == str(project)
    assert plan.lock_project == str(project)


def test_explicit_relative_project_path_is_resolved_for_aedt_save(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    relative = Path("projects") / "filter.aedt"
    args = _args(tmp_path, project=relative, project_action="add")

    plan = resolve_hfss_project_plan(args, _layout())

    assert plan.project_path == (tmp_path / relative).resolve()
    assert plan.project_path.is_absolute()


def test_project_plan_requires_explicit_project_for_add_action(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="--project-action add"):
        resolve_hfss_project_plan(_args(tmp_path, project_action="add"), _layout())

    args = _args(tmp_path, project_action="add", project_name="shared_connector")
    plan = resolve_hfss_project_plan(args, _layout())

    assert plan.project_path == tmp_path / "workspace" / "shared_connector.aedt"
    assert plan.reuse_project is True
    assert plan.init_project is None
