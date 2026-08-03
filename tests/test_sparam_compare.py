import csv
from pathlib import Path

from simads.workflows.sparam_compare import (
    SParamTrace,
    compare_traces,
    load_sparam_trace,
    run_compare,
    summarize_compare,
    write_compare_manifest,
)


def test_compare_traces_interpolates_right_trace_on_left_grid() -> None:
    ads = SParamTrace(
        label="ads",
        source=Path("ads.csv"),
        freq_ghz=[4.0, 6.0, 8.0, 10.0],
        traces_db={"s21": [-40.0, -3.0, -4.0, -50.0], "s11": [-1.0, -6.0, -7.0, -1.0]},
    )
    hfss = SParamTrace(
        label="hfss",
        source=Path("hfss.csv"),
        freq_ghz=[4.0, 5.0, 7.0, 9.0, 10.0],
        traces_db={"s21": [-42.0, -20.0, -5.0, -30.0, -52.0], "s11": [-1.5, -5.0, -8.0, -2.0, -1.2]},
    )

    rows = compare_traces(ads, hfss, sparams=["s21", "s11"])

    assert [row["freq_ghz"] for row in rows] == ["4", "6", "8", "10"]
    assert float(rows[1]["hfss_s21_db"]) == -12.5
    assert float(rows[1]["delta_s21_db"]) == -9.5
    assert float(rows[2]["hfss_s21_db"]) == -17.5


def test_summarize_compare_reports_error_metrics() -> None:
    rows = [
        {"freq_ghz": "5", "delta_s21_db": "1", "abs_delta_s21_db": "1"},
        {"freq_ghz": "6", "delta_s21_db": "-2", "abs_delta_s21_db": "2"},
        {"freq_ghz": "8", "delta_s21_db": "3", "abs_delta_s21_db": "3"},
    ]

    summary = summarize_compare(rows, sparams=["s21"])

    assert summary[0]["sparam"] == "s21"
    assert summary[0]["points"] == "3"
    assert summary[0]["max_abs_delta_db"] == "3"
    assert summary[0]["passband_mean_abs_delta_db"] == "2.5"


def test_run_compare_reads_existing_csv_shapes(tmp_path: Path) -> None:
    ads_csv = tmp_path / "ads.csv"
    hfss_csv = tmp_path / "hfss.csv"
    ads_csv.write_text(
        "\n".join(
            [
                "frequency_hz,s21_db,s11_db,s22_db",
                "4000000000,-40,-1,-1",
                "6000000000,-3,-6,-6",
                "8000000000,-4,-7,-7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    hfss_csv.write_text(
        "\n".join(
            [
                "freq_ghz,s21_db,s11_db,s22_db",
                "4,-42,-1.5,-1.5",
                "6,-5,-7,-7",
                "8,-6,-8,-8",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    written = run_compare(
        left_path=ads_csv,
        right_path=hfss_csv,
        out_csv=tmp_path / "compare.csv",
        summary_csv=tmp_path / "summary.csv",
        svg=None,
        sparams=["s21", "s11", "s22"],
    )

    assert written["compare_csv"].exists()
    rows = list(csv.DictReader(written["compare_csv"].open(encoding="utf-8")))
    assert rows[1]["freq_ghz"] == "6"
    assert rows[1]["delta_s21_db"] == "-2"
    summary = load_sparam_trace(hfss_csv, label="hfss")
    assert summary.label == "hfss"


def test_write_compare_manifest(tmp_path: Path) -> None:
    ads_csv = tmp_path / "ads.csv"
    hfss_csv = tmp_path / "hfss.csv"
    compare_csv = tmp_path / "compare.csv"
    summary_csv = tmp_path / "summary.csv"
    ads_csv.write_text("frequency_hz,s21_db\n4000000000,-40\n6000000000,-3\n", encoding="utf-8")
    hfss_csv.write_text("freq_ghz,s21_db\n4,-42\n6,-5\n", encoding="utf-8")
    compare_csv.write_text(
        "freq_ghz,ads_s21_db,hfss_s21_db,delta_s21_db,abs_delta_s21_db\n4,-40,-42,-2,2\n6,-3,-5,-2,2\n",
        encoding="utf-8",
    )
    summary_csv.write_text("sparam,points,max_abs_delta_db\ns21,2,2\n", encoding="utf-8")

    paths = write_compare_manifest(
        run_dir=tmp_path / "runs" / "run1",
        run_id="run1",
        project_id="project_a",
        round_id="round1",
        candidate_id="candidate_a",
        profile_id="ads_hfss_compare",
        ads_path=ads_csv,
        hfss_path=hfss_csv,
        written={"compare_csv": compare_csv, "summary_csv": summary_csv},
        elapsed_s=0.5,
    )

    assert paths["run_manifest"].exists()
    assert paths["artifact_manifest"].exists()
    assert paths["state"].exists()
