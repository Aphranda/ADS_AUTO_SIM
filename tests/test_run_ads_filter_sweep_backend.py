import sys
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

TOOLS = Path("tools").resolve()
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from run_ads_filter_sweep import build_hfss_sweep_command, candidate_layout_json, configured_backends


def test_sweep_backend_defaults_to_ads_even_when_pipeline_supports_both() -> None:
    args = Namespace(
        backend="ads",
        _pipeline_config=SimpleNamespace(simulation_backends=("ads_rfpro", "hfss3dlayout")),
    )

    assert configured_backends(args) == ("ads_rfpro",)


def test_sweep_auto_backend_uses_pipeline_backends() -> None:
    args = Namespace(
        backend="auto",
        _pipeline_config=SimpleNamespace(simulation_backends=("ads_rfpro", "hfss3dlayout")),
    )

    assert configured_backends(args) == ("ads_rfpro", "hfss3dlayout")


def test_build_hfss_sweep_command_routes_through_standard_runner(tmp_path: Path) -> None:
    args = Namespace(
        project_id="project_a",
        sweep_id="sweep_a",
        pipeline_id="pipeline_a",
        round_id="round13",
        device_id="filter.interdigital",
        out_dir=tmp_path / "layouts",
        results_dir=tmp_path / "results",
        hfss_profile="home",
        hfss_build_only=True,
        hfss_dry_run=True,
    )

    command = build_hfss_sweep_command(
        args,
        candidate="candidate_a",
        run_id="run_hfss",
        run_dir=tmp_path / "results" / "runs" / "run_hfss",
        root=Path("repo"),
        host_python=Path("python.exe"),
    )

    assert command[:4] == ["python.exe", str(Path("repo") / "tools" / "run_sim_filter_candidate.py"), "candidate_a", "--backend"]
    assert command[command.index("--backend") + 1] == "hfss"
    assert command[command.index("--layout") + 1] == str(candidate_layout_json(args, "candidate_a"))
    assert command[command.index("--out-dir") + 1] == str(tmp_path / "results" / "hfss" / "candidate_a")
    assert command[command.index("--run-id") + 1] == "run_hfss"
    assert command[command.index("--round-id") + 1] == "round13"
    assert command[command.index("--device-id") + 1] == "filter.interdigital"
    assert command[command.index("--hfss-profile") + 1] == "home"
    assert "--build-only" in command
    assert "--hfss-dry-run" in command
    assert "--write-manifest" in command
