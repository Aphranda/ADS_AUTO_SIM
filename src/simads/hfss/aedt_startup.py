"""AEDT startup compatibility helpers."""

from __future__ import annotations

from contextlib import contextmanager
import json
import time
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


def apply_grpc_startup_compat() -> None:
    """Use the legacy insecure gRPC startup path before PyAEDT imports AEDT."""

    os.environ.setdefault("PYAEDT_USE_PRE_GRPC_ARGS", "True")
    os.environ.setdefault("grpc_secure_mode", "False")
    os.environ.setdefault("SIMADS_AEDT_WAIT_FOR_LICENSE", "True")
    os.environ.setdefault("SIMADS_AEDT_DESKTOP_TIMEOUT_S", "300")
    if _env_bool("SIMADS_AEDT_USE_WORKSPACE_USER_DIRS", True):
        user_root = Path(os.environ.get("SIMADS_AEDT_USER_ROOT", Path.cwd() / ".simads" / "aedt_user"))
        appdata = user_root / "AppData" / "Roaming"
        local_appdata = user_root / "AppData" / "Local"
        temp = user_root / "Temp"
        for path in (user_root, appdata, local_appdata, temp, user_root / "Documents" / "Ansoft"):
            path.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("SIMADS_AEDT_USER_ROOT", str(user_root))
        os.environ["HOME"] = str(user_root)
        os.environ["USERPROFILE"] = str(user_root)
        os.environ["APPDATA"] = str(appdata)
        os.environ["LOCALAPPDATA"] = str(local_appdata)
        os.environ["TEMP"] = str(temp)
        os.environ["TMP"] = str(temp)


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def apply_pyaedt_settings(settings: Any) -> None:
    """Mirror startup environment into PyAEDT runtime settings when available."""

    if hasattr(settings, "grpc_secure_mode"):
        settings.grpc_secure_mode = False
    if hasattr(settings, "wait_for_license"):
        settings.wait_for_license = _env_bool("SIMADS_AEDT_WAIT_FOR_LICENSE", True)
    if hasattr(settings, "desktop_launch_timeout"):
        requested = _env_int("SIMADS_AEDT_DESKTOP_TIMEOUT_S", 300)
        current = int(getattr(settings, "desktop_launch_timeout", 0) or 0)
        settings.desktop_launch_timeout = max(current, requested)
    if hasattr(settings, "enable_desktop_logs"):
        settings.enable_desktop_logs = _env_bool("SIMADS_AEDT_ENABLE_DESKTOP_LOGS", False)


def startup_snapshot(settings: Any | None = None) -> dict[str, Any]:
    """Return the AEDT startup knobs that matter for non-graphical launch."""

    payload: dict[str, Any] = {
        "PYAEDT_USE_PRE_GRPC_ARGS": os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS"),
        "grpc_secure_mode_env": os.environ.get("grpc_secure_mode"),
        "SIMADS_AEDT_WAIT_FOR_LICENSE": os.environ.get("SIMADS_AEDT_WAIT_FOR_LICENSE"),
        "SIMADS_AEDT_DESKTOP_TIMEOUT_S": os.environ.get("SIMADS_AEDT_DESKTOP_TIMEOUT_S"),
        "SIMADS_AEDT_USER_ROOT": os.environ.get("SIMADS_AEDT_USER_ROOT"),
        "HOME": os.environ.get("HOME"),
        "USERPROFILE": os.environ.get("USERPROFILE"),
        "APPDATA": os.environ.get("APPDATA"),
        "LOCALAPPDATA": os.environ.get("LOCALAPPDATA"),
        "TEMP": os.environ.get("TEMP"),
    }
    if settings is not None:
        for name in (
            "grpc_secure_mode",
            "grpc_local",
            "grpc_listen_all",
            "wait_for_license",
            "desktop_launch_timeout",
            "enable_desktop_logs",
            "use_grpc_api",
            "number_of_grpc_api_retries",
        ):
            if hasattr(settings, name):
                payload[f"settings.{name}"] = getattr(settings, name)
    return payload


def _clean_design_name(name: Any) -> str:
    text = str(name)
    if ";" in text and text.split(";", 1)[0].isdigit():
        return text.split(";", 1)[1]
    return text


def _call_no_raise(func: Any, *args: Any, **kwargs: Any) -> tuple[bool, Any]:
    try:
        return True, func(*args, **kwargs)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def disable_aedt_auto_open(app: Any) -> dict[str, Any]:
    """Disable AEDT auto-open behavior when the active app exposes the API."""

    if hasattr(app, "set_auto_open"):
        ok, result = _call_no_raise(app.set_auto_open, enable=False)
        return {"api": "app.set_auto_open", "ok": ok, "result": result}
    design_solutions = getattr(app, "design_solutions", None)
    if design_solutions is not None and hasattr(design_solutions, "set_auto_open"):
        ok, result = _call_no_raise(design_solutions.set_auto_open, enable=False)
        return {"api": "app.design_solutions.set_auto_open", "ok": ok, "result": result}
    return {"api": None, "ok": False, "result": "set_auto_open is unavailable for this AEDT app"}


def _wait_for_design_name(app: Any, timeout_s: float) -> str:
    started = time.monotonic()
    last_error = ""
    while time.monotonic() - started <= timeout_s:
        ok, result = _call_no_raise(app.odesign.GetName)
        if ok:
            return _clean_design_name(result)
        last_error = str(result)
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for AEDT design load: {last_error}")


def wait_for_hfss3dlayout_ready(
    app: Any,
    *,
    setup: str | None = None,
    sweep: str | None = None,
    timeout_s: float = 90,
    settle_s: float = 2,
) -> dict[str, Any]:
    """Synchronize a cold HFSS 3D Layout gRPC session before API calls."""

    payload: dict[str, Any] = {
        "auto_open": disable_aedt_auto_open(app),
        "timeout_s": timeout_s,
        "settle_s": settle_s,
    }
    payload["design_name"] = _wait_for_design_name(app, timeout_s)
    ok_project, project_name = _call_no_raise(lambda: app.oproject.GetName())
    payload["project_name"] = project_name if ok_project else None
    payload["project_name_error"] = None if ok_project else project_name

    ok_modeler, modeler = _call_no_raise(lambda: app.modeler)
    payload["modeler_loaded"] = bool(ok_modeler and modeler is not None)
    if not ok_modeler:
        payload["modeler_error"] = modeler

    ok_setups, setup_names = _call_no_raise(lambda: list(getattr(app, "setup_names", []) or []))
    payload["setup_names"] = setup_names if ok_setups else []
    if not ok_setups:
        payload["setup_names_error"] = setup_names
    if setup:
        setup_obj = None
        if hasattr(app, "get_setup"):
            ok_setup, setup_obj = _call_no_raise(app.get_setup, setup)
            payload["setup_loaded"] = bool(ok_setup and setup_obj)
            if not ok_setup:
                payload["setup_error"] = setup_obj
        else:
            payload["setup_loaded"] = setup in payload["setup_names"]
        if sweep:
            sweeps: list[str] = []
            if hasattr(app, "get_sweeps"):
                ok_sweeps, result = _call_no_raise(app.get_sweeps, setup)
                if ok_sweeps and result:
                    sweeps = [str(item) for item in result]
                elif not ok_sweeps:
                    payload["sweeps_error"] = result
            if not sweeps and setup_obj is not None and hasattr(setup_obj, "get_sweep_names"):
                ok_sweeps, result = _call_no_raise(setup_obj.get_sweep_names)
                if ok_sweeps and result:
                    sweeps = [str(item) for item in result]
            if not sweeps and setup_obj is not None and hasattr(setup_obj, "get_sweep"):
                ok_sweep, result = _call_no_raise(setup_obj.get_sweep, sweep)
                payload["sweep_loaded"] = bool(ok_sweep and result)
                if not ok_sweep:
                    payload["sweep_error"] = result
            else:
                payload["sweep_names"] = sweeps
                payload["sweep_loaded"] = sweep in sweeps
    if settle_s > 0:
        time.sleep(settle_s)
    return payload


def stable_export_touchstone(
    app: Any,
    *,
    setup: str,
    sweep: str,
    output_file: str | Path,
    attempts: int = 3,
    delay_s: float = 3,
    **kwargs: Any,
) -> tuple[str | bool, list[dict[str, Any]]]:
    """Export Touchstone with retries for HFSS 3D Layout gRPC flakiness."""

    output_path = Path(output_file)
    attempt_log: list[dict[str, Any]] = []
    last_error: BaseException | None = None
    for attempt in range(1, max(1, attempts) + 1):
        try:
            exported = app.export_touchstone(setup=setup, sweep=sweep, output_file=str(output_path), **kwargs)
            exists = output_path.exists() or (bool(exported) and Path(str(exported)).exists())
            attempt_log.append({"attempt": attempt, "ok": bool(exported) or exists, "exported": str(exported), "exists": exists})
            if exported or exists:
                return exported or str(output_path), attempt_log
        except BaseException as exc:
            last_error = exc
            attempt_log.append({"attempt": attempt, "ok": False, "error_type": type(exc).__name__, "error": str(exc)})
            if attempt < attempts and delay_s > 0:
                time.sleep(delay_s)
    if last_error is not None:
        raise last_error
    return False, attempt_log


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _aedt_process_id(app: Any) -> int | None:
    for call in (
        lambda: app.odesktop.GetProcessID(),
        lambda: app.desktop_class.odesktop.GetProcessID(),
        lambda: app.desktop_class.aedt_process_id,
    ):
        try:
            value = call()
            if value:
                return int(value)
        except Exception:
            continue
    return None


def start_aedt_reaper(
    app: Any,
    *,
    label: str,
    parent_pid: int | None = None,
    execute: bool | None = None,
    timeout_s: float | None = None,
) -> dict[str, Any]:
    """Start a detached monitor that reaps this automation AEDT after exit."""

    pid = _aedt_process_id(app)
    if pid is None:
        return {"started": False, "reason": "aedt_process_id_unavailable"}
    reaper = _repo_root() / "tools" / "hfss" / "reap_aedt_processes.py"
    if not reaper.exists():
        return {"started": False, "reason": f"reaper_not_found: {reaper}", "aedt_process_id": pid}
    run_dir = _repo_root() / ".simads" / "aedt_reaper"
    run_dir.mkdir(parents=True, exist_ok=True)
    parent = parent_pid if parent_pid is not None else os.getpid()
    output = run_dir / f"{label}_{parent}_{pid}.json"
    command = [
        sys.executable,
        str(reaper),
        "--watch",
        "--pid",
        str(pid),
        "--parent-pid",
        str(parent),
        "--grace-after-parent-exit-s",
        os.environ.get("SIMADS_AEDT_REAPER_GRACE_S", "5"),
        "--interval-s",
        os.environ.get("SIMADS_AEDT_REAPER_INTERVAL_S", "10"),
        "--timeout-s",
        str(timeout_s if timeout_s is not None else _env_int("SIMADS_AEDT_REAPER_TIMEOUT_S", 14400)),
        "--output",
        str(output),
    ]
    should_execute = _env_bool("SIMADS_AEDT_REAPER_EXECUTE", True) if execute is None else execute
    if should_execute:
        command.append("--execute")
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
    try:
        proc = subprocess.Popen(
            command,
            cwd=str(_repo_root()),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    except Exception as exc:
        return {"started": False, "reason": f"{type(exc).__name__}: {exc}", "aedt_process_id": pid}
    return {
        "started": True,
        "label": label,
        "aedt_process_id": pid,
        "parent_pid": parent,
        "reaper_pid": proc.pid,
        "execute": should_execute,
        "output": str(output),
    }


@contextmanager
def aedt_automation_lock(label: str, timeout_s: int | None = None):
    """Serialize AEDT automation processes started from this repository."""

    timeout = timeout_s if timeout_s is not None else _env_int("SIMADS_AEDT_LOCK_TIMEOUT_S", 1800)
    lock_path = Path(os.environ.get("SIMADS_AEDT_LOCK_FILE", Path.cwd() / ".simads" / "aedt_automation.lock"))
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fp = lock_path.open("a+", encoding="utf-8")
    acquired = False
    started = time.monotonic()
    try:
        if os.name == "nt":
            import msvcrt

            fp.seek(0)
            if not fp.read(1):
                fp.write("\0")
                fp.flush()
            while True:
                try:
                    fp.seek(0)
                    msvcrt.locking(fp.fileno(), msvcrt.LK_NBLCK, 1)
                    acquired = True
                    break
                except OSError:
                    if time.monotonic() - started >= timeout:
                        raise TimeoutError(f"Timed out waiting for AEDT automation lock: {lock_path}")
                    time.sleep(2)
        metadata = {
            "label": label,
            "pid": os.getpid(),
            "started_epoch": round(time.time(), 3),
            "lock_path": str(lock_path),
        }
        fp.seek(0)
        fp.truncate()
        fp.write(json.dumps(metadata, ensure_ascii=True))
        fp.flush()
        yield metadata
    finally:
        try:
            fp.seek(0)
            fp.truncate()
            fp.flush()
            if acquired and os.name == "nt":
                import msvcrt

                fp.seek(0)
                msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            fp.close()


__all__ = [
    "aedt_automation_lock",
    "apply_grpc_startup_compat",
    "apply_pyaedt_settings",
    "disable_aedt_auto_open",
    "stable_export_touchstone",
    "start_aedt_reaper",
    "startup_snapshot",
    "wait_for_hfss3dlayout_ready",
]
