from pathlib import Path

from simads.exporters.svg import write_svg
from simads.geometry import Boundary, Layout, Polygon, Rect, Via


def test_bfp_element_review_svg_renders_only_l1_l2(tmp_path: Path) -> None:
    layout = Layout(
        layout_id="bfp_core_y_offset_p0p10",
        metadata={"layout_scope": "layout-elements"},
        shapes=[
            Boundary(name="em_boundary", x=0, y=0, w=10, h=4),
            Polygon(
                name="top_filter",
                layer="cond",
                points=[(1, 1), (3, 1), (3, 2), (1, 2)],
                metadata={"source_layer": "TOP"},
            ),
            Via(name="via_1", layer="pcvia1", x=2, y=1.5, diameter=0.2, metadata={"source_layer": "TOP"}),
            Rect(
                name="inner1_gnd",
                layer="reference_ground_plane",
                x=0,
                y=0,
                w=10,
                h=4,
                kind="reference_ground_plane",
                metadata={"source_layer": "INNER1", "target_layer": "INNER1"},
            ),
            Rect(
                name="inner2_gnd",
                layer="reference_ground_plane",
                x=0,
                y=0,
                w=10,
                h=4,
                kind="reference_ground_plane",
                metadata={"source_layer": "INNER2", "target_layer": "INNER2"},
            ),
            Rect(
                name="bottom_gnd",
                layer="reference_ground_plane",
                x=0,
                y=0,
                w=10,
                h=4,
                kind="reference_ground_plane",
                metadata={"source_layer": "BOTTOM", "target_layer": "BOTTOM"},
            ),
        ],
    )

    out = tmp_path / "layout.svg"
    write_svg(out, layout)
    svg = out.read_text(encoding="utf-8")

    assert "L1 TOP" in svg
    assert "L2 INNER1" in svg
    assert "top_filter" in svg
    assert "inner1_gnd" in svg
    assert "via_1" in svg
    assert "inner2_gnd" not in svg
    assert "bottom_gnd" not in svg
    assert "L3" not in svg
    assert "L4" not in svg
