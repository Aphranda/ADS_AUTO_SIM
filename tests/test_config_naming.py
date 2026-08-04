import json
import sys
from pathlib import Path

TOOLS = Path("tools").resolve()
TOOLS_LAYOUT = Path("tools/layout").resolve()
for path in (TOOLS, TOOLS_LAYOUT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from simads.config import (
    load_project,
    load_stackup_config,
    name_with_stackup_token,
    path_with_stackup_token,
    pipeline_from_mapping,
    stackup_name_token,
)
from simads.ads.layout import LayoutImportPlan, build_import_command, parse_generated_dxf_subset
from simads.ads.workspace import AdsCellRef
from simads.hfss.artifacts import default_project_name
from tools.run_ads_filter_candidate import stackup_ads_substrate_name
from tools.ads.ads_run_rfpro_fem import rfpro_emsetup_view_candidates
from tools.ads.ads_import_dxf_add_ports import load_layout_net_config
from tools.ads.ads_clone_emsetup_template import clone_emsetup

from generate_interdigital_filter_layout import FilterParams, params_with_stackup_config, write_outputs  # noqa: E402


def test_stackup_token_and_legacy_replacement() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))

    assert stackup_name_token(stackup) == "jlc04161h_7628_1p6mm"
    assert (
        name_with_stackup_token("interdigital_7o_fr4_210um_round14", stackup)
        == "interdigital_7o_jlc04161h_7628_1p6mm_round14"
    )
    assert (
        name_with_stackup_token("i7_fr4_r14_l555", stackup)
        == "i7_fr4_r14_l555_jlc04161h_7628_1p6mm"
    )
    assert (
        path_with_stackup_token(Path("layouts/interdigital_7o_fr4_210um_round14"), stackup)
        == Path("layouts/interdigital_7o_jlc04161h_7628_1p6mm_round14")
    )


def test_interdigital_layout_records_configured_stackup(tmp_path: Path) -> None:
    config_path = Path("config/stackups/JLC04161H_7628_1P6MM.json")
    stackup = load_stackup_config(config_path)
    params = params_with_stackup_config(
        FilterParams(name="i7_fr4_210um_r14_probe", order=7, gaps_mm=(0.3, 0.4, 0.45, 0.45, 0.4, 0.3)),
        stackup,
        config_path=config_path,
    )

    outputs = write_outputs(params, tmp_path)
    layout = json.loads(Path(outputs["layout_json"]).read_text(encoding="utf-8"))
    params_json = json.loads(Path(outputs["params"]).read_text(encoding="utf-8"))

    assert layout["layout_id"] == "i7_jlc04161h_7628_1p6mm_r14_probe"
    assert layout["metadata"]["stackup_id"] == "JLC04161H_7628_1P6MM"
    assert layout["metadata"]["stackup_token"] == "jlc04161h_7628_1p6mm"
    assert layout["metadata"]["reference_ground_layer"] == "ETCH_INNER1"
    assert layout["metadata"]["ground_layers"] == ["ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"]
    assert layout["metadata"]["dielectric_height_mm"] == stackup.signal_to_reference_height_mm
    assert params_json["parameters"]["substrate"] == "JLC04161H_7628_1P6MM"


def test_interdigital_layout_can_emit_ads_reference_ground_plane(tmp_path: Path) -> None:
    config_path = Path("config/stackups/JLC04161H_7628_1P6MM.json")
    stackup = load_stackup_config(config_path)
    params = params_with_stackup_config(
        FilterParams(
            name="i7_fr4_210um_r14_ground_probe",
            order=7,
            gaps_mm=(0.3, 0.4, 0.45, 0.45, 0.4, 0.3),
            feed_len_mm=3.0,
            boundary_margin_mm=1.5,
            include_ground_plane=True,
            ground_boundary_mode="port-edges",
        ),
        stackup,
        config_path=config_path,
    )

    outputs = write_outputs(params, tmp_path)
    layout = json.loads(Path(outputs["layout_json"]).read_text(encoding="utf-8"))
    params_json = json.loads(Path(outputs["params"]).read_text(encoding="utf-8"))
    dxf_shapes = parse_generated_dxf_subset(Path(outputs["dxf_mm_coords"]))

    gnd_shapes = [
        shape
        for shape in layout["shapes"]
        if shape["name"].startswith(stackup.geometry.ground_plane_name)
        and shape["metadata"]["role"] == "reference_ground"
    ]
    assert len(gnd_shapes) == 1
    assert gnd_shapes[0]["layer"] == "ETCH_INNER1"
    assert "net" not in gnd_shapes[0]["metadata"]
    assert gnd_shapes[0]["x"] == params_json["ports"]["P1"][0]
    assert gnd_shapes[0]["x"] + gnd_shapes[0]["w"] == params_json["ports"]["P2"][0]
    assert params_json["derived"]["ground_plane"]["layer"] == "ETCH_INNER1"
    assert params_json["derived"]["ground_layers"] == ["ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM"]
    assert params_json["derived"]["layout_ground_layers"] == ["ETCH_INNER1"]
    assert [plane["layer"] for plane in params_json["derived"]["ground_planes"]] == ["ETCH_INNER1"]
    assert any(shape["type"] == "solid" and shape["layer"] == "ETCH_INNER1" for shape in dxf_shapes)
    assert not any(shape["type"] == "solid" and shape["layer"] == "ETCH_INNER2" for shape in dxf_shapes)
    assert not any(shape["type"] == "solid" and shape["layer"] == "ETCH_BOTTOM" for shape in dxf_shapes)
    assert [shape["name"] for shape in layout["shapes"]].count("output_feed") == 1
    svg_text = Path(outputs["svg"]).read_text(encoding="utf-8")
    assert "hfss_ground_plane / ETCH_" not in svg_text
    assert "Layout mm" in svg_text
    assert "boundary " in svg_text

    metal_layer, via_layer, ground_layers = load_layout_net_config(Path(outputs["params"]))
    assert metal_layer == "ETCH_TOP"
    assert via_layer == "DRILL_TOP_BOTTOM"
    assert ground_layers == ("ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM")


def test_hfss_default_project_name_uses_layout_stackup_metadata() -> None:
    layout = {
        "layout_id": "i7_fr4_r14_probe",
        "metadata": {"stackup_token": "jlc04161h_7628_1p6mm"},
    }

    assert default_project_name(layout) == "i7_fr4_r14_probe_jlc04161h_7628_1p6mm_hfss_verdict"


def test_rfpro_emsetup_candidates_prefer_physical_oa_view() -> None:
    assert rfpro_emsetup_view_candidates("emSetup") == ["em%Setup", "emSetup"]
    assert rfpro_emsetup_view_candidates("em%Setup") == ["em%Setup", "emSetup"]


def test_stackup_config_provides_ads_substrate_name() -> None:
    stackup = load_stackup_config(Path("config/stackups/JLC04161H_7628_1P6MM.json"))

    assert stackup_ads_substrate_name(stackup) == "JLC04161H_7628_1P6MM"


def test_pipeline_can_force_generated_dxf_subset_import() -> None:
    pipeline = pipeline_from_mapping(
        {
            "schema_version": "0.1.0",
            "pipeline_id": "pipeline_a",
            "project_id": "project_a",
            "ads": {"force_generated_dxf_subset": True},
        },
        root=Path.cwd(),
    )

    assert pipeline.ads.force_generated_dxf_subset is True
    assert pipeline.to_dict()["ads"]["force_generated_dxf_subset"] is True


def test_pipeline_can_configure_hfss_backend() -> None:
    pipeline = pipeline_from_mapping(
        {
            "schema_version": "0.1.0",
            "pipeline_id": "pipeline_hfss",
            "project_id": "project_a",
            "simulation_backends": "both",
            "hfss": {
                "workflow_script": "tools/hfss/run_hfss3dlayout_filter_verdict.py",
                "profile": "home",
                "workspace_dir": "D:/Work/ADS/SIMADS_EM_PAR/HFSS_VERDICT",
                "aedt_project": "D:/Work/ADS/SIMADS_EM_PAR/HFSS_VERDICT/shared_connector.aedt",
                "project_model": "single_aedt_project_multiple_designs",
                "project_action": "add",
                "route": "reliable",
                "stackup_config": "config/stackups/JLC04161H_7628_1P6MM.json",
                "design": "I7_FR4_HFSS_VERDICT",
                "port_type": "aedt-edge",
                "gnd_boundary_mode": "port-edges",
            },
        },
        root=Path.cwd(),
    )

    assert pipeline.simulation_backends == ("ads_rfpro", "hfss3dlayout")
    assert pipeline.hfss.profile == "home"
    assert pipeline.hfss.route == "reliable"
    assert pipeline.hfss.aedt_project is not None
    assert pipeline.hfss.aedt_project.name == "shared_connector.aedt"
    assert pipeline.hfss.project_model == "single_aedt_project_multiple_designs"
    assert pipeline.hfss.project_action == "add"
    assert pipeline.to_dict()["simulation_backends"] == ["ads_rfpro", "hfss3dlayout"]
    assert pipeline.to_dict()["hfss"]["port_type"] == "aedt-edge"


def test_project_can_configure_hfss_add_design_mode() -> None:
    project = load_project("hfss_sma_connector")

    assert project.hfss.aedt_project is not None
    assert project.hfss.aedt_project.name == "hfss_sma_connector_cpw.aedt"
    assert project.hfss.project_model == "single_aedt_project_multiple_designs"
    assert project.hfss.project_action == "add"
    assert project.hfss.simulations["dual_end_connector_50r"]["design"] == "DUAL_END_SMA_CPW_100MM"


def test_ads_layout_import_command_can_force_generated_dxf_subset() -> None:
    plan = LayoutImportPlan(
        profile_id="profile_a",
        target=AdsCellRef(Path("workspace"), "library_a", "cell_a"),
        dxf_path=Path("layout.dxf"),
        params_path=Path("layout_params.json"),
        force_generated_dxf_subset=True,
    )

    command = build_import_command(plan, ads_python=Path("ads_python.exe"), script=Path("tools/ads/ads_import_dxf_add_ports.py"))

    assert "--force-generated-dxf-subset" in command.args


def test_clone_emsetup_prefers_configured_stackup_substrate(tmp_path: Path) -> None:
    workspace = tmp_path / "ads_workspace"
    library = "SIMADS_EM_PAR_lib"
    template_cell = "SIMADS_EM_TEMPLATE_2PORT_FEM"
    target_cell = "i7_jlc_probe_mm_coords"
    setup_view = "em%Setup"
    template_setup = workspace / library / template_cell / setup_view
    target_dir = workspace / library / target_cell
    template_setup.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    (workspace / library / "JLC04161H_7628_1P6MM.subst").write_text("", encoding="utf-8")
    (template_setup / "emStateFile.xml").write_text(
        """<ADS_EMSetup>
  <libSubstName>SIMADS_EM_PAR_lib:FR4_210UM</libSubstName>
  <workspaceText>old</workspaceText>
  <libraryText>old</libraryText>
  <cellText>SIMADS_EM_TEMPLATE_2PORT_FEM</cellText>
  <startFreq>1</startFreq>
  <stopFreq>10</stopFreq>
  <ptsFreq>121</ptsFreq>
</ADS_EMSetup>""",
        encoding="utf-8",
    )
    params = tmp_path / "params.json"
    params.write_text(
        json.dumps(
            {
                "parameters": {"substrate": "JLC04161H_7628_1P6MM"},
                "ports": {"P1": [0.0, 0.0], "P2": [1.0, 0.0]},
            }
        ),
        encoding="utf-8",
    )

    xml_path = clone_emsetup(
        workspace=workspace,
        library=library,
        substrate_library=library,
        template_cell=template_cell,
        target_cell=target_cell,
        setup_view=setup_view,
        params_path=params,
        start_ghz=4.0,
        stop_ghz=10.0,
        points_text="40",
        overwrite=False,
        force=False,
        profile_substrate="SIMADS_EM_PAR_lib:FR4_210UM",
        substrate_override=f"{library}:JLC04161H_7628_1P6MM",
        prefer_params_substrate=True,
    )

    xml = xml_path.read_text(encoding="utf-8")
    assert "<libSubstName>SIMADS_EM_PAR_lib:JLC04161H_7628_1P6MM</libSubstName>" in xml
    assert "<cellText>i7_jlc_probe_mm_coords</cellText>" in xml
    assert "<startFreq>4</startFreq>" in xml
    assert "<ptsFreq>40</ptsFreq>" in xml
