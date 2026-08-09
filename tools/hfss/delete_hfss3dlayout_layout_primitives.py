#!/usr/bin/env python3
"""Delete HFSS 3D Layout PCB source primitives and stop before rebuild."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.hfss.aedt_startup import OperationLifecycle, apply_grpc_startup_compat
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.layout_cleanup import (
    delete_layout_objects,
    existing_layout_objects,
    full_rebuild_delete_names,
    resolve_existing_delete_names_and_prefixes,
    sibling_layout_root,
    TEMPORARY_CLIP_FRAME_PREFIXES,
)
from simads.hfss.layout_elements import load_layout_element_policy
from simads.hfss.layout_io import load_layout
from simads.hfss.ports import delete_schematic_iports_by_name, schematic_iport_names
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session
from simads.common import json_default

apply_grpc_startup_compat()


def delete_layout_primitives(args: argparse.Namespace) -> dict[str, object]:
    lifecycle = OperationLifecycle(
        "delete_hfss3dlayout_layout_primitives",
        output=event_log_path_for_json(args.output) if getattr(args, "output", None) else None,
    )
    layout = load_layout(args.layout)
    element_policy_path = getattr(args, "element_policy", None)
    element_policy = load_layout_element_policy(element_policy_path) if element_policy_path else None
    sibling_root = sibling_layout_root(args.layout) if args.include_sibling_layouts else None
    stale_layout_roots = [sibling_root] if sibling_root is not None else []
    requested_delete = full_rebuild_delete_names(
        layout,
        ground_plane_name=args.ground_plane_name,
        scope=args.scope,
        stale_layout_roots=stale_layout_roots,
        element_policy=element_policy,
    )
    for name in getattr(args, "delete_extra_name", []):
        if name and name not in requested_delete:
            requested_delete.append(name)
    delete_prefixes = list(TEMPORARY_CLIP_FRAME_PREFIXES)
    for prefix in getattr(args, "delete_extra_prefix", []):
        if prefix and prefix not in delete_prefixes:
            delete_prefixes.append(prefix)
    is_element_policy_update = element_policy is not None
    payload: dict[str, object] = {
        "project": str(args.project),
        "design": args.design,
        "layout": str(args.layout),
        "scope": args.scope,
        "workflow": "delete_selected_layout_elements_stop_before_rebuild"
        if is_element_policy_update
        else "delete_source_layout_stop_before_rebuild",
        "layout_update_policy": {
            "mode": "element_policy_delete_only" if is_element_policy_update else "delete_only",
            "candidate_level_boolean_ops": False,
            "candidate_level_incremental_ops": False,
            "next_step": "manual_inspection_or_run_replace_to_rebuild",
        },
        "requested_delete_names": requested_delete,
        "delete_name_prefixes": delete_prefixes,
        "element_policy": element_policy.to_mapping() if element_policy is not None else None,
        "stale_layout_roots": [str(path) for path in stale_layout_roots],
        "pcb_output_port": {"delete_port_names": list(args.delete_pcb_port_name)},
        "execute": args.execute,
        "save": args.save,
        "notes": [
            "This tool deletes only source PCB layout primitives and optional PCB edge ports.",
            "Schematic connector instances and connector pin IPorts are never selected by this tool.",
            "No new layout geometry is created by this tool.",
            "Temporary board clip/cut frames are part of source-layout lifecycle cleanup when their names match the configured names or prefixes.",
        ],
    }
    if not args.execute:
        payload["status"] = "dry_run"
        payload["lifecycle"] = lifecycle.finish(status="dry_run")
        return payload

    final_lifecycle_status = "failed"
    try:
        session_config = Hfss3dLayoutSessionConfig(
            label="delete_hfss3dlayout_layout_primitives",
            project=args.project,
            design=args.design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop,
            close_on_exit=False,
            keep_open=args.keep_attached,
            close_projects=args.close_projects,
            close_desktop=args.close_desktop,
            remove_lock=args.remove_lock,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            app = session.app
            payload.update(session.metadata())
            with lifecycle.timed("read_before_ports"):
                payload["before_ports"] = schematic_iport_names(app)
            if args.delete_pcb_port_name:
                with lifecycle.timed("delete_existing_pcb_ports"):
                    payload["pcb_port_delete"] = delete_schematic_iports_by_name(app, list(args.delete_pcb_port_name))
            with lifecycle.timed("inspect_existing_layout_objects"):
                layout_editor = app.odesign.SetActiveEditor("Layout")
                existing = existing_layout_objects(app.modeler, layout_editor)
            payload["existing_candidate_count"] = len(existing)
            payload["existing_before_names"] = sorted(existing)
            delete_existing = resolve_existing_delete_names_and_prefixes(existing, requested_delete, delete_prefixes)
            payload["delete_existing_names"] = delete_existing
            if delete_existing:
                with lifecycle.timed("delete_source_layout_objects", object_count=len(delete_existing)):
                    payload["delete_result"] = delete_layout_objects(layout_editor, delete_existing)
                if not payload["delete_result"]["ok"]:
                    payload["status"] = "delete_failed_no_save"
                    final_lifecycle_status = "failed"
                    return payload
            with lifecycle.timed("inspect_layout_objects_after_delete"):
                existing_after = existing_layout_objects(app.modeler, layout_editor)
            payload["existing_after_delete_names"] = sorted(existing_after)
            payload["source_like_names_after_delete"] = resolve_existing_delete_names_and_prefixes(
                existing_after,
                requested_delete,
                delete_prefixes,
            )
            with lifecycle.timed("read_after_ports"):
                payload["after_ports"] = schematic_iport_names(app)
            if args.save:
                with lifecycle.timed("save_aedt_project"):
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
            payload["status"] = "deleted"
            final_lifecycle_status = "ok"
            return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete HFSS 3D Layout PCB source layout primitives without rebuilding.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument(
        "--scope",
        choices=["single-p1-pcb-full", "bfp-real-board-full", "bfp-filter-core", "layout-elements"],
        default="single-p1-pcb-full",
    )
    parser.add_argument("--element-policy", type=Path, default=None, help="JSON policy selecting layout elements to delete.")
    parser.add_argument("--ground-plane-name", default="hfss_ground_plane")
    parser.add_argument(
        "--delete-pcb-port-name",
        action="append",
        default=[],
        help="Existing schematic IPort name to delete. Repeat if needed. Connector pin IPorts must not be passed here.",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--include-sibling-layouts", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--delete-extra-name", action="append", default=[], help="Additional exact/base layout object name to delete, for example a leftover clip frame.")
    parser.add_argument("--delete-extra-prefix", action="append", default=[], help="Additional layout object name prefix to delete, for example clip_frame_.")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--close-desktop", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    payload = delete_layout_primitives(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
