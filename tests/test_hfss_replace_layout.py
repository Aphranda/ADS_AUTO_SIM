import importlib.util
from argparse import Namespace
from pathlib import Path


def _load_replace_module(monkeypatch):
    monkeypatch.setenv("SIMADS_AEDT_USE_WORKSPACE_USER_DIRS", "False")
    module_path = Path("tools/hfss/replace_hfss3dlayout_layout_primitives.py")
    spec = importlib.util.spec_from_file_location("replace_hfss3dlayout_layout_primitives", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_replace_layout_dry_run_declares_full_rebuild_policy(tmp_path: Path, monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    layout_path = tmp_path / "layout.json"
    layout_path.write_text(
        """
{
  "ports": [{"number": 1, "x": 0.0, "y": 0.0}, {"number": 2, "x": 10.0, "y": 0.0}],
  "shapes": [
    {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": 0.0, "y": -1.0, "w": 10.0, "h": 2.0},
    {"kind": "rect", "layer": "ETCH_TOP", "name": "input_feed", "x": 0.0, "y": -0.1, "w": 1.0, "h": 0.2},
    {"kind": "reference_ground_cutout", "layer": "ETCH_INNER1", "name": "p1_l2_cutout_rect", "x": 0.0, "y": -0.5, "w": 2.0, "h": 1.0}
  ]
}
""".strip(),
        encoding="utf-8",
    )
    args = Namespace(
        project=tmp_path / "fixture.aedt",
        design="SINGLE_END_SMA_CPW_30MM",
        layout=layout_path,
        scope="single-p1-pcb-full",
        gnd_boundary_mode="port-edges",
        signal_layer="ETCH_TOP",
        reference_ground_layer="ETCH_INNER1",
        via_top_layer="ETCH_TOP",
        via_bottom_layer="ETCH_BOTTOM",
        ground_plane_name="hfss_ground_plane",
        recreate_pcb_output_port=True,
        delete_pcb_port_name=["Port1"],
        execute=False,
        save=False,
    )

    payload = module.replace_layout_primitives(args)

    assert payload["status"] == "dry_run"
    assert payload["workflow"] == "delete_source_layout_draw_new_layout_recreate_pcb_output_port"
    assert payload["layout_update_policy"] == {
        "mode": "full_source_layout_rebuild",
        "candidate_level_boolean_ops": False,
        "candidate_level_incremental_ops": False,
        "allowed_geometry_boolean_scope": "inside_create_geometry_only_for_declared_layout_json_shapes",
    }
    assert "hfss_ground_plane" in payload["requested_delete_names"]
    assert "p1_l2_cutout_rect" in payload["requested_delete_names"]
    assert any("full delete/rebuild" in note for note in payload["notes"])
