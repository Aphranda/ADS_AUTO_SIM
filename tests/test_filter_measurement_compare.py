import json
from pathlib import Path

from simads.scoring.filter_measurement_compare import compare_measurement_to_simulation


def test_compare_measurement_to_simulation_groups_boards(tmp_path: Path) -> None:
    measured = tmp_path / "measured.csv"
    measured.write_text(
        "board_id,freq_ghz,s21_db,source\n"
        "b1,6.0,-18.0,img1\n"
        "b2,6.0,-17.0,img2\n"
        "b1,8.0,-8.0,img1\n"
        "b2,8.0,-8.4,img2\n",
        encoding="utf-8",
    )
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps(
            {
                "markers": {
                    "6G": {"freq_ghz": 6.0, "s21_db": -6.5},
                    "8G": {"freq_ghz": 8.0, "s21_db": -8.0},
                }
            }
        ),
        encoding="utf-8",
    )

    payload = compare_measurement_to_simulation(measured, metrics)

    assert payload["comparison"][0]["board_count"] == 2
    assert payload["comparison"][0]["measured_s21_mean_db"] == -17.5
    assert payload["comparison"][0]["sim_minus_measured_mean_db"] == 11.0
    assert payload["summary"]["primary_gap"] == "measured_low_edge_is_higher_than_simulation"
