from pathlib import Path

import pytest

from simads.scoring.interface import score_sparameter_file
from simads.scoring.sp8t import read_touchstone4, score_touchstone, write_trace_csv


S4P_ORDER = (
    "s11",
    "s21",
    "s31",
    "s41",
    "s12",
    "s22",
    "s32",
    "s42",
    "s13",
    "s23",
    "s33",
    "s43",
    "s14",
    "s24",
    "s34",
    "s44",
)


def write_db_s4p(path: Path, rows: list[tuple[float, dict[str, float]]]) -> None:
    lines = ["# GHZ S DB R 50"]
    for freq, values in rows:
        items = [f"{freq}"]
        for name in S4P_ORDER:
            items.extend([f"{values.get(name, -80.0)}", "0"])
        lines.append(" ".join(items))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_values(**overrides: float) -> dict[str, float]:
    values = {
        "s11": -20.0,
        "s22": -19.0,
        "s33": -21.0,
        "s44": -18.0,
        "s21": -0.25,
        "s43": -0.35,
        "s12": -0.25,
        "s34": -0.35,
        "s31": -42.0,
        "s41": -40.0,
        "s32": -43.0,
        "s42": -41.0,
        "s13": -42.0,
        "s14": -40.0,
        "s23": -43.0,
        "s24": -41.0,
    }
    values.update(overrides)
    return values


def test_read_touchstone4_preserves_touchstone_column_major_order(tmp_path: Path) -> None:
    s4p = tmp_path / "sp8t.s4p"
    write_db_s4p(s4p, [(1.0, clean_values(s21=-1.0, s43=-2.0, s31=-33.0))])

    row = read_touchstone4(s4p)[0]

    assert row["freq_ghz"] == pytest.approx(1.0)
    assert abs(row["s21"]) == pytest.approx(10 ** (-1.0 / 20.0))
    assert abs(row["s43"]) == pytest.approx(10 ** (-2.0 / 20.0))
    assert abs(row["s31"]) == pytest.approx(10 ** (-33.0 / 20.0))


def test_sp8t_score_includes_isolation_metrics(tmp_path: Path) -> None:
    s4p = tmp_path / "clean.s4p"
    write_db_s4p(
        s4p,
        [
            (0.5, clean_values()),
            (5.0, clean_values(s21=-0.45, s43=-0.55, s41=-32.0)),
            (10.0, clean_values(s21=-0.65, s43=-0.75, s24=-31.0)),
        ],
    )

    row = score_touchstone(s4p)

    assert row["status"] == "PASS_CANDIDATE"
    assert row["worst_isolation_param"] == "s24"
    assert row["worst_isolation_0p5_10g_db"] == "-31.00"
    assert row["through_min_0p5_10g_db"] == "-0.75"
    assert float(row["sp8t_score"]) > 95.0


def test_sp8t_unified_scoring_profile_loads_default_config(tmp_path: Path) -> None:
    s4p = tmp_path / "default_profile.s4p"
    write_db_s4p(s4p, [(1.0, clean_values(s41=-28.0))])

    row = score_sparameter_file(
        s4p,
        system="sp8t",
        profile_id="sp8t_four_port_connector_isolation_0p5_10g_v1",
    )

    assert row["scoring_system"] == "sp8t"
    assert row["score_version"] == "sp8t_four_port_connector_isolation_v1"
    assert row["worst_isolation_param"] == "s41"
    assert float(row["optimization_cost"]) > 0.0


def test_sp8t_trace_csv_contains_worst_isolation(tmp_path: Path) -> None:
    s4p = tmp_path / "trace.s4p"
    trace = tmp_path / "trace.csv"
    write_db_s4p(s4p, [(1.0, clean_values(s31=-34.0))])

    write_trace_csv(read_touchstone4(s4p), trace)

    text = trace.read_text(encoding="utf-8")
    assert "worst_isolation_db" in text
    assert "s43_db" in text
