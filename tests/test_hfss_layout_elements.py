from argparse import Namespace
import importlib.util
import json
from pathlib import Path

from simads.hfss.filter_core import FILTER_CORE_SCOPE, filter_core_policy, filter_core_shapes
from simads.hfss.layout_elements import (
    LayoutElementPolicy,
    candidate_layout_for_policy,
    select_layout_elements,
)


def _load_replace_module(monkeypatch):
    monkeypatch.setenv("SIMADS_AEDT_USE_WORKSPACE_USER_DIRS", "False")
    module_path = Path("tools/hfss/replace_hfss3dlayout_layout_primitives.py")
    spec = importlib.util.spec_from_file_location("replace_hfss3dlayout_layout_primitives", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _layout() -> dict:
    return {
        "metadata": {"editable_regions": {"filter_core_bbox_mm": [91.6, 87.1, 95.3, 93.4]}},
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "em_boundary", "x": 78.0, "y": 80.0, "w": 30.0, "h": 20.0},
            {
                "kind": "polygon",
                "layer": "cond",
                "name": "filter_core_finger_1",
                "points": [[92.0, 88.0], [93.0, 88.0], [93.0, 89.0]],
                "metadata": {"role": "signal_filter_core"},
            },
            {
                "kind": "polygon",
                "layer": "cond",
                "name": "input_feed",
                "points": [[89.0, 88.0], [90.0, 88.0], [90.0, 89.0]],
                "metadata": {"role": "signal_feed"},
            },
            {"kind": "via", "layer": "pcvia1", "name": "ground_via_1", "x": 92.4, "y": 88.4, "diameter": 0.2, "metadata": {"role": "ground_via"}},
            {"kind": "reference_ground_plane", "layer": "reference_ground_plane", "name": "solid_gnd", "x": 78.0, "y": 80.0, "w": 30.0, "h": 20.0},
        ],
    }


def test_layout_element_policy_selects_by_role() -> None:
    policy = LayoutElementPolicy(include_roles=("signal_filter_core",))

    selected = select_layout_elements(_layout(), policy)

    assert [shape["name"] for shape in selected] == ["filter_core_finger_1"]


def test_layout_element_policy_selects_by_editable_region_with_excludes() -> None:
    policy = LayoutElementPolicy(
        include_regions=("filter_core_bbox_mm",),
        include_kinds=("polygon",),
        exclude_roles=("signal_feed",),
    )

    selected = select_layout_elements(_layout(), policy)

    assert [shape["name"] for shape in selected] == ["filter_core_finger_1"]


def test_filter_core_calls_generic_element_selector() -> None:
    selected = filter_core_shapes(_layout())

    assert [shape["name"] for shape in selected] == ["filter_core_finger_1"]
    assert filter_core_policy().suppress_default_reference_ground_plane is True


def test_candidate_layout_for_policy_keeps_boundary_as_context_and_suppresses_default_ground() -> None:
    policy = LayoutElementPolicy(include_roles=("signal_filter_core",), suppress_default_reference_ground_plane=True)

    candidate = candidate_layout_for_policy(_layout(), policy, layout_scope=FILTER_CORE_SCOPE)

    assert [shape["name"] for shape in candidate["shapes"]] == ["em_boundary", "filter_core_finger_1"]
    assert candidate["metadata"]["suppress_default_reference_ground_plane"] is True
    assert candidate["metadata"]["layout_element_policy"]["include"]["roles"] == ["signal_filter_core"]


def test_replace_layout_dry_run_with_element_policy_deletes_and_draws_only_selected_elements(tmp_path: Path, monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    layout_path = tmp_path / "layout.json"
    policy_path = tmp_path / "policy.json"
    layout_path.write_text(json.dumps(_layout(), ensure_ascii=False), encoding="utf-8")
    policy_path.write_text(
        json.dumps(
            {
                "include": {"roles": ["signal_filter_core"]},
                "draw": {"suppress_default_reference_ground_plane": True},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = Namespace(
        project=tmp_path / "fixture.aedt",
        design="BFP",
        layout=layout_path,
        scope="layout-elements",
        element_policy=policy_path,
        gnd_boundary_mode="em-boundary",
        signal_layer="ETCH_TOP",
        reference_ground_layer="ETCH_INNER1",
        via_top_layer="ETCH_TOP",
        via_bottom_layer="ETCH_BOTTOM",
        ground_plane_name="hfss_ground_plane",
        recreate_pcb_output_port=False,
        delete_pcb_port_name=[],
        delete_extra_name=[],
        delete_extra_prefix=[],
        include_sibling_layouts=False,
        execute=False,
        save=False,
    )

    payload = module.replace_layout_primitives(args)

    assert payload["status"] == "dry_run"
    assert payload["selected_shape_names"] == ["filter_core_finger_1"]
    assert payload["requested_delete_names"] == ["filter_core_finger_1"]
    assert "hfss_ground_plane" not in payload["requested_delete_names"]
    assert "input_feed" not in payload["requested_delete_names"]
    assert "ground_via_1" not in payload["requested_delete_names"]
