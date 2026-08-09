from simads.geometry import Boundary, Polygon, Rect, Via
from simads.hfss.layout_io import layout_to_geometry


def test_layout_to_geometry_converts_common_layout_shapes() -> None:
    layout = {
        "layout_id": "example",
        "units": "mm",
        "layers": [{"name": "cond", "purpose": "drawing"}],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": 0, "y": 0, "w": 2, "h": 1},
            {"kind": "rect", "layer": "cond", "name": "feed", "x": 0.0, "y": 0.4, "w": 0.5, "h": 0.2},
            {"kind": "polygon", "layer": "cond", "name": "finger", "points": [[1, 0], [2, 0], [2, 1]]},
            {"kind": "via", "layer": "pcvia1", "name": "via_1", "x": 1.0, "y": 0.5, "diameter": 0.2, "pad_diameter": 0.4},
        ],
    }

    geometry = layout_to_geometry(layout)

    assert geometry.layout_id == "example"
    assert [type(shape) for shape in geometry.shapes] == [Boundary, Rect, Polygon, Via]
    assert geometry.shapes[3].pad_diameter == 0.4
