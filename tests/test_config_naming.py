import json
import sys
from pathlib import Path

from simads.config import load_stackup_config, name_with_stackup_token, path_with_stackup_token, stackup_name_token
from simads.hfss.artifacts import default_project_name

TOOLS_LAYOUT = Path("tools/layout").resolve()
if str(TOOLS_LAYOUT) not in sys.path:
    sys.path.insert(0, str(TOOLS_LAYOUT))

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
    assert layout["metadata"]["dielectric_height_mm"] == stackup.signal_to_reference_height_mm
    assert params_json["parameters"]["substrate"] == "JLC04161H_7628_1P6MM"


def test_hfss_default_project_name_uses_layout_stackup_metadata() -> None:
    layout = {
        "layout_id": "i7_fr4_r14_probe",
        "metadata": {"stackup_token": "jlc04161h_7628_1p6mm"},
    }

    assert default_project_name(layout) == "i7_fr4_r14_probe_jlc04161h_7628_1p6mm_hfss_verdict"
