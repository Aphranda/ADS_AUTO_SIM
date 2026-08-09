#!/usr/bin/env python3
"""Duplicate an HFSS 3D Layout design through AEDT/PyAEDT APIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import OperationLifecycle, apply_grpc_startup_compat
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def _json_default(value: Any) -> str:
    return str(value)


def _clean_design_name(name: Any) -> str:
    text = str(name)
    if ";" in text and text.split(";", 1)[0].isdigit():
        return text.split(";", 1)[1]
    return text


def _design_list(app: Any) -> list[str]:
    names = getattr(app, "design_list", None)
    if names:
        return [_clean_design_name(name) for name in names]
    try:
        raw = app.oproject.GetTopDesignList()
    except Exception:
        raw = []
    return [_clean_design_name(name) for name in raw]


def _set_active_design(app: Any, design: str) -> None:
    if hasattr(app, "set_active_design"):
        app.set_active_design(design)
        return
    app.oproject.SetActiveDesign(design)


def _delete_design(app: Any, design: str) -> Any:
    if hasattr(app, "delete_design"):
        return app.delete_design(design)
    return app.oproject.DeleteDesign(design)


def _duplicate_design(app: Any, target_design: str, *, save_after_duplicate: bool) -> Any:
    if hasattr(app, "duplicate_design"):
        return app.duplicate_design(target_design, save_after_duplicate=save_after_duplicate)
    app.oproject.CopyDesign(app.design_name)
    app.oproject.Paste()
    if hasattr(app, "rename_design"):
        return app.rename_design(target_design, save_after_duplicate=save_after_duplicate)
    return True


def duplicate_design(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle(
        "duplicate_hfss3dlayout_design",
        output=event_log_path_for_json(args.output) if getattr(args, "output", None) else None,
    )
    payload: dict[str, Any] = {
        "project": str(args.project),
        "source_design": args.source_design,
        "target_design": args.target_design,
        "delete_existing": bool(args.delete_existing),
        "execute": bool(args.execute),
        "save": bool(args.save),
    }
    if not args.execute:
        payload["status"] = "dry_run"
        payload["lifecycle"] = lifecycle.finish(status="dry_run")
        return payload

    final_lifecycle_status = "failed"
    try:
        session_config = Hfss3dLayoutSessionConfig(
            label="duplicate_hfss3dlayout_design",
            project=args.project,
            design=args.source_design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=args.new_desktop,
            close_on_exit=False,
            keep_open=args.keep_open,
            close_projects=args.close_projects,
            close_desktop=args.close_desktop,
            remove_lock=args.remove_lock,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            app = session.app
            payload.update(session.metadata())
            with lifecycle.timed("read_designs_before"):
                before = _design_list(app)
            payload["designs_before"] = before
            if args.source_design not in before:
                payload["status"] = "missing_source_design"
                final_lifecycle_status = "failed"
                return payload
            if args.target_design in before:
                if not args.delete_existing:
                    payload["status"] = "target_design_exists"
                    final_lifecycle_status = "blocked"
                    return payload
                with lifecycle.timed("delete_existing_target_design"):
                    payload["delete_existing_result"] = _delete_design(app, args.target_design)
            with lifecycle.timed("activate_source_design"):
                _set_active_design(app, args.source_design)
            with lifecycle.timed("duplicate_design"):
                payload["duplicate_result"] = _duplicate_design(
                    app,
                    args.target_design,
                    save_after_duplicate=bool(args.save_after_duplicate),
                )
            with lifecycle.timed("read_designs_after"):
                after = _design_list(app)
            payload["designs_after"] = after
            payload["created_design_detected"] = args.target_design in after
            if not payload["created_design_detected"]:
                payload["status"] = "duplicate_missing_target"
                final_lifecycle_status = "failed"
                return payload
            if args.save:
                with lifecycle.timed("save_aedt_project"):
                    payload["saved"] = bool(app.save_project(str(args.project), overwrite=True))
            payload["status"] = "duplicated"
            final_lifecycle_status = "ok"
            return payload
    finally:
        if "lifecycle" not in payload:
            payload["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Duplicate an HFSS 3D Layout design through AEDT/PyAEDT APIs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--source-design", required=True)
    parser.add_argument("--target-design", required=True)
    parser.add_argument("--delete-existing", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--save-after-duplicate", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--close-projects", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--close-desktop", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    payload = duplicate_design(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "duplicated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
