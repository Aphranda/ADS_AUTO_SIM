import importlib.util
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from simads.hfss.layout_io import load_layout
from simads.hfss.layout_cleanup import (
    generated_optional_delete_names,
    resolve_existing_delete_names_and_prefixes,
)
from simads.hfss.ports import delete_schematic_iports_by_name

def _load_replace_module(monkeypatch):
    monkeypatch.setenv("SIMADS_AEDT_USE_WORKSPACE_USER_DIRS", "False")
    module_path = Path("tools/hfss/replace_hfss3dlayout_layout_primitives.py")
    spec = importlib.util.spec_from_file_location("replace_hfss3dlayout_layout_primitives", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_delete_module(monkeypatch):
    monkeypatch.setenv("SIMADS_AEDT_USE_WORKSPACE_USER_DIRS", "False")
    module_path = Path("tools/hfss/delete_hfss3dlayout_layout_primitives.py")
    spec = importlib.util.spec_from_file_location("delete_hfss3dlayout_layout_primitives", module_path)
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
        delete_extra_name=[],
        delete_extra_prefix=[],
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
        "allowed_geometry_boolean_scope": "none",
        "reference_ground_cutout_handling": "delete_stale_objects_only_do_not_create_or_subtract",
    }
    assert "hfss_ground_plane" in payload["requested_delete_names"]
    assert "p1_l2_cutout_rect" in payload["requested_delete_names"]
    assert "clip_frame" in payload["requested_delete_names"]
    assert any("full delete/rebuild" in note for note in payload["notes"])


def test_replace_layout_parser_closes_aedt_by_default(monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    args = module.parse_args(
        [
            "--project",
            "fixture.aedt",
            "--design",
            "SINGLE_END_SMA_CPW_30MM",
            "--layout",
            "layout.json",
        ]
    )

    assert args.close_projects is True
    assert args.close_desktop is True


def test_replace_layout_parser_accepts_bfp_real_board_scope(monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    args = module.parse_args(
        [
            "--project",
            "fixture.aedt",
            "--design",
            "BFP",
            "--layout",
            "layout.json",
            "--scope",
            "bfp-real-board-full",
        ]
    )

    assert args.scope == "bfp-real-board-full"
    assert args.recreate_pcb_output_port is False


def test_bfp_real_board_scope_selects_full_source_layout(tmp_path: Path, monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    layout_path = tmp_path / "layout.json"
    layout_path.write_text(
        """
{
  "ports": [{"number": 1, "x": 0.0, "y": 0.0}, {"number": 2, "x": 10.0, "y": 0.0}],
  "shapes": [
    {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "boundary", "x": 0.0, "y": -1.0, "w": 10.0, "h": 2.0},
    {"kind": "polygon", "layer": "cond", "name": "input_feed", "points": [[0.0, 0.0], [1.0, 0.0], [1.0, 0.2]]},
    {"kind": "via", "layer": "pcvia1", "name": "via_1", "x": 0.5, "y": 0.5, "diameter": 0.2}
  ]
}
""".strip(),
        encoding="utf-8",
    )
    args = Namespace(
        project=tmp_path / "fixture.aedt",
        design="BFP",
        layout=layout_path,
        scope="bfp-real-board-full",
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
        execute=False,
        save=False,
    )

    payload = module.replace_layout_primitives(args)

    assert payload["status"] == "dry_run"
    assert payload["scope"] == "bfp-real-board-full"
    assert payload["selected_shape_names"] == ["boundary", "input_feed", "via_1"]
    assert payload["pcb_output_port"]["recreate"] is False


def test_replace_layout_parser_accepts_extra_clip_frame_cleanup(monkeypatch) -> None:
    module = _load_replace_module(monkeypatch)
    args = module.parse_args(
        [
            "--project",
            "fixture.aedt",
            "--design",
            "SINGLE_END_SMA_CPW_30MM",
            "--layout",
            "layout.json",
            "--delete-extra-name",
            "my_cut_frame",
            "--delete-extra-prefix",
            "manual_clip_",
        ]
    )

    assert args.delete_extra_name == ["my_cut_frame"]
    assert args.delete_extra_prefix == ["manual_clip_"]


def test_clip_frame_names_are_lifecycle_delete_targets() -> None:
    names = generated_optional_delete_names()

    assert "clip_frame" in names
    assert "board_cut_box" in names


def test_clip_frame_prefix_matches_aedt_renamed_objects() -> None:
    existing = {"clip_frame1", "manual_clip_17", "input_feed", "SMA_KE_Unite_Small_Solder4"}
    resolved = resolve_existing_delete_names_and_prefixes(
        existing,
        ["input_feed"],
        ["clip_frame", "manual_clip_"],
    )

    assert resolved == ["input_feed", "clip_frame1", "manual_clip_17"]


def test_delete_layout_parser_closes_aedt_by_default(monkeypatch) -> None:
    module = _load_delete_module(monkeypatch)
    args = module.parse_args(
        [
            "--project",
            "fixture.aedt",
            "--design",
            "SINGLE_END_SMA_CPW_30MM",
            "--layout",
            "layout.json",
        ]
    )

    assert args.close_projects is True
    assert args.close_desktop is True


def test_delete_layout_parser_accepts_extra_clip_frame_cleanup(monkeypatch) -> None:
    module = _load_delete_module(monkeypatch)
    args = module.parse_args(
        [
            "--project",
            "fixture.aedt",
            "--design",
            "SINGLE_END_SMA_CPW_30MM",
            "--layout",
            "layout.json",
            "--delete-extra-name",
            "my_cut_frame",
            "--delete-extra-prefix",
            "manual_clip_",
        ]
    )

    assert args.delete_extra_name == ["my_cut_frame"]
    assert args.delete_extra_prefix == ["manual_clip_"]


def test_load_layout_accepts_utf8_bom(tmp_path: Path) -> None:
    layout_path = tmp_path / "layout.json"
    layout_path.write_text("\ufeff{\"shapes\": []}\n", encoding="utf-8")

    assert load_layout(layout_path) == {"shapes": []}


def test_delete_schematic_iports_by_name_matches_aedt_suffix() -> None:
    class Editor:
        def __init__(self) -> None:
            self.ports = ["IPort@S1_1_Pin_T1;12", "IPort@Port1;8"]
            self.deleted = None

        def GetAllPorts(self):
            return list(self.ports)

        def Delete(self, selection):
            self.deleted = selection
            selected = set(selection[selection.index("Selections:=") + 1])
            self.ports = [port for port in self.ports if port not in selected]
            return None

    editor = Editor()
    app = SimpleNamespace(odesign=SimpleNamespace(SetActiveEditor=lambda name: editor))

    result = delete_schematic_iports_by_name(app, ["Port1"])

    assert result["deleted"] is True
    assert result["selected"] == ["IPort@Port1;8"]
    assert result["after"] == ["IPort@S1_1_Pin_T1;12"]
