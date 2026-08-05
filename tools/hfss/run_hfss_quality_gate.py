#!/usr/bin/env python3
"""Run the HFSS code quality gate, including a real AEDT API smoke test."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.config import get_hfss_profile, hfss_profile_names, validate_hfss_profile


DEFAULT_COMPILE_TARGETS = [
    "src/simads/hfss/__init__.py",
    "src/simads/hfss/aedt_startup.py",
    "src/simads/hfss/session.py",
    "src/simads/hfss/build.py",
    "src/simads/hfss/layout.py",
    "src/simads/hfss/ports.py",
    "src/simads/hfss/port_plans.py",
    "src/simads/hfss/connector_contract.py",
    "src/simads/hfss/manifest.py",
    "src/simads/hfss/results.py",
    "src/simads/hfss/solve.py",
    "src/simads/hfss/workflow.py",
    "src/simads/reports/__init__.py",
    "src/simads/reports/manifest_report.py",
    "tools/reports/build_report_manifest.py",
    "tools/hfss/check_hfss_script_classes.py",
    "tools/hfss/create_hfss3dlayout_smoke_project.py",
    "tools/hfss/recreate_connector_component_pin_port.py",
    "tools/hfss/rebuild_connector_pin_iports.py",
    "tools/hfss/replace_hfss3dlayout_layout_primitives.py",
    "tools/hfss/run_existing_hfss3dlayout_verdict.py",
]

DEFAULT_PYTEST_TARGETS = [
    "tests/test_aedt_lifecycle.py",
    "tests/test_hfss_build.py",
    "tests/test_hfss_connector.py",
    "tests/test_hfss_layout.py",
    "tests/test_hfss_port_plans.py",
    "tests/test_hfss_rebuild_connector_pin_iports.py",
    "tests/test_hfss_replace_layout.py",
    "tests/test_hfss_results.py",
    "tests/test_hfss_script_classes.py",
    "tests/test_hfss_manifest_contracts.py",
    "tests/test_hfss_solve.py",
    "tests/test_report_manifest.py",
    "tests/test_run_existing_hfss3dlayout_verdict.py",
]


@dataclass(frozen=True)
class GateCommand:
    name: str
    command: list[str]
    timeout_s: int


@dataclass
class GateCommandResult:
    name: str
    command: list[str]
    returncode: int
    elapsed_s: float
    stdout_tail: str
    stderr_tail: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _tail(text: str, limit: int = 12000) -> str:
    return text[-limit:] if len(text) > limit else text


def _run_subprocess(command: Sequence[str], *, cwd: Path, timeout_s: int) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
    )


def run_gate_command(
    step: GateCommand,
    *,
    runner: Callable[[Sequence[str], Path, int], subprocess.CompletedProcess[str]],
) -> GateCommandResult:
    started = time.monotonic()
    try:
        completed = runner(step.command, REPO_ROOT, step.timeout_s)
        return GateCommandResult(
            name=step.name,
            command=step.command,
            returncode=int(completed.returncode),
            elapsed_s=round(time.monotonic() - started, 3),
            stdout_tail=_tail(completed.stdout or ""),
            stderr_tail=_tail(completed.stderr or ""),
        )
    except subprocess.TimeoutExpired as exc:
        return GateCommandResult(
            name=step.name,
            command=step.command,
            returncode=124,
            elapsed_s=round(time.monotonic() - started, 3),
            stdout_tail=_tail((exc.stdout or "") if isinstance(exc.stdout, str) else str(exc.stdout or "")),
            stderr_tail=_tail((exc.stderr or "") if isinstance(exc.stderr, str) else str(exc.stderr or "")),
        )


def build_gate_commands(args: argparse.Namespace, *, host_python: Path) -> list[GateCommand]:
    commands: list[GateCommand] = []
    if not args.skip_compile:
        compile_targets = [str(Path(item)) for item in (args.compile_target or DEFAULT_COMPILE_TARGETS)]
        commands.append(
            GateCommand(
                name="py_compile",
                command=[str(host_python), "-m", "py_compile", *compile_targets],
                timeout_s=args.compile_timeout_s,
            )
        )
    if not args.skip_pytest:
        pytest_targets = [str(Path(item)) for item in (args.pytest_target or DEFAULT_PYTEST_TARGETS)]
        pytest_basetemp = REPO_ROOT / ".simads" / "pytest_tmp" / "hfss_quality_gate"
        pytest_cache = REPO_ROOT / ".simads" / "pytest_cache"
        pytest_basetemp.parent.mkdir(parents=True, exist_ok=True)
        pytest_cache.mkdir(parents=True, exist_ok=True)
        commands.append(
            GateCommand(
                name="pytest",
                command=[
                    str(host_python),
                    "-m",
                    "pytest",
                    "--basetemp",
                    str(pytest_basetemp),
                    "-o",
                    f"cache_dir={pytest_cache}",
                    *pytest_targets,
                ],
                timeout_s=args.pytest_timeout_s,
            )
        )
    if not args.skip_smoke:
        smoke_output = args.smoke_output or (REPO_ROOT / ".simads" / "aedt_smoke" / "latest_gate_smoke.json")
        smoke_command = [
            str(host_python),
            "tools/hfss/create_hfss3dlayout_smoke_project.py",
            "--version",
            args.version,
            "--output",
            str(smoke_output),
        ]
        if not args.non_graphical:
            smoke_command.append("--graphical")
        if args.keep_open:
            smoke_command.append("--keep-open")
        commands.append(
            GateCommand(
                name="aedt_smoke",
                command=smoke_command,
                timeout_s=args.smoke_timeout_s,
            )
        )
    return commands


def run_gate(
    args: argparse.Namespace,
    *,
    runner: Callable[[Sequence[str], Path, int], subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, object]:
    started = time.monotonic()
    runner = runner or (lambda command, cwd, timeout_s: _run_subprocess(command, cwd=cwd, timeout_s=timeout_s))
    profile = get_hfss_profile(args.profile)
    host_python = Path(args.host_python) if args.host_python is not None else profile.host_python
    checks = validate_hfss_profile(profile)
    profile_payload = profile.to_dict()
    profile_payload["selected_host_python"] = str(host_python)
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "status": "running",
        "profile": profile_payload,
        "profile_checks": [
            {"name": check.name, "path": str(check.path), "ok": check.ok, "message": check.message}
            for check in checks
        ],
        "steps": [],
    }
    try:
        failed_checks = [check for check in checks if not check.ok]
        if args.strict_profile and failed_checks:
            payload["status"] = "failed"
            payload["stage"] = "profile_check"
            payload["failed_profile_checks"] = [check.name for check in failed_checks]
            return payload

        step_results: list[dict[str, object]] = []
        for step in build_gate_commands(args, host_python=host_python):
            result = run_gate_command(step, runner=runner)
            step_results.append(asdict(result) | {"ok": result.ok})
            payload["steps"] = step_results
            if not result.ok:
                payload["status"] = "failed"
                payload["stage"] = result.name
                return payload
        payload["status"] = "ok"
        payload["stage"] = "completed"
        return payload
    except BaseException as exc:
        payload.update(
            {
                "status": "failed",
                "stage": payload.get("stage", "unknown"),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
        return payload
    finally:
        payload["elapsed_s"] = round(time.monotonic() - started, 3)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HFSS py_compile, pytest, and AEDT API smoke checks.")
    parser.add_argument("--profile", default="auto", choices=hfss_profile_names(include_auto=True))
    parser.add_argument("--host-python", type=Path, default=None, help="Override the HFSS profile host Python.")
    parser.add_argument("--version", default=None, help="AEDT version for the smoke test. Defaults to profile version.")
    parser.add_argument("--strict-profile", action="store_true", default=True)
    parser.add_argument("--no-strict-profile", action="store_false", dest="strict_profile")
    parser.add_argument("--skip-compile", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--compile-target", action="append", default=[])
    parser.add_argument("--pytest-target", action="append", default=[])
    parser.add_argument("--compile-timeout-s", type=int, default=120)
    parser.add_argument("--pytest-timeout-s", type=int, default=300)
    parser.add_argument("--smoke-timeout-s", type=int, default=600)
    parser.add_argument("--smoke-output", type=Path, default=None)
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / ".simads" / "gates" / "hfss_quality_gate_latest.json")
    args = parser.parse_args()
    profile = get_hfss_profile(args.profile)
    args.version = args.version or profile.version
    return args


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    payload = run_gate(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
