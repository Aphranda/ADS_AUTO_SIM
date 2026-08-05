"""AEDT startup compatibility helpers."""

from __future__ import annotations

from contextlib import contextmanager
import json
import time
import os
from pathlib import Path
from typing import Any


def apply_grpc_startup_compat() -> None:
    """Use the legacy insecure gRPC startup path before PyAEDT imports AEDT."""

    os.environ.setdefault("PYAEDT_USE_PRE_GRPC_ARGS", "True")
    os.environ.setdefault("grpc_secure_mode", "False")
    os.environ.setdefault("SIMADS_AEDT_WAIT_FOR_LICENSE", "True")
    os.environ.setdefault("SIMADS_AEDT_DESKTOP_TIMEOUT_S", "300")


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
    "startup_snapshot",
]
