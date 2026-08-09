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


def test_run_validates_after_updating_dependent_design(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    calls: list[tuple[str, str]] = []

    class FakeODesign:
        def ValidateDesign(self):
            calls.append(("validate", "BFP_5O_marki_l3_ref_r1"))
            return True

    class FakeApp:
        design_list = ["2.4_CON", "BFP_5O_marki_l3_ref_r1"]
        ports = []
        project_name = "BFP_HFSS"

        def __init__(self):
            self.design_name = "BFP_5O_marki_l3_ref_r1"
            self.odesign = FakeODesign()
            self.oproject = self

        @property
        def setup_names(self):
            return ["Setup1"] if self.design_name in self.design_list else []

        def SetActiveDesign(self, design):
            calls.append(("raw_active", design))
            self.design_name = design
            return self

        def GetModule(self, name):
            assert name == "AnalysisSetup"
            return self

        def GetSetups(self):
            return ["Setup1"]

        def Analyze(self, setup):
            calls.append(("raw_analyze", f"{self.design_name}:{setup}"))
            return True

        def set_active_design(self, design):
            calls.append(("active", design))
            self.design_name = design

        def analyze_setup(self, setup):
            calls.append(("analyze", f"{self.design_name}:{setup}"))
            return True

        def validate_full_design(self, output_dir=None):
            calls.append(("validate", "BFP_5O_marki_l3_ref_r1"))
            return ["ok"], True

    class FakeSession:
        def __init__(self):
            self.app = FakeApp()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def metadata(self):
            return {}

    def fake_export(app, *, setup, sweep, output_file, attempts, delay_s, renormalization, impedance):
        path = Path(output_file)
        path.write_text("! fake s2p\n", encoding="utf-8")
        return str(path), [{"attempt": 1, "ok": True}]

    monkeypatch.setattr(runner, "open_hfss3dlayout_session", lambda config, lifecycle: FakeSession())
    monkeypatch.setattr(runner, "stable_export_touchstone", fake_export)
    monkeypatch.setattr(runner, "run_post_tools", lambda *args, **kwargs: {"score": "ok"})
    args = runner.parse_args(
        [
            "--project",
            str(tmp_path / "BFP_HFSS.aedt"),
            "--design",
            "BFP_5O_marki_l3_ref_r1",
            "--setup",
            "Setup1",
            "--sweep",
            "Sweep1",
            "--candidate",
            "case",
            "--out-dir",
            str(tmp_path / "out"),
            "--postprocess-profile",
            "filter",
            "--validate-update-design",
            "2.4_CON",
            "--no-auto-validate-update-designs",
        ]
    )

    result = runner.run(args)

    assert result["status"] == "ok"
    assert result["pre_validate_update_designs"][0]["status"] == "updated"
    assert calls[:4] == [
        ("raw_active", "2.4_CON"),
        ("raw_analyze", "2.4_CON:Setup1"),
        ("active", "BFP_5O_marki_l3_ref_r1"),
        ("validate", "BFP_5O_marki_l3_ref_r1"),
    ]
    assert ("analyze", "BFP_5O_marki_l3_ref_r1:Setup1") in calls


def test_component_dependency_scan_maps_numbered_connector_instances() -> None:
    runner = load_runner()

    class FakeEditor:
        def GetComponentInfo(self, comp_id):
            if comp_id == "3":
                return ["ComponentName=2_4_CON1"]
            if comp_id == "4":
                return ["ComponentName=2_4_CON2"]
            if comp_id == "20":
                return ["ComponentName=R0402_0R1"]
            raise RuntimeError("missing")

    class FakeDesign:
        def SetActiveEditor(self, name):
            assert name == "Layout"
            return FakeEditor()

    class FakeApp:
        design_list = ["BFP_5O_marki_l3_ref_r1", "2.4_CON", "Unrelated"]
        odesign = FakeDesign()

    payload = runner._component_design_dependencies(FakeApp(), parent_design="BFP_5O_marki_l3_ref_r1")

    assert payload["dependencies"] == ["2.4_CON"]
    assert payload["components_by_name"]["2_4_CON1"] == ["3"]
    assert payload["components_by_name"]["2_4_CON2"] == ["4"]
    assert "R0402_0R1" in payload["unmatched_components"]


def test_validate_only_stops_before_export(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    calls: list[str] = []

    class FakeODesign:
        def ValidateDesign(self):
            calls.append("validate")
            return True

    class FakeApp:
        design_list = ["BFP"]
        ports = []
        project_name = "unit"
        design_name = "BFP"
        odesign = FakeODesign()

        def validate_full_design(self, output_dir=None):
            calls.append("validate")
            return ["ok"], True

    class FakeSession:
        app = FakeApp()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def metadata(self):
            return {}

    monkeypatch.setattr(runner, "open_hfss3dlayout_session", lambda config, lifecycle: FakeSession())
    monkeypatch.setattr(runner, "stable_export_touchstone", lambda *args, **kwargs: calls.append("export"))
    args = runner.parse_args(
        [
            "--project",
            str(tmp_path / "unit.aedt"),
            "--design",
            "BFP",
            "--out-dir",
            str(tmp_path / "out"),
            "--validate-only",
            "--no-auto-validate-update-designs",
        ]
    )

    result = runner.run(args)

    assert result["status"] == "validated"
    assert calls == ["validate"]


def test_validate_warning_stops_before_analyze(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    calls: list[str] = []

    class FakeApp:
        design_list = ["BFP"]
        ports = []
        project_name = "unit"
        design_name = "BFP"

        def validate_full_design(self, output_dir=None):
            calls.append("validate")
            return ["ok"], True

        def analyze_setup(self, setup):
            calls.append("analyze")
            return True

    class FakeSession:
        app = FakeApp()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def metadata(self):
            return {}

    def fake_messages(app, *, aedt_messages):
        if aedt_messages:
            return ["Project: unit, Design: BFP, [warning] cached data is out of date"]
        return []

    monkeypatch.setattr(runner, "open_hfss3dlayout_session", lambda config, lifecycle: FakeSession())
    monkeypatch.setattr(runner, "_safe_messages", fake_messages)
    args = runner.parse_args(
        [
            "--project",
            str(tmp_path / "unit.aedt"),
            "--design",
            "BFP",
            "--out-dir",
            str(tmp_path / "out"),
            "--no-auto-validate-update-designs",
        ]
    )

    result = runner.run(args)

    assert result["status"] == "validation_needs_review"
    assert result["validation_alerts"]["warnings"] == ["Project: unit, Design: BFP, [warning] cached data is out of date"]
    assert calls == ["validate"]


def test_validation_alerts_ignores_plain_info() -> None:
    runner = load_runner()

    alerts = runner._validation_alerts(
        {"attempts": [{"messages": ["Ports Defined: 2"]}]},
        [],
        ["Project: unit, [info] Normal completion of simulation"],
    )

    assert alerts["errors"] == []
    assert alerts["warnings"] == []
    assert alerts["allowed_warnings"] == []
    assert alerts["blocking_warnings"] == []


def test_validation_alerts_allows_configured_warning() -> None:
    runner = load_runner()

    warning = "Project: unit, [warning] Referenced material 'COPPER' matches local definition 'copper'."
    alerts = runner._validation_alerts(
        {"attempts": []},
        [],
        [warning],
        allowed_warning_patterns=[r"Referenced material '.+' matches local definition '.+'"],
    )

    assert alerts["warnings"] == [warning]
    assert alerts["allowed_warnings"] == [warning]
    assert alerts["blocking_warnings"] == []
