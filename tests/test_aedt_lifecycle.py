import importlib.util
import json
from argparse import Namespace
from pathlib import Path

import pytest

from simads.hfss.aedt_startup import OperationLifecycle, hidden_subprocess_kwargs


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
