from pathlib import Path

import pytest

from simads.scoring.systems import SCORING_SYSTEM_SPECS, get_scoring_system_spec
from simads.scoring.touchstone import read_s2p_network, read_s3p_network, read_s4p_network, read_s5p_network, read_s6p_network


def write_db_snp(path: Path, nports: int) -> None:
    values = ["1.0"]
    for source in range(1, nports + 1):
        for response in range(1, nports + 1):
            values.extend([f"-{10 * response + source}", "0"])
    path.write_text("# GHZ S DB R 50\n" + " ".join(values) + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("nports", "reader"),
    [
        (2, read_s2p_network),
        (3, read_s3p_network),
        (4, read_s4p_network),
        (5, read_s5p_network),
        (6, read_s6p_network),
    ],
)
def test_sparameter_network_supports_s2p_to_s6p(tmp_path: Path, nports: int, reader) -> None:
    path = tmp_path / f"network.s{nports}p"
    write_db_snp(path, nports)

    network = reader(path)

    assert network.nports == nports
    assert network.frequency_ghz == [1.0]
    assert network.db(f"s{nports}1") == pytest.approx([-(10 * nports + 1)])


def test_sparameter_network_rejects_wrong_fixed_port_count(tmp_path: Path) -> None:
    path = tmp_path / "wrong.s3p"
    write_db_snp(path, 3)

    with pytest.raises(ValueError, match="suffix/reader mismatch"):
        read_s2p_network(path)


def test_sparameter_network_validates_system_port_count(tmp_path: Path) -> None:
    path = tmp_path / "wrong.s4p"
    write_db_snp(path, 4)

    network = read_s4p_network(path)
    with pytest.raises(ValueError, match="expected S2P for connector"):
        network.require_nports(2, system="connector")


def test_scoring_system_specs_define_distinct_metric_families() -> None:
    assert get_scoring_system_spec("filter").metric_family == "bandpass_filter"
    assert get_scoring_system_spec("connector").primary_metrics == (
        "s21_insertion_loss",
        "s21_extra_loss_vs_baseline",
        "s11_s22_return_loss",
        "s11_s22_weighted_balance",
        "smith_impedance_hint",
    )
    assert get_scoring_system_spec("sp8t").primary_metrics == (
        "s21_s43_through_loss",
        "s21_s43_extra_loss_vs_baseline",
        "s11_s22_s33_s44_return_loss",
        "near_end_isolation_s31_s13",
        "far_end_isolation_s42_s24",
        "diagonal_isolation_s41_s14_s32_s23",
    )
    assert {spec.touchstone_suffix for spec in SCORING_SYSTEM_SPECS.values()} == {"s2p", "s4p"}
