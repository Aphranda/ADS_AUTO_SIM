from argparse import Namespace
from pathlib import Path

from simads.config import load_stackup_config
from simads.hfss.stackup import configure_hfss_extents, reset_stackup
from simads.hfss.stackup import reset_stackup_from_config


class FakeLayers:
    def __init__(self) -> None:
        self.all_layers = ["old_top", "old_bottom"]
        self.removed = []
        self.added = []

    def remove_layer(self, layer):
        self.removed.append(layer)

    def add_layer(self, name, layer_type, thickness, elevation, material):
        self.added.append((name, layer_type, thickness, elevation, material))


class FakeModeler:
    def __init__(self) -> None:
        self.layers = FakeLayers()


class FakeDesign:
    def __init__(self) -> None:
        self.extents = None

    def EditHfssExtents(self, payload):
        self.extents = payload


class FakeApp:
    def __init__(self) -> None:
        self.modeler = FakeModeler()
        self.odesign = FakeDesign()


def test_reset_stackup_rebuilds_gnd_dielectric_top_layers() -> None:
    app = FakeApp()

    reset_stackup(app, core_h_mm=0.21, cu_t_mm=0.035)

    assert app.modeler.layers.removed == ["old_top", "old_bottom"]
    assert app.modeler.layers.added == [
        ("GND", "signal", "0.035mm", "0mm", "copper"),
        ("FR4_CORE", "dielectric", "0.21mm", "0.035mm", "SIMADS_FR4_ER4P6_TD02"),
        ("TOP", "signal", "0.035mm", "0.245mm", "copper"),
    ]


def test_configure_hfss_extents_can_be_disabled() -> None:
    app = FakeApp()

    changed = configure_hfss_extents(app, Namespace(configure_extents=False))

    assert changed is False
    assert app.odesign.extents is None


def test_reset_stackup_from_config_rebuilds_imported_jlc_layers() -> None:
    app = FakeApp()
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))

    reset_stackup_from_config(app, stackup)

    names = [item[0] for item in app.modeler.layers.added]
    assert names == [
        "ETCH_BOTTOM",
        "DIEL_PP_BOTTOM_7628_RC49_8P6MIL",
        "ETCH_INNER2",
        "DIEL_CORE_1P1MM_H_HOZ",
        "ETCH_INNER1",
        "DIEL_PP_TOP_7628_RC49_8P6MIL",
        "ETCH_TOP",
    ]
    assert app.modeler.layers.added[4] == ("ETCH_INNER1", "signal", "0.0152mm", "1.3256mm", "copper")
    assert app.modeler.layers.added[6] == ("ETCH_TOP", "signal", "0.035mm", "1.5512mm", "copper")
