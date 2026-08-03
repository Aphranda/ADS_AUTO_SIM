from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import pytest

from simads.ads.naming import fem_simulation_path_length, short_ads_cell_name
from simads.ads.ports import build_two_port_reference_specs, place_layout_pins, resolve_next_reference_layer
from tools.ads.ads_clone_emsetup_template import (
    patch_existing_ads_gui_port_state,
    set_pin_snapshot,
    set_port_gnd_layer,
    sync_ads_gui_port_state,
)
import tools.ads.ads_import_dxf_add_ports as ads_import
from tools.ads.ads_import_dxf_add_ports import load_layout_via_pad_diameter


class FakeTermType:
    INPUT_OUTPUT = "input_output"


class FakeDbUu:
    TermType = FakeTermType


class FakeDesign:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def find_or_add_net(self, name: str) -> str:
        self.calls.append(("net", name))
        return name

    def add_term(self, net: str, name: str, term_type: str | None = None) -> str:
        self.calls.append(("term", net, name, term_type))
        return f"term:{name}"

    def create_layer_id(self, layer: str) -> str:
        self.calls.append(("layer", layer))
        return f"layer:{layer}"

    def add_dot(self, layer_id: str, point: tuple[float, float]) -> str:
        self.calls.append(("dot", layer_id, point))
        return f"dot:{point}"

    def add_pin(self, term: str, dots: object, *, angle: float = 0.0) -> str:
        self.calls.append(("pin", term, dots, angle))
        return f"pin:{term}"


class FakeLayoutDesign:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def find_or_add_net(self, name: str) -> str:
        self.calls.append(("net", name))
        return name

    def create_layer_id(self, layer: str) -> str:
        self.calls.append(("layer", layer))
        return f"layer:{layer}"

    def add_rectangle(self, layer_id: str, lower_left: tuple[float, float], upper_right: tuple[float, float]) -> Any:
        shape = type("FakeShape", (), {})()
        self.calls.append(("rect", layer_id, lower_left, upper_right, shape))
        return shape

    def add_polygon(self, layer_id: str, points: list[tuple[float, float]]) -> Any:
        shape = type("FakeShape", (), {})()
        self.calls.append(("polygon", layer_id, points, shape))
        return shape

    def add_plane(self, plane_info: Any, shape_obj: Any, name: str) -> Any:
        plane = type("FakePlane", (), {})()
        self.calls.append(("plane", plane_info.layer_id, getattr(plane_info, "net", None), getattr(shape_obj, "net", None), name))
        return plane

    def add_via_with_drill_layer(
        self,
        padstack: str,
        layer_id: str,
        point: tuple[float, float],
        *,
        name: str,
    ) -> str:
        self.calls.append(("via_drill", padstack, layer_id, point, name))
        return name

    def add_via_with_specified_layers(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append(("via_specified", args, kwargs))
        raise AssertionError("via should use the legacy drill-layer path")

    def add_net_connection_label(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append(("net_label", args, kwargs))
        raise AssertionError("via should not receive a net label")

    def save_design(self) -> None:
        self.calls.append(("save",))

    def close_design(self) -> None:
        self.calls.append(("close",))


class FakeDbUuLayout:
    class PlaneInfo:
        def __init__(self, design: FakeLayoutDesign) -> None:
            self.design = design
            self.layer_id: str | None = None

    def __init__(self, design: FakeLayoutDesign) -> None:
        self.design = design

    def create_layout(self, target: tuple[str, str, str]) -> FakeLayoutDesign:
        self.design.calls.append(("create_layout", target))
        return self.design


class FakeLibrary:
    name = "SIMADS_EM_PAR_lib"


def test_ads_port_reference_layer_is_next_ground_layer() -> None:
    reference_layer = resolve_next_reference_layer(
        "ETCH_TOP",
        ("ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"),
    )

    assert reference_layer == "ETCH_INNER1"


def test_ads_two_port_specs_keep_reference_metadata() -> None:
    p1, p2 = build_two_port_reference_specs(
        (-3.0, 0.5),
        (12.0, 0.5),
        signal_layer="ETCH_TOP",
        reference_layer="ETCH_INNER1",
    )

    assert p1.name == "P1"
    assert p1.signal_point == (-3.0, 0.5)
    assert p1.angle_deg == 180.0
    assert p1.reference.layer == "ETCH_INNER1"
    assert p1.reference.point == p1.signal_point
    assert p2.name == "P2"
    assert p2.angle_deg == 0.0
    assert p2.reference.net_name == ""


def test_place_layout_pins_uses_signal_layer_and_reports_reference() -> None:
    design = FakeDesign()
    ports = build_two_port_reference_specs(
        (0.0, 0.0),
        (1.0, 0.0),
        signal_layer="ETCH_TOP",
        reference_layer="ETCH_INNER1",
    )

    placed = place_layout_pins(design, FakeDbUu(), ports)

    assert ("layer", "ETCH_TOP") in design.calls
    assert ("dot", "layer:ETCH_TOP", (0.0, 0.0)) in design.calls
    assert not any(call == ("layer", "ETCH_INNER1") for call in design.calls)
    assert ("pin", "term:P1", ["dot:(0.0, 0.0)"], 180.0) in design.calls
    assert ("pin", "term:P2", ["dot:(1.0, 0.0)"], 0.0) in design.calls
    assert placed[0]["reference"]["layer"] == "ETCH_INNER1"
    assert placed[1]["reference"]["point"] == (1.0, 0.0)


def test_emsetup_port_editor_sets_explicit_gnd_layer_and_signal_pin_snapshot() -> None:
    root = ET.fromstring(
        """
        <PortEditorDialog>
          <PinView>
            <Pins>
              <Pin>
                <pinName>P1</pinName>
                <shapes>
                  <PinShapeDef>
                    <layerNum>1</layerNum>
                    <purposeNum>-1</purposeNum>
                    <layerIdName>cond:drawing</layerIdName>
                    <shapeType>point</shapeType>
                    <points><stdItem>0:0</stdItem></points>
                  </PinShapeDef>
                </shapes>
              </Pin>
            </Pins>
          </PinView>
          <PortView>
            <Ports>
              <Port><portName>P1</portName><gndLayer /></Port>
              <Port><portName>P2</portName></Port>
            </Ports>
          </PortView>
        </PortEditorDialog>
        """
    )

    set_pin_snapshot(root, "P1", -3.54, 1.95, layer_name="ETCH_TOP", layer_num=1000)
    set_port_gnd_layer(root, "ETCH_INNER1", gnd_layer_num=1001)

    assert root.findtext(".//PinShapeDef/layerNum") == "1000"
    assert root.findtext(".//PinShapeDef/layerIdName") == "ETCH_TOP:drawing"
    assert root.findtext(".//PinShapeDef/points/stdItem") == "-0.00354:0.00195"
    assert [elem.text for elem in root.findall(".//Port/gndLayer")] == ["1001", "1001"]


def test_emsetup_port_editor_gnd_layer_falls_back_to_layer_name() -> None:
    root = ET.fromstring(
        """
        <PortEditorDialog>
          <PortView>
            <Ports>
              <Port><portName>P1</portName><gndLayer /></Port>
              <Port><portName>P2</portName></Port>
            </Ports>
          </PortView>
        </PortEditorDialog>
        """
    )

    assert set_port_gnd_layer(root, "ETCH_INNER1") == "ETCH_INNER1"
    assert [elem.text for elem in root.findall(".//Port/gndLayer")] == ["ETCH_INNER1", "ETCH_INNER1"]


def test_existing_ads_gui_port_state_is_patched_when_present(tmp_path: Path) -> None:
    workspace = tmp_path / "SIMADS_EM_PAR"
    state_xml = workspace / "undefined" / "state" / "SIMADS_EM_PAR_lib" / "cell_a" / "layout" / "emSetup.xml"
    state_xml.parent.mkdir(parents=True)
    state_xml.write_text(
        """
        <PortEditorDialog>
          <PinView>
            <Pins>
              <Pin>
                <pinName>P1</pinName>
                <shapes><PinShapeDef><layerNum>1</layerNum><layerIdName>cond:drawing</layerIdName><points><stdItem>0:0</stdItem></points></PinShapeDef></shapes>
              </Pin>
              <Pin>
                <pinName>P2</pinName>
                <shapes><PinShapeDef><layerNum>1</layerNum><layerIdName>cond:drawing</layerIdName><points><stdItem>0:0</stdItem></points></PinShapeDef></shapes>
              </Pin>
            </Pins>
          </PinView>
          <PortView>
            <Ports>
              <Port><portName>P1</portName><gndLayer /></Port>
              <Port><portName>P2</portName><gndLayer /></Port>
            </Ports>
          </PortView>
        </PortEditorDialog>
        """,
        encoding="utf-8",
    )
    params = tmp_path / "params.json"
    params.write_text(
        """
        {
          "ports": [
            {"name": "P1", "x": -3.54, "y": 1.95},
            {"name": "P2", "x": 7.0502, "y": 1.95}
          ]
        }
        """,
        encoding="utf-8",
    )

    patched = patch_existing_ads_gui_port_state(
        workspace,
        "SIMADS_EM_PAR_lib",
        "cell_a",
        params,
        signal_layer="ETCH_TOP",
        signal_layer_num=1000,
        reference_ground_layer="ETCH_INNER1",
        reference_ground_layer_num=1001,
    )

    assert patched == state_xml
    root = ET.parse(state_xml).getroot()
    assert [elem.text for elem in root.findall(".//Port/gndLayer")] == ["ETCH_INNER1", "ETCH_INNER1"]
    assert [elem.text for elem in root.findall(".//Port/PlusPinNames/stdItem")] == ["P1", "P2"]
    assert [elem.text for elem in root.findall(".//Port/MinusPinNames/stdItem")] == ["::__GND__", "::__GND__"]
    assert [elem.text for elem in root.findall(".//PinShapeDef/layerNum")] == ["1000", "1000"]
    assert [elem.text for elem in root.findall(".//PinShapeDef/layerIdName")] == [
        "ETCH_TOP:drawing",
        "ETCH_TOP:drawing",
    ]


def test_ads_gui_port_state_is_created_when_missing(tmp_path: Path) -> None:
    workspace = tmp_path / "SIMADS_EM_PAR"
    params = tmp_path / "params.json"
    params.write_text(
        """
        {
          "ports": {
            "P1": [-3.54, 1.95],
            "P2": [7.0502, 1.95]
          }
        }
        """,
        encoding="utf-8",
    )

    created = sync_ads_gui_port_state(
        workspace,
        "SIMADS_EM_PAR_lib",
        "cell_a",
        params,
        signal_layer="ETCH_TOP",
        signal_layer_num=1000,
        reference_ground_layer="ETCH_INNER1",
    )

    assert created == workspace / "undefined" / "state" / "SIMADS_EM_PAR_lib" / "cell_a" / "layout" / "emSetup.xml"
    root = ET.parse(created).getroot()
    assert root.tag == "EmSimSetup"
    assert root.findtext(".//workspaceText") == "undefined"
    assert root.findtext(".//libraryText") == "SIMADS_EM_PAR_lib"
    assert root.findtext(".//cellText") == "cell_a"
    assert root.findtext(".//viewText") == "layout"
    assert [elem.text for elem in root.findall(".//Port/gndLayer")] == ["ETCH_INNER1", "ETCH_INNER1"]
    assert [elem.text for elem in root.findall(".//Port/PlusPinNames/stdItem")] == ["P1", "P2"]
    assert [elem.text for elem in root.findall(".//Port/MinusPinNames/stdItem")] == ["::__GND__", "::__GND__"]
    assert [elem.text for elem in root.findall(".//PinShapeDef/layerIdName")] == [
        "ETCH_TOP:drawing",
        "ETCH_TOP:drawing",
    ]
    assert [elem.text for elem in root.findall(".//PinShapeDef/points/stdItem")] == [
        "-0.00354:0.00195",
        "0.0070502:0.00195",
    ]


def test_load_layout_via_pad_diameter_prefers_larger_pad(tmp_path: Path) -> None:
    params = tmp_path / "params.json"
    params.write_text(
        '{"parameters": {"via_diameter_mm": 0.254, "via_pad_mm": 0.3556}}',
        encoding="utf-8",
    )

    assert load_layout_via_pad_diameter(params) == 0.3556


def test_generated_dxf_via_uses_legacy_drill_layer_path_without_net_label(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dxf = tmp_path / "via.dxf"
    dxf.write_text(
        "\n".join(
            [
                "0",
                "SECTION",
                "2",
                "ENTITIES",
                "0",
                "CIRCLE",
                "8",
                "pcvia1",
                "10",
                "1.0",
                "20",
                "2.0",
                "30",
                "0",
                "40",
                "0.127",
                "0",
                "ENDSEC",
                "0",
                "EOF",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    design = FakeLayoutDesign()
    monkeypatch.setattr(
        ads_import,
        "_ensure_circular_via_padstack",
        lambda library, metal_layer, via_layer, diameter_mm: f"{library.name}:{via_layer}_d0p254mm",
    )

    counts = ads_import._add_generated_dxf_subset_layout(
        FakeDbUuLayout(design),
        FakeLibrary(),
        "cell_a",
        str(dxf),
        "ETCH_TOP",
        "pcvia1",
        ("ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"),
        via_pad_diameter_mm=0.3556,
    )

    assert counts["via"] == 1
    assert ("via_drill", "SIMADS_EM_PAR_lib:pcvia1_d0p254mm", "layer:pcvia1", (1.0, 2.0), "pcvia1_1") in design.calls
    assert not any(call[0] == "via_specified" for call in design.calls)
    assert not any(call[0] == "net_label" for call in design.calls)


def test_generated_dxf_reference_ground_solid_uses_gnd_net(tmp_path: Path) -> None:
    dxf = tmp_path / "gnd.dxf"
    dxf.write_text(
        "\n".join(
            [
                "0",
                "SECTION",
                "2",
                "ENTITIES",
                "0",
                "SOLID",
                "8",
                "ETCH_INNER1",
                "10",
                "0.0",
                "20",
                "0.0",
                "11",
                "2.0",
                "21",
                "0.0",
                "12",
                "2.0",
                "22",
                "1.0",
                "13",
                "0.0",
                "23",
                "1.0",
                "0",
                "ENDSEC",
                "0",
                "EOF",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    design = FakeLayoutDesign()

    counts = ads_import._add_generated_dxf_subset_layout(
        FakeDbUuLayout(design),
        FakeLibrary(),
        "cell_a",
        str(dxf),
        "ETCH_TOP",
        "DRILL_TOP_BOTTOM",
        ("ETCH_INNER1",),
        via_pad_diameter_mm=0.3556,
    )

    assert counts["plane"] == 1
    assert ("net", "GND") in design.calls
    assert ("plane", "layer:ETCH_INNER1", "GND", "GND", "PLANE_ETCH_INNER1_1") in design.calls


def test_short_ads_cell_name_keeps_fem_path_under_ads_limit() -> None:
    cell = short_ads_cell_name("i7_fr4_r13_retest_base_l555_taper_ads_gnd_l234_jlc04161h_7628_1p6mm")

    assert len(cell) <= 40
    assert cell.endswith("_mm")
    assert (
        fem_simulation_path_length(
            workspace=r"D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR",
            library="SIMADS_EM_PAR_lib",
            cell=cell,
        )
        < 160
    )
