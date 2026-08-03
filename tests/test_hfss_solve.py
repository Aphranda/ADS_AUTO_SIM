from argparse import Namespace
from pathlib import Path

from simads.hfss.solve import solve_and_export_hfss


class FakeApp:
    def __init__(self, exported: Path | None = None) -> None:
        self.exported = exported
        self.analyzed = []
        self.exports = []

    def analyze_setup(self, setup):
        self.analyzed.append(setup)

    def export_touchstone(self, **kwargs):
        self.exports.append(kwargs)
        return str(self.exported) if self.exported is not None else None


def test_solve_and_export_hfss_runs_solver_export_and_post_tools(tmp_path: Path, monkeypatch) -> None:
    out_dir = tmp_path / "results"
    exported_s2p = tmp_path / "external.s2p"
    exported_s2p.write_text("! touchstone\n", encoding="utf-8")
    post_calls = []

    def fake_post_tools(s2p, score_csv, trace_csv, svg_dir, candidate):
        post_calls.append((s2p, score_csv, trace_csv, svg_dir, candidate))

    monkeypatch.setattr("simads.hfss.solve.run_post_tools", fake_post_tools)
    app = FakeApp(exported=exported_s2p)
    layout = {"layout_id": "case_a", "metadata": {"stackup_token": "jlc"}}
    args = Namespace(
        setup="Setup_4to10G",
        sweep="Sweep_4to10G_40pt",
        out_dir=out_dir,
        s2p=None,
        score_out=None,
        project=None,
        project_name=None,
        workspace_dir=tmp_path,
    )

    result = solve_and_export_hfss(app, layout, args).to_dict()

    assert app.analyzed == ["Setup_4to10G"]
    assert app.exports == [
        {
            "setup": "Setup_4to10G",
            "sweep": "Sweep_4to10G_40pt",
            "output_file": str(out_dir / "case_a_jlc_hfss.s2p"),
            "renormalization": True,
            "impedance": 50,
        }
    ]
    assert result["s2p"] == str(exported_s2p)
    assert result["score"] == str(out_dir / "case_a_jlc_hfss_score.csv")
    assert result["trace_csv"] == str(out_dir / "case_a_jlc_hfss_trace.csv")
    assert result["post_processed"] is True
    assert post_calls == [
        (
            exported_s2p,
            out_dir / "case_a_jlc_hfss_score.csv",
            out_dir / "case_a_jlc_hfss_trace.csv",
            out_dir / "svg",
            "case_a_jlc_hfss",
        )
    ]


def test_solve_and_export_hfss_skips_post_tools_when_s2p_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "simads.hfss.solve.run_post_tools",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("post tools should not run")),
    )
    app = FakeApp(exported=None)
    layout = {"layout_id": "case_b"}
    args = Namespace(
        setup="Setup",
        sweep="Sweep",
        out_dir=tmp_path,
        s2p=None,
        score_out=None,
        project=None,
        project_name=None,
        workspace_dir=tmp_path,
    )

    result = solve_and_export_hfss(app, layout, args).to_dict()

    assert result == {
        "setup": "Setup",
        "sweep": "Sweep",
        "s2p": str(tmp_path / "case_b_hfss.s2p"),
        "post_processed": False,
    }
