#!/usr/bin/env python3
"""Monitor and reap AEDT processes left by non-graphical automation."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import signal
import sys
import time
from typing import Any

import psutil


AEDT_PROCESS_NAMES = {"ansysedt.exe", "ansysedtsv.exe"}


def _json_default(value: Any) -> str:
    return str(value)


def _visible_windows_by_pid() -> dict[int, list[str]]:
    if os.name != "nt":
        return {}
    user32 = ctypes.windll.user32
    windows: dict[int, list[str]] = {}

    enum_proc_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        windows.setdefault(int(pid.value), []).append(buffer.value)
        return True

    user32.EnumWindows(enum_proc_type(callback), 0)
    return windows


def _load_pid_file(path: Path) -> list[int]:
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [int(token) for token in text.replace(",", "\n").splitlines() if token.strip()]
    if isinstance(data, int):
        return [data]
    if isinstance(data, list):
        return [int(item) for item in data]
    if isinstance(data, dict):
        values = data.get("pids") or data.get("pid") or data.get("aedt_process_id")
        if isinstance(values, list):
            return [int(item) for item in values]
        if values is not None:
            return [int(values)]
    return []


def _target_pids(args: argparse.Namespace) -> set[int]:
    output = {int(pid) for pid in args.pid}
    for pid_file in args.pid_file:
        output.update(_load_pid_file(pid_file))
    return output


def _process_info(proc: psutil.Process, windows_by_pid: dict[int, list[str]]) -> dict[str, Any]:
    try:
        name = proc.name()
    except psutil.Error:
        name = ""
    try:
        create_time = proc.create_time()
    except psutil.Error:
        create_time = None
    try:
        cmdline = proc.cmdline()
    except psutil.Error as exc:
        cmdline = [f"<unavailable: {type(exc).__name__}>"]
    try:
        ppid = proc.ppid()
    except psutil.Error:
        ppid = None
    pid = int(proc.pid)
    window_titles = windows_by_pid.get(pid, [])
    return {
        "pid": pid,
        "ppid": ppid,
        "name": name,
        "exe": _safe(lambda: proc.exe()),
        "cmdline": cmdline,
        "create_time": create_time,
        "age_s": round(time.time() - create_time, 3) if create_time else None,
        "status": _safe(lambda: proc.status()),
        "has_visible_window": bool(window_titles),
        "window_titles": window_titles,
    }


def _safe(call, default: Any = None) -> Any:
    try:
        return call()
    except Exception:
        return default


def _candidate_processes(args: argparse.Namespace) -> list[dict[str, Any]]:
    target_pids = _target_pids(args)
    windows_by_pid = _visible_windows_by_pid()
    items: list[dict[str, Any]] = []
    now = time.time()
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = (proc.info.get("name") or proc.name() or "").lower()
        except psutil.Error:
            continue
        if target_pids:
            if int(proc.pid) not in target_pids:
                continue
        elif name not in AEDT_PROCESS_NAMES:
            continue
        info = _process_info(proc, windows_by_pid)
        reasons: list[str] = []
        if target_pids:
            reasons.append("explicit_pid")
        if name in AEDT_PROCESS_NAMES:
            reasons.append("aedt_process_name")
        if args.no_window_only and info["has_visible_window"]:
            info["eligible"] = False
            info["skip_reason"] = "visible_window"
            items.append(info)
            continue
        if not args.allow_windowed and target_pids and info["has_visible_window"]:
            info["eligible"] = False
            info["skip_reason"] = "visible_window_explicit_pid_requires_allow_windowed"
            items.append(info)
            continue
        create_time = info.get("create_time")
        if args.started_after_epoch is not None and create_time and create_time < args.started_after_epoch:
            info["eligible"] = False
            info["skip_reason"] = "started_before_threshold"
            items.append(info)
            continue
        if args.min_age_s > 0 and create_time and now - create_time < args.min_age_s:
            info["eligible"] = False
            info["skip_reason"] = "younger_than_min_age"
            items.append(info)
            continue
        info["eligible"] = True
        info["match_reasons"] = reasons
        items.append(info)
    return items


def _terminate_pid(pid: int, *, kill_after_s: float) -> dict[str, Any]:
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return {"pid": pid, "action": "none", "ok": True, "reason": "already_exited"}
    try:
        proc.terminate()
        try:
            proc.wait(timeout=kill_after_s)
            return {"pid": pid, "action": "terminate", "ok": True}
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=max(1.0, kill_after_s))
            return {"pid": pid, "action": "kill_after_timeout", "ok": True}
    except Exception as exc:
        return {"pid": pid, "action": "terminate", "ok": False, "error_type": type(exc).__name__, "error": str(exc)}


def _parent_alive(parent_pid: int | None) -> bool:
    if parent_pid is None:
        return False
    try:
        return psutil.pid_exists(parent_pid)
    except Exception:
        return False


def run_once(args: argparse.Namespace) -> dict[str, Any]:
    candidates = _candidate_processes(args)
    eligible = [item for item in candidates if item.get("eligible")]
    payload: dict[str, Any] = {
        "mode": "execute" if args.execute else "dry_run",
        "timestamp_epoch": round(time.time(), 3),
        "target_pids": sorted(_target_pids(args)),
        "no_window_only": args.no_window_only,
        "allow_windowed": args.allow_windowed,
        "min_age_s": args.min_age_s,
        "started_after_epoch": args.started_after_epoch,
        "candidates": candidates,
        "eligible_pids": [item["pid"] for item in eligible],
    }
    if args.execute:
        payload["reap_results"] = [_terminate_pid(int(item["pid"]), kill_after_s=args.kill_after_s) for item in eligible]
    return payload


def run_watch(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    iterations: list[dict[str, Any]] = []
    parent_gone_since: float | None = None
    while True:
        parent_alive = _parent_alive(args.parent_pid)
        if args.parent_pid is not None and not parent_alive and parent_gone_since is None:
            parent_gone_since = time.monotonic()
        should_reap = args.parent_pid is None or (
            parent_gone_since is not None and time.monotonic() - parent_gone_since >= args.grace_after_parent_exit_s
        )
        if should_reap:
            child_args = argparse.Namespace(**vars(args))
            child_args.watch = False
            child_args.execute = args.execute
            payload = run_once(child_args)
            payload["parent_pid"] = args.parent_pid
            payload["parent_alive"] = parent_alive
            payload["watch_elapsed_s"] = round(time.monotonic() - started, 3)
            return payload
        snapshot = run_once(argparse.Namespace(**{**vars(args), "execute": False, "watch": False}))
        snapshot["parent_alive"] = parent_alive
        snapshot["elapsed_s"] = round(time.monotonic() - started, 3)
        iterations.append(snapshot)
        if args.timeout_s and time.monotonic() - started >= args.timeout_s:
            return {
                "mode": "watch_timeout",
                "parent_pid": args.parent_pid,
                "iterations": iterations[-args.keep_iterations :],
                "elapsed_s": round(time.monotonic() - started, 3),
            }
        time.sleep(args.interval_s)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run or reap headless AEDT automation processes.")
    parser.add_argument("--pid", type=int, action="append", default=[], help="Explicit AEDT PID to monitor/reap. Repeatable.")
    parser.add_argument("--pid-file", type=Path, action="append", default=[], help="JSON or text file containing pid/pids.")
    parser.add_argument("--parent-pid", type=int, default=None, help="Automation parent PID. In --watch mode, reap after this process exits.")
    parser.add_argument("--watch", action="store_true", help="Monitor until parent exits or timeout expires.")
    parser.add_argument("--execute", action="store_true", help="Actually terminate eligible processes. Default is dry-run.")
    parser.add_argument("--no-window-only", action=argparse.BooleanOptionalAction, default=True, help="Only match processes without visible windows.")
    parser.add_argument("--allow-windowed", action="store_true", help="Allow explicit PID reaping even if it has a visible window.")
    parser.add_argument("--min-age-s", type=float, default=0.0)
    parser.add_argument("--started-after-epoch", type=float, default=None)
    parser.add_argument("--interval-s", type=float, default=10.0)
    parser.add_argument("--timeout-s", type=float, default=0.0)
    parser.add_argument("--grace-after-parent-exit-s", type=float, default=5.0)
    parser.add_argument("--kill-after-s", type=float, default=10.0)
    parser.add_argument("--keep-iterations", type=int, default=6)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_watch(args) if args.watch else run_once(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    failed = any(not item.get("ok", True) for item in payload.get("reap_results", []))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
