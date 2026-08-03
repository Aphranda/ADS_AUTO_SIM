from pathlib import Path
import xml.etree.ElementTree as ET

from simads.config import load_project, load_stackup_config
from simads.config.stackups import stackup_from_mapping
from simads.ads.stackup_sync import sync_ads_stackup_files
from simads.stackups.ads import ads_stackup_layer_map, ads_substrate_text, ads_tech_layer_specs


def test_load_jlc04161h_stackup_config() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))

    assert stackup.stackup_id == "JLC04161H_7628_1P6MM"
    assert stackup.geometry.signal_layer == "ETCH_TOP"
    assert stackup.geometry.reference_ground_layer == "ETCH_INNER1"
    assert stackup.geometry.ground_layers == ("ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM")
    assert round(stackup.signal_to_reference_height_mm, 4) == 0.2104
    assert round(stackup.total_thickness_mm, 4) == 1.5862
    assert stackup.primary_dielectric is not None
    assert stackup.primary_dielectric.er == 4.4
    assert stackup.materials["JLC_1P1MM_H_HOZ_CORE"].er == 4.6


def test_project_config_references_real_stackup_config() -> None:
    project = load_project("bfp_6_8g_i7_fr4")

    assert project.ads.stackup_config is not None
    assert project.ads.stackup_config.name == "JLC04161H_7628_1P6MM.json"


def test_stackup_ads_mapping_is_independent_domain_module() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    mapping = ads_stackup_layer_map(stackup)

    assert mapping.substrate_name == "JLC04161H_7628_1P6MM"
    assert mapping.conductor_layer_ids["ETCH_TOP"] == 1000
    assert mapping.conductor_layer_ids["ETCH_INNER1"] == 1001
    assert mapping.drill_layer == "DRILL_TOP_BOTTOM"
    assert mapping.drill_layer_id == 1005
    assert mapping.drill_process_role == "CONDUCTOR_VIA"
    assert mapping.drill_layer_binding == "ETCH_TOP ETCH_BOTTOM"
    assert mapping.drill_substrate_top_layer == "ETCH_TOP"
    assert mapping.drill_substrate_bottom_layer == "ETCH_BOTTOM"
    assert mapping.boundary_layer == "EM_BOUNDARY"
    assert mapping.boundary_layer_id == 1004


def test_stackup_ads_tech_layer_specs_include_auxiliary_layers() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    specs = ads_tech_layer_specs(stackup)
    by_name = {spec.name: spec for spec in specs}

    assert by_name["ETCH_TOP"].number == 1000
    assert by_name["ETCH_TOP"].role == "conductor"
    assert by_name["ETCH_TOP"].process_role == "CONDUCTOR"
    assert by_name["DRILL_TOP_BOTTOM"].number == 1005
    assert by_name["DRILL_TOP_BOTTOM"].role == "conductor_via"
    assert by_name["DRILL_TOP_BOTTOM"].process_role == "CONDUCTOR_VIA"
    assert by_name["DRILL_TOP_BOTTOM"].layer_binding == "ETCH_TOP ETCH_BOTTOM"
    assert by_name["EM_BOUNDARY"].number == 1004
    assert by_name["EM_BOUNDARY"].role == "boundary"
    assert by_name["EM_BOUNDARY"].process_role == "BOUNDARY"


def test_custom_ads_via_layer_can_define_conductor_via_binding() -> None:
    base = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json")).raw
    assert base is not None
    data = dict(base)
    ads = dict(data["ads"])
    ads["drill_layer"] = "DRILL_TOP_BOTTOM"
    ads["drill_layer_id"] = 1005
    ads["via_layers"] = [
        {
            "name": "DRILL_TOP_BOTTOM",
            "layer_id": 1005,
            "process_role": "CONDUCTOR_VIA",
            "layer_binding": "ETCH_TOP ETCH_BOTTOM",
            "substrate_top_layer": "ETCH_TOP",
            "substrate_bottom_layer": "ETCH_BOTTOM",
        }
    ]
    data["ads"] = ads
    stackup = stackup_from_mapping(data)

    mapping = ads_stackup_layer_map(stackup)
    assert mapping.drill_layer == "DRILL_TOP_BOTTOM"
    assert mapping.drill_layer_id == 1005
    assert mapping.drill_process_role == "CONDUCTOR_VIA"
    assert mapping.drill_layer_binding == "ETCH_TOP ETCH_BOTTOM"

    by_name = {spec.name: spec for spec in ads_tech_layer_specs(stackup)}
    assert by_name["DRILL_TOP_BOTTOM"].process_role == "CONDUCTOR_VIA"
    assert by_name["DRILL_TOP_BOTTOM"].layer_binding == "ETCH_TOP ETCH_BOTTOM"

    root = ET.fromstring(ads_substrate_text(stackup).split("\n", 1)[1])
    via = root.find("./vias/via")
    assert via is not None
    assert via.get("layer") == "1005"
    assert via.get("index1") == "0"
    assert via.get("index2") == "3"


def test_jlc_stackup_ads_substrate_xml_contains_real_layers() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    text = ads_substrate_text(stackup)
    root = ET.fromstring(text.split("\n", 1)[1])

    layer_ids = [layer.get("layer") for layer in root.findall("./layers/layer")]
    assert layer_ids == ["1003", "1002", "1001", "1000"]
    assert not root.findall("./stack/interface[@groundplane='1']")

    stack = root.find("./stack")
    assert stack is not None
    stack_items = list(stack)
    assert [elem.get("materialname") for elem in stack_items] == [
        "AIR",
        "PERFECT_CONDUCTOR",
        "JLC_7628_RC49_8P6MIL",
        "PERFECT_CONDUCTOR",
        "JLC_1P1MM_H_HOZ_CORE",
        "PERFECT_CONDUCTOR",
        "JLC_7628_RC49_8P6MIL",
        "PERFECT_CONDUCTOR",
        "AIR",
    ]

    via = root.find("./vias/via")
    assert via is not None
    assert via.get("layer") == "1005"
    assert via.get("index1") == "0"
    assert via.get("index2") == "3"


def test_ads_stackup_sync_writes_isolated_library_files(tmp_path: Path) -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))
    library_dir = tmp_path / "SIMADS_EM_PAR_lib"
    library_dir.mkdir()
    (library_dir / "materials.matdb").write_text(
        "<!DOCTYPE Materials>\n<Materials><Conductors/><Dielectrics/></Materials>\n",
        encoding="utf-8",
    )
    (library_dir / "library.tech").write_text("<!DOCTYPE Technology>\n<Lpp_List />\n", encoding="utf-8")
    (library_dir / "display.tech").write_text("<!DOCTYPE Display>\n<Display />\n", encoding="utf-8")

    check = sync_ads_stackup_files(library_dir, stackup, apply=False, force=False)
    assert check.changed == {"substrate": True, "materials": True, "library_tech": True, "display_tech": True}
    assert not check.substrate_path.exists()

    applied = sync_ads_stackup_files(library_dir, stackup, apply=True, force=False)
    assert applied.substrate_path.exists()
    assert "JLC_7628_RC49_8P6MIL" in applied.materials_path.read_text(encoding="utf-8")
    assert "ETCH_TOP" in applied.library_tech_path.read_text(encoding="utf-8")
    assert "DRILL_TOP_BOTTOM:drawing" in applied.display_tech_path.read_text(encoding="utf-8")
