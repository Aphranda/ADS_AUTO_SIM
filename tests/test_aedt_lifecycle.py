import importlib.util
import json
from argparse import Namespace
from pathlib import Path

import pytest

from simads.hfss import aedt_startup
from simads.hfss.aedt_startup import OperationLifecycle, hidden_subprocess_kwargs, prepare_aedt_project_lock
from simads.hfss import session as hfss_session
from simads.hfss.session import Hfss3dLayoutSessionConfig, open_hfss3dlayout_session


def _load_reaper_module():
    module_path = Path("tools/hfss/reap_aedt_processes.py")
    spec = importlib.util.spec_from_file_location("reap_aedt_processes", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_operation_lifecycle_writes_jsonl_events(tmp_path: Path) -> None:
    event_log = tmp_path / "events.jsonl"
    lifecycle = OperationLifecycle("unit_lifecycle", output=event_log)

    with lifecycle.timed("quick_step"):
        pass
    summary = lifecycle.finish(status="ok")

    assert summary["label"] == "unit_lifecycle"
    assert summary["status"] == "ok"
    assert summary["event_count"] == 4
    events = [json.loads(line) for line in event_log.read_text(encoding="utf-8").splitlines()]
    assert [event["operation"] for event in events] == [
        "lifecycle_start",
        "quick_step",
        "quick_step",
        "lifecycle_finish",
    ]
    assert events[2]["duration_s"] >= 0


def test_hidden_subprocess_kwargs_are_no_window_on_windows() -> None:
    kwargs = hidden_subprocess_kwargs()

    assert kwargs["stdin"] is not None
    assert kwargs["stdout"] is not None
    assert kwargs["stderr"] is not None
    if "creationflags" in kwargs:
        assert kwargs["creationflags"] != 0
        assert kwargs["startupinfo"] is not None


def test_prepare_aedt_project_lock_removes_stale_lock_without_aedt_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "unit.aedt"
    lock = tmp_path / "unit.aedt.lock"
    project.write_text("", encoding="utf-8")
    lock.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(aedt_startup, "_active_aedt_processes", lambda: ([], None))

    payload = prepare_aedt_project_lock(project)

    assert payload["action"] == "removed_stale_lock"
    assert payload["removed"] is True
    assert not lock.exists()


def test_prepare_aedt_project_lock_keeps_lock_when_aedt_process_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "unit.aedt"
    lock = tmp_path / "unit.aedt.lock"
    project.write_text("", encoding="utf-8")
    lock.write_text("active", encoding="utf-8")
    monkeypatch.setattr(aedt_startup, "_active_aedt_processes", lambda: ([{"pid": 123, "name": "ansysedt.exe"}], None))

    payload = prepare_aedt_project_lock(project)

    assert payload["action"] == "kept"
    assert payload["reason"] == "active AEDT process exists"
    assert payload["removed"] is False
    assert lock.exists()


def test_open_hfss3dlayout_session_manages_lock_ready_reaper_and_release(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, object]] = []

    class FakeLock:
        def __enter__(self):
            calls.append(("lock_enter", None))
            return {"label": "unit_session", "lock_path": "unit.lock"}

        def __exit__(self, exc_type, exc, tb):
            calls.append(("lock_exit", exc_type))

    class FakeApp:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            calls.append(("app_init", kwargs))

        def release_desktop(self, **kwargs):
            calls.append(("release_desktop", kwargs))

    fake_settings = object()
    monkeypatch.setattr(hfss_session, "apply_pyaedt_settings", lambda settings: calls.append(("settings", settings)))
    monkeypatch.setattr(hfss_session, "startup_snapshot", lambda settings: {"settings": "snapshot"})
    monkeypatch.setattr(hfss_session, "aedt_automation_lock", lambda label: FakeLock())
    monkeypatch.setattr(
        hfss_session,
        "prepare_aedt_project_lock",
        lambda project, remove_stale=True, force_remove=False: {
            "project": str(project),
            "removed": True,
            "remove_stale": remove_stale,
            "force_remove": force_remove,
        },
    )
    monkeypatch.setattr(hfss_session, "start_aedt_reaper", lambda app, **kwargs: {"reaper": kwargs})
    monkeypatch.setattr(hfss_session, "wait_for_hfss3dlayout_ready", lambda app, **kwargs: {"ready": kwargs})

    lifecycle = OperationLifecycle("unit_session", output=tmp_path / "events.jsonl")
    config = Hfss3dLayoutSessionConfig(
        label="unit_session",
        project=tmp_path / "unit.aedt",
        design="D1",
        version="2026.1",
        ready_setup="Setup1",
        ready_sweep="Sweep1",
        remove_lock=False,
    )

    with open_hfss3dlayout_session(config, lifecycle, app_factory=FakeApp, settings_obj=fake_settings) as session:
        assert session.startup == {"settings": "snapshot"}
        assert session.project_lock and session.project_lock["removed"] is True
        assert session.aedt_ready and session.aedt_ready["ready"]["setup"] == "Setup1"

    init_kwargs = dict(next(payload for name, payload in calls if name == "app_init"))
    assert init_kwargs["non_graphical"] is True
    assert init_kwargs["new_desktop"] is True
    assert init_kwargs["remove_lock"] is True
    assert ("release_desktop", {"close_projects": True, "close_desktop": True}) in calls
    assert calls[-1][0] == "lock_exit"


def test_open_hfss3dlayout_session_releases_lock_when_desktop_release_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeLock:
        def __enter__(self):
            calls.append("lock_enter")
            return {"label": "unit_session"}

        def __exit__(self, exc_type, exc, tb):
            calls.append("lock_exit")

    class FakeApp:
        def __init__(self, **kwargs):
            calls.append("app_init")

        def release_desktop(self, **kwargs):
            calls.append("release_desktop")
            raise RuntimeError("release failed")

    monkeypatch.setattr(hfss_session, "apply_pyaedt_settings", lambda settings: None)
    monkeypatch.setattr(hfss_session, "startup_snapshot", lambda settings: {})
    monkeypatch.setattr(hfss_session, "aedt_automation_lock", lambda label: FakeLock())
    monkeypatch.setattr(hfss_session, "prepare_aedt_project_lock", lambda *args, **kwargs: {"removed": False})
    monkeypatch.setattr(hfss_session, "start_aedt_reaper", lambda app, **kwargs: {})
    monkeypatch.setattr(hfss_session, "wait_for_hfss3dlayout_ready", lambda app, **kwargs: {})

    lifecycle = OperationLifecycle("unit_session", output=tmp_path / "events.jsonl")
    config = Hfss3dLayoutSessionConfig(label="unit_session", project=tmp_path / "unit.aedt")

    with pytest.raises(RuntimeError, match="release failed"):
        with open_hfss3dlayout_session(config, lifecycle, app_factory=FakeApp, settings_obj=object()):
            pass

    assert calls == ["lock_enter", "app_init", "release_desktop", "lock_exit"]


def test_open_hfss3dlayout_session_skips_release_after_manual_release_mark(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeLock:
        def __enter__(self):
            calls.append("lock_enter")
            return {"label": "unit_session"}

        def __exit__(self, exc_type, exc, tb):
            calls.append("lock_exit")

    class FakeApp:
        def __init__(self, **kwargs):
            calls.append("app_init")

        def release_desktop(self, **kwargs):
            calls.append("release_desktop")

    monkeypatch.setattr(hfss_session, "apply_pyaedt_settings", lambda settings: None)
    monkeypatch.setattr(hfss_session, "startup_snapshot", lambda settings: {})
    monkeypatch.setattr(hfss_session, "aedt_automation_lock", lambda label: FakeLock())
    monkeypatch.setattr(hfss_session, "prepare_aedt_project_lock", lambda *args, **kwargs: {"removed": False})
    monkeypatch.setattr(hfss_session, "start_aedt_reaper", lambda app, **kwargs: {})
    monkeypatch.setattr(hfss_session, "wait_for_hfss3dlayout_ready", lambda app, **kwargs: {})

    lifecycle = OperationLifecycle("unit_session", output=tmp_path / "events.jsonl")
    config = Hfss3dLayoutSessionConfig(label="unit_session", project=tmp_path / "unit.aedt")

    with open_hfss3dlayout_session(config, lifecycle, app_factory=FakeApp, settings_obj=object()) as session:
        session.app.release_desktop(close_projects=True, close_desktop=True)
        session.mark_desktop_released()

    assert calls == ["lock_enter", "app_init", "release_desktop", "lock_exit"]


def test_reaper_dry_run_records_timing_and_create_time_guard(tmp_path: Path) -> None:
    pytest.importorskip("psutil")
    reaper = _load_reaper_module()
    args = Namespace(
        label="unit_reaper",
        owner_record=None,
        pid=[999999],
        pid_file=[],
        parent_pid=None,
        watch=False,
        execute=False,
        no_window_only=True,
        allow_windowed=False,
        allow_when_any_windowed_aedt=False,
        allow_unsafe_no_create_time=False,
        min_age_s=0.0,
        started_after_epoch=None,
        target_create_time_epoch=1.0,
        create_time_tolerance_s=2.0,
        interval_s=0.01,
        timeout_s=0.0,
        grace_after_parent_exit_s=0.0,
        kill_after_s=0.01,
        keep_iterations=1,
        output=None,
        event_log=tmp_path / "reaper.jsonl",
    )

    payload = reaper.run_once(args)

    assert payload["mode"] == "dry_run"
    assert payload["target_pids"] == [999999]
    assert payload["eligible_pids"] == []
    assert payload["duration_s"] >= 0
    events = [json.loads(line) for line in args.event_log.read_text(encoding="utf-8").splitlines()]
    assert "scan_processes" in {event["operation"] for event in events}
    assert "run_once" in {event["operation"] for event in events}


def test_reaper_execute_requires_create_time_for_explicit_pid(tmp_path: Path) -> None:
    pytest.importorskip("psutil")
    reaper = _load_reaper_module()
    args = Namespace(
        label="unit_reaper_blocked",
        owner_record=None,
        pid=[999999],
        pid_file=[],
        parent_pid=None,
        watch=False,
        execute=True,
        no_window_only=True,
        allow_windowed=False,
        allow_when_any_windowed_aedt=False,
        allow_unsafe_no_create_time=False,
        min_age_s=0.0,
        started_after_epoch=None,
        target_create_time_epoch=None,
        create_time_tolerance_s=2.0,
        interval_s=0.01,
        timeout_s=0.0,
        grace_after_parent_exit_s=0.0,
        kill_after_s=0.01,
        keep_iterations=1,
        output=None,
        event_log=tmp_path / "reaper_blocked.jsonl",
    )

    payload = reaper.run_once(args)

    assert payload["mode"] == "execute"
    assert payload["execute_blocked_reason"] == "missing_or_unowned_owner_record"
    assert payload["reap_results"] == []


def test_reaper_execute_uses_only_owned_recorded_pid(tmp_path: Path) -> None:
    pytest.importorskip("psutil")
    reaper = _load_reaper_module()
    owner_record = tmp_path / "owned.owner.json"
    owner_record.write_text(
        json.dumps(
            {
                "label": "unit_owned",
                "owner_pid": 123,
                "aedt_process_id": 999999,
                "target_create_time_epoch": 1.0,
                "script_started": True,
            }
        ),
        encoding="utf-8",
    )
    args = Namespace(
        label="unit_reaper_owned",
        owner_record=owner_record,
        pid=[],
        pid_file=[],
        parent_pid=None,
        watch=False,
        execute=True,
        no_window_only=True,
        allow_windowed=False,
        allow_when_any_windowed_aedt=False,
        allow_unsafe_no_create_time=False,
        min_age_s=0.0,
        started_after_epoch=None,
        target_create_time_epoch=None,
        create_time_tolerance_s=2.0,
        interval_s=0.01,
        timeout_s=0.0,
        grace_after_parent_exit_s=0.0,
        kill_after_s=0.01,
        keep_iterations=1,
        output=None,
        event_log=tmp_path / "reaper_owned.jsonl",
    )

    payload = reaper.run_once(args)

    assert payload["target_pids"] == [999999]
    assert payload["target_create_time_epoch"] == 1.0
    assert "execute_blocked_reason" not in payload
    assert payload["reap_results"] == []
