import sys
from argparse import Namespace
from pathlib import Path

TOOLS = Path("tools").resolve()
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from simads.config import pipeline_from_mapping
from run_sim_filter_candidate import build_hfss_command, selected_backends


def test_selected_backends_expands_cli_and_pipeline_values() -> None:
    assert selected_backends("ads", ("hfss3dlayout",)) == ("ads_rfpro",)
    assert selected_backends("hfss", ("ads_rfpro",)) == ("hfss3dlayout",)
    assert selected_backends("both", ("ads_rfpro",)) == ("ads_rfpro", "hfss3dlayout")
    assert selected_backends("auto", ("ads_rfpro", "hfss3dlayout")) == ("ads_rfpro", "hfss3dlayout")


def test_build_hfss_command_uses_pipeline_contract() -> None:
    pipeline = pipeline_from_mapping(
        {
            "schema_version": "0.1.0",
            "pipeline_id": "pipeline_hfss",
            "project_id": "project_a",
            "simulation_backends": ["hfss3dlayout"],
            "frequency": {"start_ghz": 4.0, "stop_ghz": 10.0, "points": 40, "plan_type": "Linear"},
            "hfss": {
                "workflow_script": "tools/hfss/run_hfss3dlayout_filter_verdict.py",
                "profile": "home",
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
    args = Namespace(
        candidate="candidate_a",
        layout=Path("candidate_a_layout.json"),
        out_dir=Path("out"),
        project_name=None,
        hfss_project=None,
        hfss_project_model=None,
        hfss_project_action=None,
        hfss_profile=None,
        build_only=True,
        hfss_dry_run=True,
        write_manifest=True,
        run_id="run1",
        run_dir=Path("runs/run1"),
        round_id="round1",
        device_id="filter.interdigital",
    )

    command = build_hfss_command(args, pipeline)

    assert "tools\\hfss\\run_hfss3dlayout_filter_verdict.py" in " ".join(command) or "tools/hfss/run_hfss3dlayout_filter_verdict.py" in " ".join(command)
    assert command[command.index("--profile") + 1] == "home"
    assert command[command.index("--pipeline-id") + 1] == "pipeline_hfss"
    assert command[command.index("--project-model") + 1] == "single_aedt_project_multiple_designs"
    assert command[command.index("--project-action") + 1] == "add"
    assert command[command.index("--project") + 1].endswith("shared_connector.aedt")
    assert command[command.index("--route") + 1] == "reliable"
    assert command[command.index("--stackup-config") + 1].endswith("JLC04161H_7628_1P6MM.json")
    assert command[command.index("--points") + 1] == "40"
    assert "--build-only" in command
    assert "--dry-run" in command
    assert "--write-manifest" in command
    assert command[command.index("--candidate-id") + 1] == "candidate_a"
    assert command[command.index("--round-id") + 1] == "round1"
    assert command[command.index("--device-id") + 1] == "filter.interdigital"
