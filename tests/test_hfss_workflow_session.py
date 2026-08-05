from __future__ import annotations

from argparse import Namespace
from contextlib import contextmanager
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from simads.hfss import workflow


def _args(tmp_path: Path, layout_path: Path) -> Namespace:
    return Namespace(
        layout=layout_path,
        out_dir=tmp_path / "out",
        workspace_dir=tmp_path / "workspace",
        project=None,
        project_name="unit_case",
        project_model="per_design_project",
        project_action="new",
        reuse_project=False,
        design="HFSS_UNIT",
        version="2026.1",
        route="custom",
        stackup_config=None,
        non_graphical=True,
        keep_open=False,
        setup="Setup1",
        sweep="Sweep1",
        patch_edb_port_properties=False,
        port_type="aedt-edge",
        skip_ports=True,
        build_only=True,
    )


def test_run_hfss_primary_lifecycle_uses_session_opener(tmp_path: Path, monkeypatch) -> None:
    layout_path = tmp_path / "unit_layout.json"
    layout_path.write_text(json.dumps({"layout_id": "unit_layout", "metadata": {}, "ports": [], "shapes": []}), encoding="utf-8")
    app_releases: list[dict[str, Any]] = []
    session_calls: list[dict[str, Any]] = []

    class FakeApp:
        def release_desktop(self, **kwargs):
            app_releases.append(kwargs)

    fake_app = FakeApp()

    class FakeSession:
        app = fake_app
        startup = {"settings": "snapshot"}
        aedt_lock = {"label": "simads.hfss.workflow.run_hfss"}
        project_lock = {"action": "not_applicable"}
        aedt_reaper = {"label": "primary"}
        aedt_ready = {"ready": True}

        def mark_desktop_released(self):
            raise AssertionError("normal build-only path should not manually release primary desktop")

    @contextmanager
    def fake_session_opener(config, lifecycle, *, app_factory, settings_obj):
        session_calls.append(
            {
                "project": config.project,
                "design": config.design,
                "version": config.version,
                "non_graphical": config.non_graphical,
                "new_desktop": config.new_desktop,
                "keep_open": config.keep_open,
                "ready_setup": config.ready_setup,
                "ready_sweep": config.ready_sweep,
                "app_factory": app_factory,
                "settings_obj": settings_obj,
                "lifecycle_label": lifecycle.label,
            }
        )
        yield FakeSession()

    def fake_build(app, layout, args, *, project_path, stackup_config):
        assert app is fake_app
        assert layout["layout_id"] == "unit_layout"
        assert project_path == tmp_path / "workspace" / "unit_case.aedt"
        assert stackup_config is None
        return SimpleNamespace(
            to_dict=lambda: {
                "project": str(project_path),
                "design": args.design,
                "geometry_count": 0,
                "ports": [],
                "build_only": True,
                "saved": True,
            }
        )

    monkeypatch.setattr(workflow, "build_hfss_layout_project", fake_build)

    settings = object()
    runtime = workflow.HfssWorkflowRuntime(
        app_factory=FakeApp,
        settings=settings,
        session_opener=fake_session_opener,
    )

    result = workflow._run_hfss_with_runtime(_args(tmp_path, layout_path), runtime)

    assert session_calls == [
        {
            "project": None,
            "design": "HFSS_UNIT",
            "version": "2026.1",
            "non_graphical": True,
            "new_desktop": True,
            "keep_open": False,
            "ready_setup": "Setup1",
            "ready_sweep": "Sweep1",
            "app_factory": FakeApp,
            "settings_obj": settings,
            "lifecycle_label": "simads.hfss.workflow.run_hfss",
        }
    ]
    assert result["aedt_startup"] == {"settings": "snapshot"}
    assert result["aedt_lock"] == {"label": "simads.hfss.workflow.run_hfss"}
    assert result["project_lock"] == {"action": "not_applicable"}
    assert result["aedt_reapers"] == [{"label": "primary"}]
    assert result["aedt_ready"] == {"ready": True}
    assert app_releases == []


def test_run_hfss_edb_patch_marks_primary_released_and_releases_reopened_app(tmp_path: Path, monkeypatch) -> None:
    layout_path = tmp_path / "unit_layout.json"
    layout_path.write_text(json.dumps({"layout_id": "unit_layout", "metadata": {}, "ports": [], "shapes": []}), encoding="utf-8")
    calls: list[tuple[str, Any]] = []

    class FakeModeler:
        def __init__(self):
            self.model_units = None

    class FakeApp:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.modeler = FakeModeler()
            calls.append(("app_init", kwargs))

        def save_project(self, path, overwrite):
            calls.append(("save_project", {"path": path, "overwrite": overwrite, "model_units": self.modeler.model_units}))
            return True

        def release_desktop(self, **kwargs):
            calls.append(("release_desktop", kwargs))

    primary_app = FakeApp(role="primary")

    class FakeSession:
        app = primary_app
        startup = {}
        aedt_lock = {}
        project_lock = {"action": "not_applicable"}
        aedt_reaper = {"label": "primary"}
        aedt_ready = {}

        def mark_desktop_released(self):
            calls.append(("mark_desktop_released", None))

    @contextmanager
    def fake_session_opener(config, lifecycle, *, app_factory, settings_obj):
        yield FakeSession()

    def fake_build(app, layout, args, *, project_path, stackup_config):
        return SimpleNamespace(
            to_dict=lambda: {
                "project": str(project_path),
                "design": args.design,
                "geometry_count": 0,
                "ports": ["Port1", "Port2"],
                "build_only": True,
                "saved": True,
            }
        )

    monkeypatch.setattr(workflow, "build_hfss_layout_project", fake_build)
    monkeypatch.setattr(workflow, "patch_gap_ports_in_edb", lambda edb_path, args: {"patched": True, "edb_path": str(edb_path)})
    monkeypatch.setattr(workflow, "prepare_aedt_project_lock", lambda project: {"project": str(project), "removed": True})
    monkeypatch.setattr(workflow, "start_aedt_reaper", lambda app, **kwargs: {"label": kwargs["label"], "app_project": app.kwargs["project"]})

    args = _args(tmp_path, layout_path)
    args.patch_edb_port_properties = True
    args.port_type = "pin-gap"
    args.skip_ports = False

    result = workflow._run_hfss_with_runtime(
        args,
        workflow.HfssWorkflowRuntime(app_factory=FakeApp, settings=object(), session_opener=fake_session_opener),
    )

    project_path = tmp_path / "workspace" / "unit_case.aedt"
    assert ("release_desktop", {"close_projects": True, "close_desktop": True}) in calls
    assert ("mark_desktop_released", None) in calls
    assert ("save_project", {"path": str(project_path), "overwrite": True, "model_units": "mm"}) in calls
    assert calls[-1] == ("release_desktop", {"close_projects": True, "close_desktop": True})
    assert result["edb_port_patch"] == {"patched": True, "edb_path": str(project_path.with_suffix(".aedb"))}
    assert result["post_patch_project_lock"] == {"project": str(project_path), "removed": True}
    assert result["aedt_reapers"] == [
        {"label": "primary"},
        {"label": "simads_hfss_workflow_run_hfss_reopen", "app_project": str(project_path)},
    ]
