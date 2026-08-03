from tools.ads.ads_inspect_layout_ports import render_markdown, snapshot_term


class FakeInfo:
    def __init__(self, term_name: str, is_positive: bool) -> None:
        self.term_name = term_name
        self.is_positive = is_positive


class FakeNet:
    name = "P1"


class FakeTerm:
    name = "P1"
    number = 0
    term_type = "InputOutput"
    is_implicit = False
    is_delta_gap_port = False
    ref_plane_shift_dbu = 0
    ref_plane_shift_meters = 0.0
    net = FakeNet()
    secondary_term_info = [FakeInfo("P1_GND", False)]
    parameters = []
    props = []
    pins = []


def test_snapshot_term_expands_secondary_term_info() -> None:
    data = snapshot_term(FakeTerm())

    assert data["name"] == "P1"
    assert data["net"] == "P1"
    assert data["secondary_term_info"][0]["term_name"] == "P1_GND"
    assert data["secondary_term_info"][0]["is_positive"] is False


def test_render_markdown_includes_layout_and_em_setup_reference() -> None:
    markdown = render_markdown(
        {
            "generated_at": "2026-08-03T00:00:00",
            "python": "ads-python",
            "target": {"library": "lib", "cell": "cell", "view": "layout"},
            "terms": [
                {
                    "name": "P1",
                    "net": "P1",
                    "is_delta_gap_port": False,
                    "secondary_term_info": [],
                    "pins": [],
                }
            ],
            "em_setup": {
                "canonical_em_state": {
                    "path": "emStateFile.xml",
                    "exists": True,
                    "ports": [{"portName": "P1", "gndLayer": "1001"}],
                }
            },
        }
    )

    assert "Target: `lib:cell:layout`" in markdown
    assert "- `P1`: net=`P1`" in markdown
    assert "gndLayer=`1001`" in markdown
