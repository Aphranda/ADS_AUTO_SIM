from argparse import Namespace

from simads.hfss.ports import resolve_gnd_boundary, resolve_port_edges


def sample_layout() -> dict:
    return {
        "layout_id": "sample",
        "units": "mm",
        "metadata": {
            "substrate": "FR4_210UM",
            "er": 4.6,
            "dielectric_height_mm": 0.21,
            "copper_thickness_mm": 0.035,
        },
        "ports": [
            {"number": 1, "x": -3.0, "y": 0.2},
            {"number": 2, "x": 3.0, "y": 0.2},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": -5.0, "y": -0.1, "w": 10.0, "h": 5.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": -3.0, "y": 0.0, "w": 1.0, "h": 0.4},
            {"kind": "rect", "layer": "cond", "name": "output_feed", "x": 2.0, "y": 0.0, "w": 1.0, "h": 0.4},
        ],
    }


def test_port_edges_reference_ground_below_ports() -> None:
    edges = resolve_port_edges(sample_layout(), None, None, None, None)

    assert edges["p1_edge"] == 1
    assert edges["p2_edge"] == 3
    assert edges["p1_side"] == "left"
    assert edges["p2_side"] == "right"
    assert edges["p1_ref_side"] == "bottom"
    assert edges["p2_ref_side"] == "bottom"


def test_gnd_boundary_can_align_to_port_cross_sections() -> None:
    args = Namespace(gnd_boundary_mode="port-edges")

    boundary = resolve_gnd_boundary(sample_layout(), args)

    assert boundary["x"] == -3.0
    assert boundary["w"] == 6.0
    assert boundary["metadata"]["gnd_boundary_mode"] == "port-edges"
