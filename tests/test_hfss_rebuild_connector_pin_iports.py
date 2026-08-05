from __future__ import annotations

from contextlib import contextmanager
import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_module():
    script = Path(__file__).resolve().parents[1] / "tools" / "hfss" / "rebuild_connector_pin_iports.py"
    spec = importlib.util.spec_from_file_location("rebuild_connector_pin_iports", script)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeODesign:
    def __init__(self, schematic_editor):
        self.schematic_editor = schematic_editor

    def SetActiveEditor(self, name):
        if name == "SchematicEditor":
            return self.schematic_editor
        raise ValueError(name)


class FakeSchematicEditor:
    def __init__(self):
        self.components = ["CompInst@SMA_CONN;80;8", "CompInst@SMA_CONN;81;8"]

    def GetAllComponents(self):
        return list(self.components)

    def GetComponentPins(self, selection):
        assert selection.startswith("CompInst@SMA_CONN;")
        return ["Pin_T1"]


class FakeApp:
    def __init__(self):
        self.schematic_editor = FakeSchematicEditor()
        self.odesign = FakeODesign(self.schematic_editor)
        self.save_calls = []

    def save_project(self, project=None, overwrite=False):
        self.save_calls.append((project, overwrite))
        return True


def _args(**overrides):
    values = {
        "project": Path("unit.aedt"),
        "design": "hfss_sma_connector_cpw",
        "delete_port": ["S2_1_Pin_T1"],
        "component_id": ["80"],
        "expected_port": ["S2_1_Pin_T1"],
        "component": [],
        "component_def": [],
        "raw_component": [],
        "pin": [],
        "element": [],
        "method": ["CreatePortsOnComponents"],
        "add_method": "add-pin",
        "page": 1,
        "delete_iport": True,
        "connect_schematic": True,
        "move_schematic_iport": True,
        "delete_old_schematic_wires": True,
        "schematic_safe_x_mil": None,
        "schematic_safe_y_mil": None,
        "schematic_safe_min_clearance_mil": 250.0,
        "schematic_safe_grid_start_x_mil": -4000.0,
        "schematic_safe_grid_start_y_mil": -4000.0,
        "schematic_safe_grid_step_mil": 1000.0,
        "schematic_safe_grid_count": 9,
        "execute": False,
        "save": False,
        "backup": False,
        "version": "2026.1",
        "non_graphical": True,
        "new_desktop": True,
        "remove_lock": False,
        "keep_attached": False,
        "close_projects": True,
        "close_desktop": True,
        "ready_timeout_s": 120.0,
        "ready_settle_s": 3.0,
        "output": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_build_port_plans_infers_connector_metadata_from_schematic() -> None:
    module = _load_module()
    app = FakeApp()

    plans, selected, errors = module.build_port_plans(_args(), app)

    assert errors == []
    assert len(plans) == 1
    assert plans[0].component == "SMA_CONN"
    assert plans[0].component_def == "SMA_CONN"
    assert plans[0].component_id == "80"
    assert plans[0].raw_component == "CompInst@SMA_CONN;80;8"
    assert plans[0].pin == "Pin_T1"
    assert plans[0].port == "S2_1_Pin_T1"
    assert selected[0]["status"] == "planned"


def test_rebuild_iports_executes_each_plan_and_saves_once(monkeypatch) -> None:
    module = _load_module()
    app = FakeApp()
    executed = []

    @contextmanager
    def fake_session(config, lifecycle):
        yield SimpleNamespace(app=app, metadata=lambda: {"aedt_startup": {"fake": True}})

    def fake_execute(app_arg, plan, *, execute, save, save_project_path):
        assert app_arg is app
        executed.append((plan.component_id, plan.port, execute, save, save_project_path))
        return {"status": "created_good_candidate", "port": plan.port}

    monkeypatch.setattr(module, "open_hfss3dlayout_session", fake_session)
    monkeypatch.setattr(module, "execute_connector_pin_port_plan", fake_execute)
    monkeypatch.setattr(module, "connector_port_acceptance_report", lambda app_arg, plans: {"status": "ok", "count": len(plans)})

    payload = module.rebuild_iports(
        _args(
            component_id=["80", "81"],
            delete_port=["S2_1_Pin_T1", "S1_1_Pin_T1"],
            expected_port=["S2_1_Pin_T1", "S1_1_Pin_T1"],
            execute=True,
            save=True,
        )
    )

    assert payload["status"] == "rebuilt"
    assert payload["acceptance_report"] == {"status": "ok", "count": 2}
    assert executed == [
        ("80", "S2_1_Pin_T1", True, False, "unit.aedt"),
        ("81", "S1_1_Pin_T1", True, False, "unit.aedt"),
    ]
    assert app.save_calls == [("unit.aedt", True)]
