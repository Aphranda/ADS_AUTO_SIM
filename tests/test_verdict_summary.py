import json
from pathlib import Path

from simads.workflows.verdict_summary import build_verdict_summary, write_verdict_summary


def test_build_verdict_summary_combines_ads_hfss_and_compare(tmp_path: Path) -> None:
    ads_score = tmp_path / "ads_score.csv"
    hfss_score = tmp_path / "hfss_score.csv"
    compare_summary = tmp_path / "compare_summary.csv"
    ads_score.write_text(
        "status,s21_5g_db,s21_6g_db,s21_8g_db,passband_min_s21_db,worst_s11_6_8_db,worst_s22_6_8_db\n"
        "TUNE,-26.98,-2.51,-4.60,-4.60,-4.26,-4.20\n",
        encoding="utf-8",
    )
    hfss_score.write_text(
        "file,status,s21_5g_db,s21_6g_db,s21_8g_db,passband_min_s21_db,worst_s11_6_8_db,worst_s22_6_8_db\n"
        "filter.s2p,TUNE,-21.67,-3.24,-5.52,-5.52,-6.92,-6.88\n",
        encoding="utf-8",
    )
    compare_summary.write_text(
        "sparam,points,mean_abs_delta_db,passband_mean_abs_delta_db,delta_at_5g_db\n"
        "s21,40,6.2099,1.21163,5.06359\n",
        encoding="utf-8",
    )

    summary = build_verdict_summary(
        candidate_id="candidate_a",
        ads_score_csv=ads_score,
        hfss_score_csv=hfss_score,
        compare_summary_csv=compare_summary,
        compare_svg=tmp_path / "compare.svg",
    )

    assert summary["candidate_id"] == "candidate_a"
    assert summary["verdict"] == "needs_tuning"
    assert summary["ads"]["metrics"]["s21_5g_db"] == -26.98
    assert summary["hfss"]["metrics"]["worst_s22_6_8_db"] == -6.88
    assert summary["compare"]["metrics"]["s21"]["passband_mean_abs_delta_db"] == 1.21163


def test_write_verdict_summary_writes_utf8_json(tmp_path: Path) -> None:
    out = tmp_path / "verdict.json"

    written = write_verdict_summary(out, {"candidate_id": "候选", "verdict": "needs_tuning"})

    assert written == out
    assert json.loads(out.read_text(encoding="utf-8"))["candidate_id"] == "候选"
