"""Reusable HFSS 3D Layout session lifecycle helpers."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from simads.hfss.aedt_startup import (
    OperationLifecycle,
    aedt_automation_lock,
    apply_grpc_startup_compat,
    apply_pyaedt_settings,
    prepare_aedt_project_lock,
    start_aedt_reaper,
    startup_snapshot,
    wait_for_hfss3dlayout_ready,
)


@dataclass(frozen=True)
class Hfss3dLayoutSessionConfig:
    label: str
    project: str | Path | None
    design: str | None = None
    version: str | None = None
    non_graphical: bool = True
    new_desktop: bool = True
    remove_lock: bool = False
    close_on_exit: bool = False
    keep_open: bool = False
    close_projects: bool = True
    close_desktop: bool = True
    wait_ready: bool = True
    ready_setup: str | None = None
    ready_sweep: str | None = None
    ready_timeout_s: float = 120.0
    ready_settle_s: float = 3.0
    reaper_execute: bool | None = None
    reaper_script_started: bool | None = None
    remove_stale_project_lock: bool = True
    force_remove_project_lock: bool = False


@dataclass
class Hfss3dLayoutSession:
    app: Any
    startup: dict[str, Any]
    aedt_lock: dict[str, Any] | None
    project_lock: dict[str, Any] | None
    aedt_reaper: dict[str, Any] | None
    aedt_ready: dict[str, Any] | None

    def metadata(self) -> dict[str, Any]:
        return {
            "aedt_startup": self.startup,
            "aedt_lock": self.aedt_lock,
            "project_lock": self.project_lock,
            "aedt_reaper": self.aedt_reaper,
            "aedt_ready": self.aedt_ready,
        }


def _default_app_factory() -> tuple[Callable[..., Any], Any]:
    apply_grpc_startup_compat()
    from ansys.aedt.core import Hfss3dLayout, settings

    return Hfss3dLayout, settings


@contextmanager
def open_hfss3dlayout_session(
    config: Hfss3dLayoutSessionConfig,
    lifecycle: OperationLifecycle,
    *,
    app_factory: Callable[..., Any] | None = None,
    settings_obj: Any | None = None,
) -> Iterator[Hfss3dLayoutSession]:
    """Open a managed HFSS 3D Layout session through PyAEDT APIs."""

    if app_factory is None or settings_obj is None:
        default_factory, default_settings = _default_app_factory()
        app_factory = app_factory or default_factory
        settings_obj = settings_obj or default_settings

    with lifecycle.timed("apply_pyaedt_settings"):
        apply_pyaedt_settings(settings_obj)
    startup = startup_snapshot(settings_obj)

    app: Any | None = None
    lock_cm = None
    lock_acquired = False
    aedt_lock: dict[str, Any] | None = None
    project_lock: dict[str, Any] | None = None
    aedt_reaper: dict[str, Any] | None = None
    aedt_ready: dict[str, Any] | None = None
    try:
        with lifecycle.timed("acquire_aedt_automation_lock"):
            lock_cm = aedt_automation_lock(config.label)
            aedt_lock = lock_cm.__enter__()
            lock_acquired = True
        with lifecycle.timed("prepare_aedt_project_lock"):
            project_lock = prepare_aedt_project_lock(
                config.project,
                remove_stale=config.remove_stale_project_lock,
                force_remove=config.force_remove_project_lock,
            )
        with lifecycle.timed("start_hfss3dlayout"):
            app = app_factory(
                project=str(config.project) if config.project is not None else None,
                design=config.design,
                version=config.version,
                non_graphical=config.non_graphical,
                new_desktop=config.new_desktop,
                close_on_exit=config.close_on_exit,
                remove_lock=config.remove_lock or bool((project_lock or {}).get("removed")),
            )
        script_started = (
            bool(config.new_desktop and config.non_graphical)
            if config.reaper_script_started is None
            else bool(config.reaper_script_started)
        )
        aedt_reaper = start_aedt_reaper(
            app,
            label=config.label,
            execute=(not config.keep_open) if config.reaper_execute is None else config.reaper_execute,
            script_started=script_started,
        )
        if config.wait_ready:
            with lifecycle.timed("wait_for_hfss3dlayout_ready"):
                aedt_ready = wait_for_hfss3dlayout_ready(
                    app,
                    setup=config.ready_setup,
                    sweep=config.ready_sweep,
                    timeout_s=config.ready_timeout_s,
                    settle_s=config.ready_settle_s,
                )
        yield Hfss3dLayoutSession(
            app=app,
            startup=startup,
            aedt_lock=aedt_lock,
            project_lock=project_lock,
            aedt_reaper=aedt_reaper,
            aedt_ready=aedt_ready,
        )
    finally:
        try:
            if app is not None and not config.keep_open:
                with lifecycle.timed("release_desktop"):
                    app.release_desktop(close_projects=config.close_projects, close_desktop=config.close_desktop)
        finally:
            if lock_cm is not None and lock_acquired:
                with lifecycle.timed("release_aedt_automation_lock"):
                    lock_cm.__exit__(None, None, None)


__all__ = ["Hfss3dLayoutSession", "Hfss3dLayoutSessionConfig", "open_hfss3dlayout_session"]
