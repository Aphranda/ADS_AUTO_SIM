import importlib.util
from pathlib import Path
import sys

from simads.hfss import results as hfss_results


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tools" / "hfss" / "run_existing_hfss3dlayout_verdict.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_existing_hfss3dlayout_verdict", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_connector_postprocess_writes_smith_artifact(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    commands = []

    monkeypatch.setattr(hfss_results, "hidden_subprocess_kwargs", lambda: {})
    monkeypatch.setattr(hfss_results.subprocess, "run", lambda command, check, **kwargs: commands.append(command))
    monkeypatch.setattr(hfss_results, "convert_s2p_to_csv", lambda s2p, trace_csv, *, profile: trace_csv.write_text("trace\n", encoding="utf-8"))
    monkeypatch.setattr(hfss_results, "write_plot_summary", lambda trace_csv, candidate, summary_csv: summary_csv.write_text("summary\n", encoding="utf-8"))

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = runner.run_post_tools(
        tmp_path / "case.s2p",
        out_dir / "case_score.csv",
        out_dir,
        "case",
        "connector",
    )

    assert result["smith_svg"] == str(out_dir / "svg" / "case_smith.svg")
    assert result["tdr_csv"] == str(out_dir / "case_tdr.csv")
    assert result["tdr_svg"] == str(out_dir / "svg" / "case_tdr.svg")
    assert len(commands) == 4
    assert commands[0][1].endswith("analyze_connector_s2p.py")
    assert commands[1][1].endswith("plot_connector_s_curves_svg.py")
    assert commands[2][1].endswith("plot_connector_smith_svg.py")
    assert commands[2][commands[2].index("--out") + 1] == str(out_dir / "svg" / "case_smith.svg")
    assert commands[3][1].endswith("plot_connector_tdr_svg.py")
    assert commands[3][commands[3].index("--csv-out") + 1] == str(out_dir / "case_tdr.csv")
    assert commands[3][commands[3].index("--svg-out") + 1] == str(out_dir / "svg" / "case_tdr.svg")


def test_filter_postprocess_does_not_write_smith_artifact(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    commands = []

    monkeypatch.setattr(hfss_results, "hidden_subprocess_kwargs", lambda: {})
    monkeypatch.setattr(hfss_results.subprocess, "run", lambda command, check, **kwargs: commands.append(command))
    monkeypatch.setattr(hfss_results, "convert_s2p_to_csv", lambda s2p, trace_csv, *, profile: trace_csv.write_text("trace\n", encoding="utf-8"))
    monkeypatch.setattr(hfss_results, "write_plot_summary", lambda trace_csv, candidate, summary_csv: summary_csv.write_text("summary\n", encoding="utf-8"))

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = runner.run_post_tools(
        tmp_path / "case.s2p",
        out_dir / "case_score.csv",
        out_dir,
        "case",
        "filter",
    )

    assert "smith_svg" not in result
    assert len(commands) == 2
    assert commands[0][1].endswith("analyze_filter_s2p.py")
    assert commands[1][1].endswith("plot_filter_s_curves_svg.py")


def test_connector_postprocess_can_use_unified_scoring_profile(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    commands = []

    monkeypatch.setattr(hfss_results, "hidden_subprocess_kwargs", lambda: {})
    monkeypatch.setattr(hfss_results.subprocess, "run", lambda command, check, **kwargs: commands.append(command))
    monkeypatch.setattr(hfss_results, "convert_s2p_to_csv", lambda s2p, trace_csv, *, profile: trace_csv.write_text("trace\n", encoding="utf-8"))
    monkeypatch.setattr(hfss_results, "write_plot_summary", lambda trace_csv, candidate, summary_csv: summary_csv.write_text("summary\n", encoding="utf-8"))

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    baseline = tmp_path / "baseline.s2p"
    result = runner.run_post_tools(
        tmp_path / "case.s2p",
        out_dir / "case_score.csv",
        out_dir,
        "case",
        "connector",
        scoring_profile_id="sma_launch_fullband_0p5_10g_v2",
        baseline_s2p=baseline,
    )

    assert result["scoring_profile_id"] == "sma_launch_fullband_0p5_10g_v2"
    assert result["baseline_s2p"] == str(baseline)
    assert commands[0][1].endswith("analyze_sparams.py")
    assert commands[0][commands[0].index("--system") + 1] == "connector"
    assert commands[0][commands[0].index("--profile-id") + 1] == "sma_launch_fullband_0p5_10g_v2"
    assert commands[0][commands[0].index("--baseline-s2p") + 1] == str(baseline)
