from argparse import Namespace
from pathlib import Path

from simads.hfss.build import build_hfss_layout_project


def mm(value: float) -> str:
    return f"{value:g}mm"


class FakeMaterial:
    def __init__(self) -> None:
        self.permittivity = None
        self.dielectric_loss_tangent = None
        self.conductivity = None
        self.updated = False

    def update(self) -> None:
        self.updated = True


class FakeMaterials:
    def __init__(self) -> None:
        self.added = []

    def add_material(self, name, properties):
        self.added.append((name, properties))
        return FakeMaterial()


class FakeLayers:
    def __init__(self) -> None:
        self.all_layers = []
        self.added = []

    def add_layer(self, name, layer_type, thickness, elevation, material):
        self.added.append((name, layer_type, thickness, elevation, material))


class FakeModeler:
    def __init__(self) -> None:
        self.model_units = None
        self.layers = FakeLayers()
        self.calls = []

    def create_rectangle(self, layer, origin, size, name, net):
        self.calls.append(("rect", layer, origin, size, name, net))
        return Namespace(name=name)

    def create_polygon(self, layer, points, units, name, net):
        self.calls.append(("polygon", layer, points, units, name, net))
        return Namespace(name=name)

    def create_circle(self, layer, x, y, radius, name, net):
        self.calls.append(("circle", layer, x, y, radius, name, net))
        return Namespace(name=name)

    def create_via(self, x, y, hole_diam, top_layer, bot_layer, name, net):
        self.calls.append(("via", x, y, hole_diam, top_layer, bot_layer, name, net))
        return Namespace(name=name)


class FakeDesign:
    def __init__(self) -> None:
        self.extents = None
        self.design_options = []

    def EditHfssExtents(self, payload):
        self.extents = payload

    def DesignOptions(self, payload):
        self.design_options.append(payload)
        return None


class FakeApp:
    def __init__(self) -> None:
        self.materials = FakeMaterials()
        self.modeler = FakeModeler()
        self.odesign = FakeDesign()
        self.saved_project = None

    def create_setup(self, **kwargs):
        return Namespace(name=kwargs["name"], kwargs=kwargs)

    def create_linear_count_sweep(self, **kwargs):
        return Namespace(name=kwargs["name"], kwargs=kwargs)

    def save_project(self, path, overwrite):
        self.saved_project = (path, overwrite)
        return True


def test_build_hfss_layout_project_is_independent_from_workflow() -> None:
    layout = {
        "metadata": {"er": 4.6, "dielectric_height_mm": 0.2104, "copper_thickness_mm": 0.035},
        "ports": [
            {"number": 1, "x": -1.0, "y": 0.1},
            {"number": 2, "x": 1.0, "y": 0.1},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 4.0, "h": 2.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -1.0, "y": 0.0, "w": 2.0, "h": 0.2},
        ],
    }
    args = Namespace(
        er=None,
        loss_tangent=None,
        substrate_height_mm=None,
        copper_thickness_mm=None,
        gnd_boundary_mode="em-boundary",
        configure_extents=False,
        skip_ports=True,
        setup="Setup_4to10G",
        mesh_size_factor=2.0,
        enable_design_intersection_check=None,
        adaptive_frequency_ghz=7.0,
        start_ghz=4.0,
        stop_ghz=10.0,
        points=40,
        sweep="Sweep_4to10G_40pt",
        sweep_type="Interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=120,
        build_only=True,
    )
    app = FakeApp()

    result = build_hfss_layout_project(app, layout, args, project_path=Path("case.aedt")).to_dict()

    assert app.modeler.model_units == "mm"
    assert app.modeler.layers.added[1][2] == "0.2104mm"
    assert app.modeler.calls[0] == ("rect", "GND", [mm(-2), mm(-1)], [mm(4), mm(2)], "hfss_ground_plane", "GND")
    assert app.modeler.calls[1] == ("rect", "TOP", [mm(-1), mm(0)], [mm(2), mm(0.2)], "input_feed", "IN")
    assert app.saved_project == ("case.aedt", True)
    assert result["geometry_count"] == 2
    assert result["ports"] == []
    assert result["design_options"] is None
    assert result["setup"] == "Setup_4to10G"
    assert result["sweep"] == "Sweep_4to10G_40pt"


def test_build_hfss_layout_project_can_disable_design_intersection_check() -> None:
    layout = {
        "metadata": {"er": 4.6, "dielectric_height_mm": 0.2104, "copper_thickness_mm": 0.035},
        "ports": [],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -2.0, "y": -1.0, "w": 4.0, "h": 2.0},
        ],
    }
    args = Namespace(
        er=None,
        loss_tangent=None,
        substrate_height_mm=None,
        copper_thickness_mm=None,
        gnd_boundary_mode="em-boundary",
        configure_extents=False,
        skip_ports=True,
        setup="Setup_4to10G",
        mesh_size_factor=2.0,
        enable_design_intersection_check=False,
        adaptive_frequency_ghz=7.0,
        start_ghz=4.0,
        stop_ghz=10.0,
        points=40,
        sweep="Sweep_4to10G_40pt",
        sweep_type="Interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=120,
        build_only=True,
    )
    app = FakeApp()

    result = build_hfss_layout_project(app, layout, args, project_path=Path("case.aedt")).to_dict()

    assert app.odesign.design_options == [
        [
            "NAME:Options",
            "EnableDesignIntersectionCheck:=",
            False,
        ]
    ]
    assert result["design_options"]["EnableDesignIntersectionCheck"] is False
    assert result["design_options"]["applied"] is True
