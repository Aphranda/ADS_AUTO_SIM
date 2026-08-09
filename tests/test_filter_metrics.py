import math
from pathlib import Path

from simads.scoring.filter_metrics import BandWindow, summarize_filter_s2p


def write_db_s2p(path: Path) -> None:
    rows = [
        (5.0, -10.0, -30.0, -30.0, -10.0, 0.0),
        (6.0, -12.0, -3.0, -3.0, -11.0, -20.0),
        (7.0, -9.0, -2.0, -2.0, -8.0, -40.0),
        (8.0, -13.0, -4.0, -4.0, -12.0, -60.0),
        (9.0, -10.0, -35.0, -35.0, -10.0, -80.0),
        (10.0, -10.0, -50.0, -50.0, -10.0, -100.0),
    ]
    lines = ["# GHz S DB R 50"]
    for freq, s11, s21, s12, s22, phase in rows:
        lines.append(f"{freq:g} {s11:g} 0 {s21:g} {phase:g} {s12:g} {phase:g} {s22:g} 0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_summarize_filter_s2p_extracts_optimization_metrics(tmp_path: Path) -> None:
    s2p = tmp_path / "filter.s2p"
    write_db_s2p(s2p)

    metrics = summarize_filter_s2p(s2p, passband=BandWindow(6.0, 8.0))

    assert metrics["sample_count"] == 6
    assert metrics["markers"]["6G"]["s21_db"] == -3.0
    assert metrics["s21_peak"]["db"] == -2.0
    assert metrics["passband_s21_min"]["db"] == -4.0
    assert metrics["passband_s21_ripple_db"] == 2.0
    assert math.isclose(metrics["passband_worst_return_db"], -8.0)
    assert metrics["minus3db_band_ghz"] == [6.0, 8.0]
    assert not math.isnan(metrics["passband_group_delay_ns"]["avg"])
