from argparse import Namespace

from simads.hfss.layout import GeometryBuildOptions, create_geometry


def mm(value: float) -> str:
    return f"{value:g}mm"


class Obj:
    def __init__(self, name: str) -> None:
        self.name = name
        self.negative = False


class FakeModeler:
    def __init__(self) -> None:
        self.calls = []
        self.subtract_calls = []

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

    def subtract(self, blank, tools, *args, **kwargs):
        self.subtract_calls.append((blank, tools, args, kwargs))
        return True


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
    assert app.modeler.calls[0] == ("rect", "GND", [mm(-1), mm(-1)], [mm(3), mm(3)], "hfss_ground_plane", "GND")
    assert app.modeler.calls[1][-1] == "IN"
    assert app.modeler.calls[2][-1] == "GND"
    assert app.modeler.calls[3] == ("circle", "TOP", mm(0.5), mm(0.5), mm(0.2), "ground_via_1_pad", "GND")
    assert app.modeler.calls[4] == ("via", mm(0.5), mm(0.5), mm(0.2), "TOP", "GND", "ground_via_1", "GND")


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

    assert app.modeler.calls[0] == (
        "rect",
        "ETCH_INNER1",
        [mm(-2), mm(-1)],
        [mm(5), mm(3)],
        "hfss_ground_plane",
        "GND",
    )
    assert app.modeler.calls[1][1] == "ETCH_TOP"
    assert app.modeler.calls[3] == ("via", mm(0.5), mm(0.5), mm(0.2), "ETCH_TOP", "ETCH_BOTTOM", "ground_via_1", "GND")


def test_create_geometry_accepts_layout_shapes_on_configured_signal_layer() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {"kind": "rect", "layer": "ETCH_TOP", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 0.5, "h": 0.2},
        ],
    }
    app = FakeApp()

    names = create_geometry(
        app,
        layout,
        GeometryBuildOptions(signal_layer="ETCH_TOP", reference_ground_layer="ETCH_INNER1"),
    )

    assert names == ["hfss_ground_plane", "input_feed"]
    assert app.modeler.calls[1] == ("rect", "ETCH_TOP", [mm(-1), mm(0)], [mm(0.5), mm(0.2)], "input_feed", "IN")


def test_create_geometry_honors_explicit_shape_net_metadata() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {
                "kind": "rect",
                "layer": "cond",
                "name": "center_line_top_ground",
                "x": 0.0,
                "y": 0.3,
                "w": 1.0,
                "h": 0.7,
                "metadata": {"net": "GND"},
            },
        ],
    }
    app = FakeApp()

    create_geometry(app, layout, Namespace(gnd_boundary_mode="port-edges"))

    assert app.modeler.calls[1] == (
        "rect",
        "TOP",
        [mm(0), mm(0.3)],
        [mm(1), mm(0.7)],
        "center_line_top_ground",
        "GND",
    )


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
    assert app.modeler.calls[0] == ("rect", "L2_GND", [mm(-1), mm(-1)], [mm(3), mm(3)], "configured_gnd", "GND")
    assert app.modeler.calls[1] == ("rect", "L1_TOP", [mm(-1), mm(0)], [mm(0.5), mm(0.2)], "input_feed", "IN")


def test_create_geometry_uses_explicit_reference_ground_plane_without_default() -> None:
    layout = {
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.0},
            {"number": 2, "x": 2.0, "y": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 5.0, "h": 3.0},
            {
                "kind": "reference_ground_plane",
                "layer": "GND",
                "name": "l2_ground_part",
                "x": -1.0,
                "y": -1.0,
                "w": 3.0,
                "h": 1.0,
                "metadata": {"target_layer": "L2_GND"},
            },
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 0.5, "h": 0.2},
        ],
    }
    app = FakeApp()

    names = create_geometry(
        app,
        layout,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="L1_TOP",
            reference_ground_layer="L2_GND",
            ground_plane_name="configured_gnd",
        ),
    )

    assert names == ["l2_ground_part", "input_feed"]
    assert app.modeler.calls[0] == ("rect", "L2_GND", [mm(-1), mm(-1)], [mm(3), mm(1)], "l2_ground_part", "GND")
    assert all(call[4] != "configured_gnd" for call in app.modeler.calls)


def test_create_geometry_skips_reference_ground_cutout_without_boolean_subtract() -> None:
    layout = {
        "ports": [],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 4.0, "h": 2.0},
            {
                "kind": "reference_ground_cutout",
                "layer": "GND",
                "name": "launch_l2_void",
                "x": -0.5,
                "y": -0.25,
                "w": 1.0,
                "h": 0.5,
            },
        ],
    }
    app = FakeApp()

    names = create_geometry(app, layout, GeometryBuildOptions(reference_ground_layer="GND"))

    assert names == ["hfss_ground_plane"]
    assert len(app.modeler.calls) == 1
    assert app.modeler.subtract_calls == []


def test_create_geometry_skips_explicit_reference_ground_cutout_without_boolean_subtract() -> None:
    layout = {
        "ports": [],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 4.0, "h": 2.0},
            {
                "kind": "reference_ground_plane",
                "layer": "GND",
                "name": "l3_reference_plane",
                "x": -2.0,
                "y": -1.0,
                "w": 4.0,
                "h": 2.0,
                "metadata": {"target_layer": "L3_GND"},
            },
            {
                "kind": "reference_ground_cutout",
                "layer": "GND",
                "name": "l3_connector_void",
                "points": [[-0.5, -0.2], [0.5, -0.2], [0.5, 0.2], [-0.5, 0.2]],
                "metadata": {"target_layer": "L3_GND"},
            },
        ],
    }
    app = FakeApp()

    create_geometry(app, layout, GeometryBuildOptions(reference_ground_layer="L2_GND"))

    assert app.modeler.calls[0][1] == "L2_GND"
    assert app.modeler.calls[1][1] == "L3_GND"
    assert len(app.modeler.calls) == 2
    assert app.modeler.subtract_calls == []


def test_create_geometry_suppresses_default_reference_ground_plane_for_partial_candidates() -> None:
    layout = {
        "metadata": {"suppress_default_reference_ground_plane": True},
        "ports": [],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 4.0, "h": 2.0},
            {"kind": "polygon", "layer": "cond", "name": "filter_core_finger_1", "points": [[0, 0], [1, 0], [1, 1]]},
        ],
    }
    app = FakeApp()

    names = create_geometry(app, layout, GeometryBuildOptions(reference_ground_layer="GND"))

    assert names == ["filter_core_finger_1"]
    assert app.modeler.calls == [("polygon", "TOP", [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]], "mm", "filter_core_finger_1", "SIG")]
