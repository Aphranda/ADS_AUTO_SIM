from pathlib import Path

from simads.config import load_project, load_stackup_config


def test_load_jlc04161h_stackup_config() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))

    assert stackup.stackup_id == "JLC04161H_7628_1P6MM"
    assert stackup.geometry.signal_layer == "ETCH_TOP"
    assert stackup.geometry.reference_ground_layer == "ETCH_INNER1"
    assert round(stackup.signal_to_reference_height_mm, 4) == 0.2104
    assert round(stackup.total_thickness_mm, 4) == 1.5862
    assert stackup.primary_dielectric is not None
    assert stackup.primary_dielectric.er == 4.4
    assert stackup.materials["JLC_1P1MM_H_HOZ_CORE"].er == 4.6


def test_project_config_references_real_stackup_config() -> None:
    project = load_project("bfp_6_8g_i7_fr4")

    assert project.ads.stackup_config is not None
    assert project.ads.stackup_config.name == "JLC04161H_7628_1P6MM.json"
