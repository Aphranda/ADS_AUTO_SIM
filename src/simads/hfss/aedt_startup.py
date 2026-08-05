"""AEDT startup compatibility helpers."""

from __future__ import annotations

import os
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


__all__ = ["apply_grpc_startup_compat", "apply_pyaedt_settings", "startup_snapshot"]
