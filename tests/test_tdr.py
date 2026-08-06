from pathlib import Path

from simads.scoring.tdr import compute_tdr_points, summarize_tdr, write_tdr_csv


def write_constant_s2p(path: Path, gamma: float, *, count: int = 20) -> None:
    lines = ["# GHz RI R 50"]
    for index in range(1, count + 1):
        freq = index * 0.05
        lines.append(f"{freq:g} {gamma:g} 0 0 0 0 0 {gamma:g} 0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_constant_reflection_tdr_impedance(tmp_path: Path) -> None:
    s2p = tmp_path / "constant.s2p"
    write_constant_s2p(s2p, 0.2, count=128)

    points = compute_tdr_points(s2p, time_max_ns=1.0, n_fft=256)

    assert points
    assert abs(points[-1].s11_z_ohm - 75.0) < 1e-9
    assert abs(points[-1].s22_z_ohm - 75.0) < 1e-9


def test_write_tdr_csv_and_summary(tmp_path: Path) -> None:
    s2p = tmp_path / "constant.s2p"
    write_constant_s2p(s2p, -0.2)
    points = compute_tdr_points(s2p, time_max_ns=1.0, n_fft=256)
    out = tmp_path / "tdr.csv"

    written = write_tdr_csv(points, out)
    summary = summarize_tdr(points)

    assert written == out
    assert out.read_text(encoding="utf-8").startswith("time_ns,s11_rho")
    assert summary["s11_z_min_ohm"] <= 50.0
