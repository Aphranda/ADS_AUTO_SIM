import importlib.util
from pathlib import Path


def load_scorer():
    path = Path(__file__).resolve().parents[1] / "tools" / "score_tx_band_filter.py"
    spec = importlib.util.spec_from_file_location("score_tx_band_filter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_trace(path: Path, *, high_return_db: float) -> None:
    rows = [
        (14.40, -20.0, -45.0, -20.0),
        (15.00, -20.0, -45.0, -20.0),
        (17.70, -12.0, -3.0, -12.0),
        (18.20, -12.0, -2.5, -12.0),
        (18.80, high_return_db, -2.6, high_return_db),
        (19.325, high_return_db, -3.0, high_return_db),
        (23.00, -20.0, -45.0, -20.0),
    ]
    with path.open("w", encoding="utf-8", newline="") as fp:
        fp.write("freq_ghz,s11_db,s21_db,s22_db\n")
        for freq, s11, s21, s22 in rows:
            fp.write(f"{freq},{s11},{s21},{s22}\n")


def test_tx_band_score_penalizes_high_frequency_return_loss(tmp_path: Path) -> None:
    scorer = load_scorer()
    good = tmp_path / "good_trace.csv"
    weak_high = tmp_path / "weak_high_trace.csv"
    write_trace(good, high_return_db=-12.0)
    write_trace(weak_high, high_return_db=-5.0)

    good_score = scorer.score_trace(good, "good")
    weak_score = scorer.score_trace(weak_high, "weak_high")

    assert float(good_score["tx_score"]) > float(weak_score["tx_score"]) + 200.0
    assert weak_score["worst_high_return_loss_db"] == "-5.0000"
    assert weak_score["high_return_loss_margin_db"] == "-5.0000"
    assert "high-frequency return loss is not acceptable" in weak_score["note"]
