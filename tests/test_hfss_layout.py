from argparse import Namespace

from simads.hfss.layout import GeometryBuildOptions, create_geometry


class Obj:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeModeler:
    def __init__(self) -> None:
        self.calls = []

    def create_rectangle(self, layer, origin, size, name, net):
        self.calls.append(("rect", layer, origin, size, name, net))
        return Obj(name)

    def create_polygon(self, layer, points, units, name, net):
        self.calls.append(("polygon", layer, points, units, name, net))
        return Obj(name)

    def create_circle(self, layer, x, y, radius, name, net):
        self.calls.append(("circle", layer, x, y, radius, name, net))
        return Obj(name)

    def create_via(self, x, y, hole_diam, top_layer, bot_layer, name, net):
        self.calls.append(("via", x, y, hole_diam, top_layer, bot_layer, name, net))
        return Obj(name)


class FakeApp:
    def __init__(self) -> None:
        self.modeler = FakeModeler()


def test_create_geometry_builds_gnd_signal_and_via() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 0.5, "h": 0.2},
            {"kind": "polygon", "layer": "cond", "name": "resonator_1", "points": [[0, 0], [1, 0], [1, 1]]},
            {"kind": "via", "layer": "via", "name": "ground_via_1", "x": 0.5, "y": 0.5, "diameter": 0.2, "pad_diameter": 0.4},
        ],
    }
    app = FakeApp()

    names = create_geometry(app, layout, Namespace(gnd_boundary_mode="port-edges"))

    assert names == ["hfss_ground_plane", "input_feed", "resonator_1", "ground_via_1_pad", "ground_via_1"]
    assert app.modeler.calls[0] == ("rect", "GND", [-1.0, -1.0], [3.0, 3.0], "hfss_ground_plane", "GND")
    assert app.modeler.calls[1][-1] == "IN"
    assert app.modeler.calls[2][-1] == "GND"


def test_create_geometry_uses_configured_stackup_layers() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 0.5, "h": 0.2},
            {"kind": "via", "layer": "via", "name": "ground_via_1", "x": 0.5, "y": 0.5, "diameter": 0.2},
        ],
    }
    app = FakeApp()
    args = Namespace(
        gnd_boundary_mode="em-boundary",
        signal_layer="ETCH_TOP",
        reference_ground_layer="ETCH_INNER1",
        via_top_layer="ETCH_TOP",
        via_bottom_layer="ETCH_BOTTOM",
        ground_plane_name="hfss_ground_plane",
    )

    create_geometry(app, layout, args)

    assert app.modeler.calls[0] == ("rect", "ETCH_INNER1", [-2.0, -1.0], [5.0, 3.0], "hfss_ground_plane", "GND")
    assert app.modeler.calls[1][1] == "ETCH_TOP"
    assert app.modeler.calls[3] == ("via", 0.5, 0.5, 0.2, "ETCH_TOP", "ETCH_BOTTOM", "ground_via_1", "GND")


def test_create_geometry_accepts_explicit_options_without_cli_namespace() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 0.5, "h": 0.2},
        ],
    }
    app = FakeApp()
    options = GeometryBuildOptions(
        gnd_boundary_mode="port-edges",
        signal_layer="L1_TOP",
        reference_ground_layer="L2_GND",
        ground_plane_name="configured_gnd",
    )

    names = create_geometry(app, layout, options)

    assert names == ["configured_gnd", "input_feed"]
    assert app.modeler.calls[0] == ("rect", "L2_GND", [-1.0, -1.0], [3.0, 3.0], "configured_gnd", "GND")
    assert app.modeler.calls[1] == ("rect", "L1_TOP", [-1.0, 0.0], [0.5, 0.2], "input_feed", "IN")
