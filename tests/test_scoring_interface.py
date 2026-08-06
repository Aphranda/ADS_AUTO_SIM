import json
from pathlib import Path

import pytest

from simads.scoring.interface import score_sparameter_file


def write_db_s2p(path: Path, rows: list[tuple[float, float, float, float, float]]) -> None:
    lines = ["# GHZ S DB R 50"]
    for freq, s11, s21, s12, s22 in rows:
        lines.append(f"{freq} {s11} 0 {s21} 0 {s12} 0 {s22} 0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_filter_profile_path_controls_frequency_windows(tmp_path: Path) -> None:
    s2p = tmp_path / "filter.s2p"
    write_db_s2p(
        s2p,
        [
            (1.0, -12.0, -40.0, -40.0, -12.0),
            (2.0, -12.0, -2.0, -2.0, -12.0),
            (3.0, -12.0, -1.0, -1.0, -12.0),
            (4.0, -12.0, -2.5, -2.5, -12.0),
            (5.0, -12.0, -35.0, -35.0, -12.0),
        ],
    )
    profile_path = tmp_path / "filter_profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "scoring_system": "filter",
                "profile_id": "unit_filter",
                "score_version": "unit_filter_v1",
                "frequency_ghz": {
                    "stop_low_probe": 1.0,
                    "passband_start": 2.0,
                    "passband_center": 3.0,
                    "passband_stop": 4.0,
                    "stop_high_probe": 5.0,
                },
                "targets": {
                    "s21_5g_max_db": -30.0,
                    "s21_6g_min_db": -3.0,
                    "s21_8g_min_db": -3.0,
                    "passband_min_s21_db": -3.0,
                    "passband_max_ripple_db": 2.0,
                    "passband_worst_return_loss_db": -10.0,
                },
            }
        ),
        encoding="utf-8",
    )

    row = score_sparameter_file(
        s2p,
        system="filter",
        profile_id="unit_filter",
        profile_path=profile_path,
    )

    assert row["score_version"] == "unit_filter_v1"
    assert row["scoring_system"] == "filter"
    assert row["s21_5g_db"] == "-40.00"
    assert row["s21_6g_db"] == "-2.00"
    assert row["s21_7g_db"] == "-1.00"
    assert row["s21_8g_db"] == "-2.50"
    assert row["s21_9g_db"] == "-35.00"
    assert row["status"] == "PASS_CANDIDATE"


def test_unified_interface_rejects_filter_baseline(tmp_path: Path) -> None:
    s2p = tmp_path / "filter.s2p"
    write_db_s2p(s2p, [(6.0, -12.0, -2.0, -2.0, -12.0), (8.0, -12.0, -2.5, -2.5, -12.0)])

    with pytest.raises(ValueError, match="filter scoring does not accept"):
        score_sparameter_file(
            s2p,
            system="filter",
            profile_id="fr4_25db_rl6",
            baseline_path=s2p,
        )
