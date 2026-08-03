import csv
from pathlib import Path

from simads.hfss.results import write_plot_summary


def test_write_plot_summary(tmp_path: Path) -> None:
    trace_csv = tmp_path / "trace.csv"
    trace_csv.write_text("freq_ghz,s21_db\n7,-3\n", encoding="utf-8")
    summary_csv = tmp_path / "plot_summary.csv"

    written = write_plot_summary(trace_csv, "candidate_a", summary_csv)

    assert written == summary_csv
    rows = list(csv.DictReader(summary_csv.open(encoding="utf-8")))
    assert rows == [{"candidate": "candidate_a", "source": str(trace_csv)}]
