from __future__ import annotations

from pathlib import Path

from simads.hfss.port_plans import (
    ConnectorPinPortPlan,
    connector_port_acceptance_report,
    execute_connector_pin_port_plan,
    is_valid_connector_pin_port,
)


class FakeODesign:
    def __init__(self, app):
        self.app = app

    def SetActiveEditor(self, name):
        if name == "Layout":
            return self.app.layout_editor
        if name == "SchematicEditor":
            return self.app.schematic_editor
        raise ValueError(name)


class FakeLayoutEditor:
    def __init__(self, app):
        self.app = app
        self.create_calls = []

    def GetComponentPinInfo(self, component, pin):
        return ["X=0.001", "Y=0.002", "Angle=0"]

    def CreatePortsOnComponents(self, args):
        self.create_calls.append(args)
        if args == ["NAME:elements", "80"]:
            if "S2_1_Pin_T1" not in self.app.port_list:
                self.app.port_list.append("S2_1_Pin_T1")
            self.app.schematic_editor.add_port("IPort@S2_1_Pin_T1;1", x=0.001, y=0.002, wire_id="")
            return True
        return False

    def CreatePortInstancePorts(self, args):
        return False

    def GetPortInfo(self, port):
        if port == "S2_1_Pin_T1":
            return ["Name=S2_1_Pin_T1", "Type=EdgePort", "ConnectionPoints=(1,2)"]
        return ["Name=Other", "Type=EdgePort", "ConnectionPoints=NONE"]

    def GetNetConnections(self, port):
        if port == "S2_1_Pin_T1":
            return ["ComponentPin 80 Pin_T1 0"]
        if port == "BAD_Pin_T1":
            return ["ComponentPin 80 Pin_T1 0"]
        return []


class FakeSchematicEditor:
    def __init__(self):
        self.ports = ["IPort@S2_1_Pin_T1;old"]
        self.port_info = {
            "IPort@S2_1_Pin_T1;old": {"x": 0.003, "y": 0.004, "angle": 0.0, "wire_id": "old_wire"}
        }
        self.pin_wire_id = "old_pin_wire"
        self.delete_calls = []
        self.change_calls = []
        self.wire_calls = []

    def add_port(self, port, *, x, y, wire_id):
        if port not in self.ports:
            self.ports.append(port)
        self.port_info[port] = {"x": x, "y": y, "angle": 0.0, "wire_id": wire_id}

    def GetAllPorts(self):
        return list(self.ports)

    def GetPortInfo(self, port):
        info = self.port_info[port]
        values = [f"X={info['x']}", f"Y={info['y']}", f"Angle={info['angle']}"]
        if info.get("wire_id"):
            values.append(f"WireId={info['wire_id']}")
        return values

    def GetAllComponents(self):
        return []

    def GetComponentPins(self, component):
        return []

    def GetComponentPinInfo(self, component, pin):
        return ["X=0.001", "Y=0.002", "Angle=0", f"WireId={self.pin_wire_id}"]

    def Delete(self, args):
        self.delete_calls.append(args)
        selections = args[args.index("Selections:=") + 1]
        targets = selections if isinstance(selections, list) else [selections]
        self.ports = [port for port in self.ports if port not in targets]
        for target in targets:
            self.port_info.pop(target, None)
        return True

    def ChangeProperty(self, args):
        self.change_calls.append(args)
        prop_server = args[1][1][1]
        changed = args[1][2][1]
        x_text = changed[changed.index("X:=") + 1]
        y_text = changed[changed.index("Y:=") + 1]
        self.port_info[prop_server]["x"] = float(x_text.removesuffix("mil")) * 25.4e-6
        self.port_info[prop_server]["y"] = float(y_text.removesuffix("mil")) * 25.4e-6
        return True

    def CreateWire(self, wire_data, attributes):
        self.wire_calls.append((wire_data, attributes))
        for port in self.ports:
            if port.startswith("IPort@S2_1_Pin_T1"):
                self.port_info[port]["wire_id"] = "new_wire"
        self.pin_wire_id = "new_wire"
        return True


class FakeApp:
    def __init__(self):
        self.port_list = []
        self.schematic_editor = FakeSchematicEditor()
        self.layout_editor = FakeLayoutEditor(self)
        self.odesign = FakeODesign(self)
        self.save_calls = []

    def save_project(self, project=None, overwrite=False):
        self.save_calls.append((project, overwrite))
        return True


def test_connector_pin_port_validation_requires_real_connection_points() -> None:
    good = {
        "port_info": {"ok": True, "value": ["Type=EdgePort", "ConnectionPoints=(1,2)"]},
        "net_connections": {"ok": True, "value": ["ComponentPin 80 Pin_T1 0"]},
    }
    no_points = {
        "port_info": {"ok": True, "value": ["Type=EdgePort", "ConnectionPoints=NONE"]},
        "net_connections": {"ok": True, "value": ["ComponentPin 80 Pin_T1 0"]},
    }
    interface_port = {
        "port_info": {"ok": True, "value": ["Type=EdgePort", "ConnectionPoints=(1,2)"]},
        "net_connections": {"ok": True, "value": ["ComponentPin 80 Pin_T1 0", "InterfacePort Port1"]},
    }

    assert is_valid_connector_pin_port(good, "80", "Pin_T1") is True
    assert is_valid_connector_pin_port(no_points, "80", "Pin_T1") is False
    assert is_valid_connector_pin_port(interface_port, "80", "Pin_T1") is False


def test_execute_connector_pin_port_plan_deletes_creates_connects_and_saves(tmp_path: Path) -> None:
    app = FakeApp()
    plan = ConnectorPinPortPlan(
        component="SMA1",
        component_def="SMA",
        component_id="80",
        raw_component="CompInst@SMA;80;8",
        port="S2_1_Pin_T1",
    )

    payload = execute_connector_pin_port_plan(
        app,
        plan,
        execute=True,
        save=True,
        save_project_path=str(tmp_path / "unit.aedt"),
    )

    assert payload["status"] == "created_good_candidate"
    assert payload["delete"]["targets"] == ["IPort@S2_1_Pin_T1;old"]
    assert payload["attempts"][0]["method"] == "CreatePortsOnComponents"
    assert payload["attempts"][0]["good_ports"] == ["S2_1_Pin_T1"]
    assert payload["schematic_connect"]["status"] == "connected"
    assert payload["acceptance_report"]["status"] == "ok"
    assert payload["acceptance_report"]["expected"][0]["connection_points"] == "(1,2)"
    assert payload["saved"] is True
    assert app.save_calls == [(str(tmp_path / "unit.aedt"), True)]


def test_connector_port_acceptance_report_lists_component_pin_only_rejections() -> None:
    app = FakeApp()
    app.port_list = ["S2_1_Pin_T1", "BAD_Pin_T1"]
    app.schematic_editor.add_port("IPort@S2_1_Pin_T1;1", x=0.001, y=0.002, wire_id="wire_1")
    plan = ConnectorPinPortPlan(
        component="SMA1",
        component_def="SMA",
        component_id="80",
        raw_component="CompInst@SMA;80;8",
        port="S2_1_Pin_T1",
    )

    report = connector_port_acceptance_report(app, (plan,))

    assert report["status"] == "ok"
    assert report["port_count"] == {"layout": 2, "schematic_iports": 2, "expected": 1}
    assert report["expected"][0]["layout_port_valid"] is True
    assert report["expected"][0]["schematic_connected"] is True
    assert report["component_pin_only_rejected"] == [
        {
            "port": "BAD_Pin_T1",
            "component_id": "80",
            "pin": "Pin_T1",
            "connection_points": "NONE",
            "net_connections": ["ComponentPin 80 Pin_T1 0"],
        }
    ]
