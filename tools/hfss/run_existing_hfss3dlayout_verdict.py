#!/usr/bin/env python3
"""Analyze an existing HFSS 3D Layout project and export S-parameters."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
AEDT_VERSION = "2026.1"
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.aedt_startup import (
    OperationLifecycle,
    apply_grpc_startup_compat,
    stable_export_touchstone,
)
from simads.hfss.results import run_post_tools as run_hfss_post_tools
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def run_post_tools(
    s2p: Path,
    score_csv: Path,
    out_dir: Path,
    candidate: str,
    profile: str,
    lifecycle: OperationLifecycle | None = None,
    scoring_profile_id: str | None = None,
    scoring_profile_path: Path | None = None,
    baseline_s2p: Path | None = None,
) -> dict[str, str]:
    trace_csv = out_dir / f"{candidate}_trace.csv"
    return run_hfss_post_tools(
        s2p,
        score_csv,
        trace_csv,
        out_dir / "svg",
        candidate,
        profile=profile,
        scoring_profile_id=scoring_profile_id,
        scoring_profile_path=scoring_profile_path,
        baseline_s2p=baseline_s2p,
        lifecycle=lifecycle,
    )


def object_names(items: Any) -> list[str]:
    names: list[str] = []
    for item in items or []:
        names.append(getattr(item, "name", str(item)))
    return names


def _safe_messages(app: Any, *, aedt_messages: bool) -> list[str]:
    project_name = str(getattr(app, "project_name", "") or "")
    design_name = str(getattr(app, "design_name", "") or "")
    if aedt_messages:
        try:
            output: list[str] = []
            desktop = getattr(app, "odesktop", None)
            if desktop is not None:
                output.extend(str(message) for message in desktop.GetMessages("", "", 0))
                if project_name:
                    output.extend(str(message) for message in desktop.GetMessages(project_name, "", 0))
                if project_name and design_name:
                    output.extend(str(message) for message in desktop.GetMessages(project_name, design_name, 0))
            unique: list[str] = []
            for message in output:
                if message not in unique:
                    unique.append(message)
            return unique
        except Exception as exc:
            return [f"failed to read AEDT messages: {type(exc).__name__}: {exc}"]
    try:
        messages = app.logger.get_messages(
            project_name,
            design_name,
            level=0,
            aedt_messages=False,
        )
        return [str(message) for message in messages]
    except Exception as exc:
        return [f"failed to read messages: {type(exc).__name__}: {exc}"]


def run(args: argparse.Namespace) -> dict[str, Any]:
    lifecycle = OperationLifecycle(
        "run_existing_hfss3dlayout_verdict",
        output=args.output.with_suffix(".events.jsonl") if getattr(args, "output", None) else None,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    app = None
    result: dict[str, Any] | None = None
    session_metadata: dict[str, Any] = {}
    final_lifecycle_status = "failed"
    try:
        session_config = Hfss3dLayoutSessionConfig(
            label="run_existing_hfss3dlayout_verdict",
            project=args.project,
            design=args.design,
            version=args.version,
            non_graphical=args.non_graphical,
            new_desktop=True,
            close_on_exit=not args.keep_open,
            keep_open=args.keep_open,
            close_projects=True,
            close_desktop=True,
            remove_lock=args.remove_lock,
            ready_setup=args.setup,
            ready_sweep=args.sweep,
            ready_timeout_s=args.ready_timeout_s,
            ready_settle_s=args.ready_settle_s,
            reaper_script_started=bool(args.non_graphical),
        )
        with open_hfss3dlayout_session(session_config, lifecycle) as session:
            app = session.app
            session_metadata = session.metadata()
            result = {
                "project": str(args.project),
                "design": args.design,
                **session_metadata,
                "setup": args.setup,
                "sweep": args.sweep,
                "analyze": not args.export_only,
                "status": "running",
            }
            with lifecycle.timed("read_ports"):
                result["ports"] = object_names(getattr(app, "ports", []))
            if not args.export_only:
                result["stage"] = "analyze_setup"
                with lifecycle.timed("analyze_setup", setup=args.setup):
                    result["analyze_return"] = app.analyze_setup(args.setup)
            s2p = args.s2p or args.out_dir / f"{args.candidate}.s2p"
            result["stage"] = "export_touchstone"
            with lifecycle.timed("export_touchstone", attempts=args.export_attempts):
                exported, export_attempts = stable_export_touchstone(
                    app,
                    setup=args.setup,
                    sweep=args.sweep,
                    output_file=str(s2p),
                    attempts=args.export_attempts,
                    delay_s=args.export_retry_delay_s,
                    renormalization=True,
                    impedance=50,
                )
            result["export_attempts"] = export_attempts
            s2p_path = Path(exported or s2p)
            result["s2p"] = str(s2p_path)
            if s2p_path.exists():
                result["stage"] = "postprocess"
                score_csv = args.score_out or args.out_dir / f"{args.candidate}_score.csv"
                result["postprocess_profile"] = args.postprocess_profile
                result.update(
                    run_post_tools(
                        s2p_path,
                        score_csv,
                        args.out_dir,
                        args.candidate,
                        args.postprocess_profile,
                        lifecycle,
                        scoring_profile_id=args.scoring_profile_id,
                        scoring_profile_path=args.scoring_profile_path,
                        baseline_s2p=args.baseline_s2p,
                    )
                )
            result["status"] = "ok"
            result["stage"] = "completed"
            with lifecycle.timed("read_messages"):
                result["messages"] = _safe_messages(app, aedt_messages=False)
                result["aedt_messages"] = _safe_messages(app, aedt_messages=True)
        final_lifecycle_status = "ok"
        return result
    except BaseException as exc:
        result = {
            "project": str(args.project),
            "design": args.design,
            "setup": args.setup,
            "sweep": args.sweep,
            "candidate": args.candidate,
            "status": "failed",
            "stage": locals().get("result", {}).get("stage", "unknown"),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "messages": _safe_messages(app, aedt_messages=False),
            "aedt_messages": _safe_messages(app, aedt_messages=True),
        }
        result.update({key: value for key, value in session_metadata.items() if value is not None})
        final_lifecycle_status = "failed"
        return result
    finally:
        if result is not None and "lifecycle" not in result:
            result["lifecycle"] = lifecycle.finish(status=final_lifecycle_status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run/export an existing HFSS 3D Layout project without rebuilding geometry.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", default="I7_FR4_HFSS_VERDICT")
    parser.add_argument("--version", default=AEDT_VERSION)
    parser.add_argument("--setup", default="Setup_4to10G")
    parser.add_argument("--sweep", default="Sweep_4to10G_40pt")
    parser.add_argument("--candidate", default="hfss_manual_ports")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--s2p", type=Path, default=None)
    parser.add_argument("--score-out", type=Path, default=None)
    parser.add_argument("--postprocess-profile", choices=["connector", "filter"], default="connector")
    parser.add_argument("--scoring-profile-id", default=None)
    parser.add_argument("--scoring-profile-path", type=Path, default=None)
    parser.add_argument("--baseline-s2p", type=Path, default=None)
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--export-attempts", type=int, default=3)
    parser.add_argument("--export-retry-delay-s", type=float, default=3.0)
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if payload.get("status") == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
