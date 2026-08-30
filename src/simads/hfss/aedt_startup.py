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

from simads.hfss.artifact_names import event_log_path_for_json, json_artifact_name


AEDT_PROCESS_NAMES = {"ansysedt.exe", "ansysedtsv.exe", "ansysedt", "ansysedtsv"}


class OperationLifecycle:
    """Small structured lifecycle log with per-operation timing."""

    def __init__(self, label: str, *, output: str | Path | None = None) -> None:
        self.label = label
        self.started_monotonic = time.monotonic()
        self.started_epoch = time.time()
        self.output = Path(output) if output else None
        self.events: list[dict[str, Any]] = []
        if self.output:
            self.output.parent.mkdir(parents=True, exist_ok=True)
        self.mark("lifecycle_start", status="running")

    def mark(self, operation: str, *, status: str = "ok", **extra: Any) -> dict[str, Any]:
        event = {
            "label": self.label,
            "operation": operation,
            "status": status,
            "timestamp_epoch": round(time.time(), 3),
            "elapsed_s": round(time.monotonic() - self.started_monotonic, 3),
        }
        event.update(extra)
        self.events.append(event)
        if self.output:
            with self.output.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        return event

    @contextmanager
    def timed(self, operation: str, **extra: Any):
        started = time.monotonic()
        self.mark(operation, status="running", **extra)
        try:
            yield
        except BaseException as exc:
            self.mark(
                operation,
                status="failed",
                duration_s=round(time.monotonic() - started, 3),
                error_type=type(exc).__name__,
                error=str(exc),
            )
            raise
        else:
            self.mark(operation, status="ok", duration_s=round(time.monotonic() - started, 3))

    def finish(self, *, status: str = "ok", **extra: Any) -> dict[str, Any]:
        self.mark("lifecycle_finish", status=status, total_elapsed_s=round(time.monotonic() - self.started_monotonic, 3), **extra)
        return self.summary(status=status)

    def summary(self, *, status: str | None = None) -> dict[str, Any]:
        payload = {
            "label": self.label,
            "status": status or (self.events[-1]["status"] if self.events else "unknown"),
            "started_epoch": round(self.started_epoch, 3),
            "elapsed_s": round(time.monotonic() - self.started_monotonic, 3),
            "event_count": len(self.events),
            "events": self.events,
        }
        if self.output:
            payload["event_log"] = str(self.output)
        return payload


def apply_grpc_startup_compat() -> None:
    """Use the legacy insecure gRPC startup path before PyAEDT imports AEDT."""

    if not _env_bool("SIMADS_KEEP_HPEESOF_DIR", False):
        os.environ.pop("HPEESOF_DIR", None)
    if _env_bool("SIMADS_AEDT_HIDDEN_GRAPHICAL", False):
        os.environ.setdefault("ANSYS_DISABLE_DISPLAY", "1")
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
        "HPEESOF_DIR": os.environ.get("HPEESOF_DIR"),
        "SIMADS_AEDT_WAIT_FOR_LICENSE": os.environ.get("SIMADS_AEDT_WAIT_FOR_LICENSE"),
        "SIMADS_AEDT_DESKTOP_TIMEOUT_S": os.environ.get("SIMADS_AEDT_DESKTOP_TIMEOUT_S"),
        "SIMADS_AEDT_HIDDEN_GRAPHICAL": os.environ.get("SIMADS_AEDT_HIDDEN_GRAPHICAL"),
        "ANSYS_DISABLE_DISPLAY": os.environ.get("ANSYS_DISABLE_DISPLAY"),
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


def _silent_python_executable() -> str:
    """Prefer pythonw.exe for hidden Windows helper processes."""

    executable = Path(sys.executable)
    if os.name == "nt" and executable.name.lower() == "python.exe":
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    return str(executable)


def hidden_subprocess_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        kwargs.update({"creationflags": creationflags, "startupinfo": startupinfo, "close_fds": True})
    else:
        kwargs["start_new_session"] = True
    return kwargs


def _process_create_time(pid: int) -> float | None:
    try:
        import psutil

        return float(psutil.Process(pid).create_time())
    except Exception:
        return None


def _project_lock_path(project: str | Path | None) -> Path | None:
    if project is None:
        return None
    path = Path(project)
    if not str(path).lower().endswith(".aedt"):
        return None
    return Path(str(path) + ".lock")


def _read_short_text(path: Path, *, limit: int = 4096) -> str:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as fp:
            return fp.read(limit)
    except Exception:
        return ""


def _active_aedt_processes() -> tuple[list[dict[str, Any]], str | None]:
    try:
        import psutil
    except Exception as exc:
        return [], f"psutil_unavailable: {type(exc).__name__}: {exc}"

    processes: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = str(proc.info.get("name") or proc.name() or "")
        except psutil.Error:
            continue
        if name.lower() not in AEDT_PROCESS_NAMES:
            continue
        try:
            create_time = float(proc.create_time())
        except psutil.Error:
            create_time = None
        processes.append(
            {
                "pid": int(proc.pid),
                "name": name,
                "create_time": create_time,
                "age_s": round(time.time() - create_time, 3) if create_time else None,
            }
        )
    return sorted(processes, key=lambda item: int(item["pid"])), None


def prepare_aedt_project_lock(
    project: str | Path | None,
    *,
    remove_stale: bool = True,
    force_remove: bool = False,
) -> dict[str, Any]:
    """Inspect and optionally remove a stale AEDT project lock file.

    The safe default only removes ``*.aedt.lock`` when no AEDT process is
    running. Active AEDT processes may be a user GUI or another automation
    session, so their locks must be left intact unless the caller explicitly
    requests ``force_remove``.
    """

    lock_path = _project_lock_path(project)
    payload: dict[str, Any] = {
        "project": str(project) if project is not None else None,
        "lock_path": str(lock_path) if lock_path is not None else None,
        "exists": False,
        "removed": False,
        "action": "not_applicable",
    }
    if lock_path is None:
        payload["reason"] = "project is not an .aedt path"
        return payload
    payload["exists"] = lock_path.exists()
    if not payload["exists"]:
        payload["action"] = "none"
        return payload

    payload["lock_preview"] = _read_short_text(lock_path)
    processes, process_error = _active_aedt_processes()
    payload["active_aedt_processes"] = processes
    if process_error:
        payload["process_probe_error"] = process_error
    if not remove_stale:
        payload["action"] = "kept"
        payload["reason"] = "remove_stale disabled"
        return payload
    if processes and not force_remove:
        payload["action"] = "kept"
        payload["reason"] = "active AEDT process exists"
        return payload
    if process_error and not force_remove:
        payload["action"] = "kept"
        payload["reason"] = "could not safely inspect AEDT processes"
        return payload

    try:
        lock_path.unlink()
    except FileNotFoundError:
        payload["action"] = "already_removed"
        payload["exists_after"] = False
        return payload
    except Exception as exc:
        payload["action"] = "remove_failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        payload["exists_after"] = lock_path.exists()
        return payload
    payload["action"] = "removed_stale_lock"
    payload["removed"] = True
    payload["exists_after"] = lock_path.exists()
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
    script_started: bool = False,
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
    stem = f"{label}_{parent}_{pid}"
    output = run_dir / json_artifact_name(stem, "run_log")
    event_log = event_log_path_for_json(output)
    owner_record = run_dir / json_artifact_name(stem, "owner")
    target_create_time = _process_create_time(pid)
    owner_payload = {
        "label": label,
        "owner_pid": parent,
        "aedt_process_id": pid,
        "target_create_time_epoch": target_create_time,
        "script_started": bool(script_started),
        "created_epoch": round(time.time(), 3),
    }
    owner_record.write_text(json.dumps(owner_payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    command = [
        _silent_python_executable(),
        str(reaper),
        "--watch",
        "--label",
        label,
        "--owner-record",
        str(owner_record),
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
        "--event-log",
        str(event_log),
    ]
    if target_create_time is not None:
        command.extend(["--target-create-time-epoch", f"{target_create_time:.6f}"])
    execute_requested = _env_bool("SIMADS_AEDT_REAPER_EXECUTE", True) if execute is None else bool(execute)
    terminate_disabled = _env_bool("SIMADS_AEDT_REAPER_DISABLE_TERMINATE", False)
    should_execute = execute_requested and script_started and not terminate_disabled
    if should_execute:
        command.append("--execute")
    execute_block_reason = None
    if execute_requested and not script_started:
        execute_block_reason = "target AEDT was not marked as started by this script"
    elif execute_requested and terminate_disabled:
        execute_block_reason = "SIMADS_AEDT_REAPER_DISABLE_TERMINATE is true"
    try:
        proc = subprocess.Popen(
            command,
            cwd=str(_repo_root()),
            **hidden_subprocess_kwargs(),
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
        "execute_requested": execute_requested,
        "terminate_disabled": terminate_disabled,
        "script_started": script_started,
        "execute_block_reason": execute_block_reason,
        "output": str(output),
        "event_log": str(event_log),
        "owner_record": str(owner_record),
        "silent": True,
        "helper_executable": command[0],
        "target_create_time_epoch": target_create_time,
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
    "hidden_subprocess_kwargs",
    "OperationLifecycle",
    "prepare_aedt_project_lock",
    "stable_export_touchstone",
    "start_aedt_reaper",
    "startup_snapshot",
    "wait_for_hfss3dlayout_ready",
]
