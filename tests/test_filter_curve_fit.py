import json
from pathlib import Path

from simads.scoring.filter_curve_fit import compare_fit_to_simulation, fit_measured_batch


def test_fit_measured_batch_creates_dense_curve(tmp_path: Path) -> None:
    measured = tmp_path / "measured.csv"
    measured.write_text(
        "board_id,freq_ghz,s21_db,trace,source,note\n"
        "board_1,5.0,-40.0,S21,a,first\n"
        "board_1,6.0,-18.0,S21,a,first\n"
        "board_1,6.3,-9.0,S21,a,first\n"
        "board_1,8.0,-8.0,S21,a,first\n"
        "board_1,9.0,-46.0,S21,a,first\n"
        "board_2,5.0,-41.0,S21,b,second\n"
        "board_2,6.0,-17.0,S21,b,second\n"
        "board_2,6.3,-8.5,S21,b,second\n"
        "board_2,8.0,-8.2,S21,b,second\n"
        "board_2,9.0,-45.0,S21,b,second\n",
        encoding="utf-8",
    )
    sim = tmp_path / "sim.s2p"
    sim.write_text(
        "# GHZ S DB R 50\n"
        "5.0 -30 0 -30 0 -30 0 -30 0\n"
        "6.0 -10 0 -10 0 -10 0 -10 0\n"
        "6.3 -9 0 -9 0 -9 0 -9 0\n"
        "8.0 -8 0 -8 0 -8 0 -8 0\n"
        "9.0 -20 0 -20 0 -20 0 -20 0\n",
        encoding="utf-8",
    )

    fit = fit_measured_batch(measured)
    compare = compare_fit_to_simulation(fit, sim)

    assert len(fit["fit_rows"]) > 100
    assert fit["fit_rows"][0]["freq_ghz"] == 5.0
    assert fit["fit_rows"][-1]["freq_ghz"] == 9.0
    assert compare["summary"]["rms_error_db"] > 0.0
    assert compare["marker_compare_rows"]
