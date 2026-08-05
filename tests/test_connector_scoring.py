from pathlib import Path

import pytest

from simads.scoring.connector import ConnectorScoreProfile, read_s2p_db, score_s2p


def write_db_s2p(path: Path, rows: list[tuple[float, float, float, float, float]]) -> None:
    lines = ["# GHZ S DB R 50"]
    for freq, s11, s21, s12, s22 in rows:
        lines.append(f"{freq} {s11} 0 {s21} 0 {s12} 0 {s22} 0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_connector_score_uses_full_band_fields_without_filter_terms(tmp_path: Path) -> None:
    s2p = tmp_path / "connector.s2p"
    write_db_s2p(
        s2p,
        [
            (0.5, -18.0, -0.2, -0.2, -17.0),
            (5.0, -9.0, -1.0, -1.0, -8.0),
            (10.0, -12.0, -2.2, -2.2, -11.0),
        ],
    )

    row = score_s2p(s2p)

    assert row["score_version"] == "connector_fullband_v1"
    assert row["score_profile_id"] == "sma_launch_fullband_0p5_10g_v1"
    assert row["status"] == "TUNE"
    assert row["s21_min_0p5_10g_db"] == "-2.20"
    assert row["worst_return_0p5_10g_db"] == "-8.00"
    assert row["worst_return_param"] == "s22"
    assert float(row["optimization_cost"]) > 0.0
    assert "passband_min_s21_db" not in row
    assert "worst_s11_6_8_db" not in row


def test_connector_score_can_mark_clean_fixture_as_pass_candidate(tmp_path: Path) -> None:
    s2p = tmp_path / "clean.s2p"
    write_db_s2p(
        s2p,
        [
            (0.5, -22.0, -0.10, -0.10, -21.0),
            (5.0, -20.0, -0.20, -0.20, -20.5),
            (10.0, -18.0, -0.40, -0.40, -17.0),
        ],
    )

    row = score_s2p(s2p)

    assert row["status"] == "PASS_CANDIDATE"
    assert row["optimization_cost"] == "0.000"
    assert float(row["connector_score"]) == 100.0


def test_connector_profile_can_change_band_and_targets(tmp_path: Path) -> None:
    s2p = tmp_path / "profiled.s2p"
    write_db_s2p(
        s2p,
        [
            (0.5, -8.0, -2.0, -2.0, -8.0),
            (1.0, -20.0, -0.1, -0.1, -20.0),
            (2.0, -20.0, -0.2, -0.2, -20.0),
        ],
    )

    row = score_s2p(s2p, ConnectorScoreProfile(band_min_ghz=1.0, band_max_ghz=2.0))

    assert row["band_min_ghz"] == "1"
    assert row["band_max_ghz"] == "2"
    assert row["worst_return_0p5_10g_db"] == "-20.00"
    assert row["optimization_cost"] == "0.000"


def test_read_s2p_db_returns_normalized_trace_rows(tmp_path: Path) -> None:
    s2p = tmp_path / "trace.s2p"
    write_db_s2p(s2p, [(1.0, -10.0, -1.0, -1.0, -11.0)])

    rows = read_s2p_db(s2p)

    assert rows == [pytest.approx((1.0, -10.0, -1.0, -1.0, -11.0))]
