#!/usr/bin/env python3
"""Analyze an existing HFSS 3D Layout project and export S-parameters."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
import re
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
from simads.hfss.artifact_names import event_log_path_for_json
from simads.hfss.results import run_post_tools as run_hfss_post_tools
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session

apply_grpc_startup_compat()


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return str(value)


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


def _clean_design_name(name: Any) -> str:
    text = str(name)
    if ";" in text and text.split(";", 1)[0].isdigit():
        return text.split(";", 1)[1]
    return text


def _design_names(app: Any) -> list[str]:
    names = getattr(app, "design_list", None)
    if names:
        return [_clean_design_name(name) for name in names]
    try:
        return [_clean_design_name(name) for name in app.oproject.GetTopDesignList()]
    except Exception:
        return []


def _component_info_value(info: list[str], key: str) -> str | None:
    prefix = f"{key}="
    for item in info:
        text = str(item)
        if text.startswith(prefix):
            return text.split("=", 1)[1]
    return None


def _component_names_by_id(editor: Any, *, limit: int = 3000) -> dict[str, list[str]]:
    components: dict[str, list[str]] = {}
    for index in range(1, limit):
        comp_id = str(index)
        try:
            info = [str(item) for item in editor.GetComponentInfo(comp_id)]
        except Exception:
            continue
        if not info:
            continue
        component_name = _component_info_value(info, "ComponentName") or "<unknown>"
        components.setdefault(component_name, []).append(comp_id)
    return components


def _normalize_component_or_design_name(name: str) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"\.(aedt|aedb|snp|s\d+p)$", "", text)
    text = re.sub(r"\d+$", "", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def _component_design_dependencies(app: Any, *, parent_design: str) -> dict[str, Any]:
    available_designs = [name for name in _design_names(app) if name != parent_design]
    design_by_normalized: dict[str, str] = {}
    for design in available_designs:
        design_by_normalized.setdefault(_normalize_component_or_design_name(design), design)

    editor = app.odesign.SetActiveEditor("Layout")
    components_by_name = _component_names_by_id(editor)
    dependencies: list[str] = []
    unmatched: dict[str, list[str]] = {}
    for component_name, ids in sorted(components_by_name.items()):
        normalized = _normalize_component_or_design_name(component_name)
        design = design_by_normalized.get(normalized)
        if design is None:
            unmatched[component_name] = ids
            continue
        if design not in dependencies:
            dependencies.append(design)
    return {
        "components_by_name": components_by_name,
        "available_designs": available_designs,
        "dependencies": dependencies,
        "unmatched_components": unmatched,
    }


def _setup_names(app: Any) -> list[str]:
    for attr in ("setup_names", "existing_analysis_setups"):
        try:
            value = getattr(app, attr)
            items = value() if callable(value) else value
            if items:
                return [str(item) for item in items]
        except Exception:
            continue
    try:
        return [str(item) for item in app.oanalysis.GetSetups()]
    except Exception:
        return []


def _set_active_design(app: Any, design: str) -> None:
    if hasattr(app, "set_active_design"):
        app.set_active_design(design)
        return
    app.oproject.SetActiveDesign(design)


def _raw_set_active_design(app: Any, design: str) -> Any:
    return app.oproject.SetActiveDesign(design)


def _raw_setup_names(odesign: Any) -> list[str]:
    try:
        module = odesign.GetModule("AnalysisSetup")
        return [str(item) for item in module.GetSetups()]
    except Exception:
        return []


def _raw_analyze_design(odesign: Any, setup: str | None) -> Any:
    if setup:
        try:
            return odesign.Analyze(setup)
        except TypeError:
            return odesign.Analyze(setup, True)
    try:
        return odesign.AnalyzeAll()
    except TypeError:
        return odesign.AnalyzeAll(True)


def _validate_design(app: Any, output_dir: Path) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(app, "validate_full_design"):
        try:
            messages, is_valid = app.validate_full_design(output_dir=str(output_dir))
            attempt = {
                "call": "validate_full_design",
                "ok": bool(is_valid),
                "messages": _jsonable(messages),
                "log_file": str(output_dir / "all_validation.log"),
            }
            attempts.append(attempt)
            return {"ok": bool(is_valid), "method": "validate_full_design", "attempts": attempts}
        except Exception as exc:  # pragma: no cover - depends on AEDT COM/gRPC.
            attempts.append({"call": "validate_full_design", "ok": False, "error": f"{type(exc).__name__}: {exc}"})
    log_file = output_dir / "validate_design.log"
    try:
        value = app.odesign.ValidateDesign(str(log_file))
        ok = bool(value)
        attempts.append({"call": "ValidateDesign(log_file)", "ok": ok, "value": _jsonable(value), "log_file": str(log_file)})
        return {"ok": ok, "method": "ValidateDesign(log_file)", "attempts": attempts}
    except Exception as exc:  # pragma: no cover - depends on AEDT COM/gRPC.
        attempts.append({"call": "ValidateDesign(log_file)", "ok": False, "error": f"{type(exc).__name__}: {exc}", "log_file": str(log_file)})
        return {"ok": False, "method": None, "attempts": attempts}


def _parse_update_design_spec(spec: str) -> tuple[str, str | None]:
    text = str(spec).strip()
    if not text:
        raise ValueError("empty validate update design spec")
    if ":" not in text:
        return text, None
    design, setup = text.rsplit(":", 1)
    return design.strip(), setup.strip() or None


def _update_design_solver_data(app: Any, specs: list[str], *, parent_design: str, fallback_setup: str, lifecycle: OperationLifecycle) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not specs:
        return results
    available_designs = _design_names(app)
    for raw_spec in specs:
        design, requested_setup = _parse_update_design_spec(raw_spec)
        item: dict[str, Any] = {"design": design, "requested_setup": requested_setup, "status": "running"}
        with lifecycle.timed("pre_validate_update_design_solver_data", design=design):
            if available_designs and design not in available_designs:
                item["status"] = "missing_design"
                item["available_designs"] = available_designs
                results.append(item)
                continue
            raw_design = _raw_set_active_design(app, design)
            setup_names = _raw_setup_names(raw_design)
            item["setup_names"] = setup_names
            setup = requested_setup
            if setup is None and fallback_setup in setup_names:
                setup = fallback_setup
            if setup is None and setup_names:
                setup = setup_names[0]
            item["setup"] = setup
            item["analyze_return"] = _jsonable(_raw_analyze_design(raw_design, setup))
            item["status"] = "updated"
        results.append(item)
    with lifecycle.timed("restore_parent_design_after_pre_validate_update", design=parent_design):
        _set_active_design(app, parent_design)
    return results


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
        output=event_log_path_for_json(args.output) if getattr(args, "output", None) else None,
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
            should_validate = bool(args.validate_before_analyze and (not args.export_only or args.validate_only))
            if should_validate:
                if args.auto_validate_update_designs:
                    with lifecycle.timed("scan_component_design_dependencies"):
                        result["component_design_dependencies"] = _component_design_dependencies(app, parent_design=args.design)
                    for design in result["component_design_dependencies"].get("dependencies", []):
                        if design not in args.validate_update_design:
                            args.validate_update_design.append(design)
                result["stage"] = "pre_validate_update_designs"
                result["pre_validate_update_designs"] = _update_design_solver_data(
                    app,
                    list(args.validate_update_design),
                    parent_design=args.design,
                    fallback_setup=args.setup,
                    lifecycle=lifecycle,
                )
                result["stage"] = "validate_design"
                with lifecycle.timed("validate_design"):
                    result["validate_design"] = _validate_design(app, args.out_dir)
                if not result["validate_design"].get("ok"):
                    result["status"] = "validation_failed"
                    result["messages"] = _safe_messages(app, aedt_messages=False)
                    result["aedt_messages"] = _safe_messages(app, aedt_messages=True)
                    final_lifecycle_status = "failed"
                    return result
                if args.validate_only:
                    result["status"] = "validated"
                    result["stage"] = "completed"
                    with lifecycle.timed("read_messages"):
                        result["messages"] = _safe_messages(app, aedt_messages=False)
                        result["aedt_messages"] = _safe_messages(app, aedt_messages=True)
                    final_lifecycle_status = "ok"
                    return result
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
        current_result = result or {}
        result = {
            "project": str(args.project),
            "design": args.design,
            "setup": args.setup,
            "sweep": args.sweep,
            "candidate": args.candidate,
            "status": "failed",
            "stage": current_result.get("stage", "unknown"),
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    parser.add_argument("--postprocess-profile", choices=["connector", "filter", "sp8t"], default="connector")
    parser.add_argument("--scoring-profile-id", default=None)
    parser.add_argument("--scoring-profile-path", type=Path, default=None)
    parser.add_argument("--baseline-s2p", type=Path, default=None)
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true", help="Run dependency update and ValidateDesign, then exit before solve/export.")
    parser.add_argument("--validate-before-analyze", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--skip-validate", action="store_false", dest="validate_before_analyze")
    parser.add_argument("--auto-validate-update-designs", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--validate-update-design",
        action="append",
        default=[],
        help="Solve/update a dependent design before ValidateDesign. Use DESIGN or DESIGN:SETUP. Repeat for multiple dependencies.",
    )
    parser.add_argument("--ready-timeout-s", type=float, default=120.0)
    parser.add_argument("--ready-settle-s", type=float, default=3.0)
    parser.add_argument("--export-attempts", type=int, default=3)
    parser.add_argument("--export-retry-delay-s", type=float, default=3.0)
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


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
