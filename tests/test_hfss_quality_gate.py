import importlib.util
from argparse import Namespace
from pathlib import Path
import subprocess
import sys
from typing import Sequence


def _load_gate_module():
    module_path = Path("tools/hfss/run_hfss_quality_gate.py")
    spec = importlib.util.spec_from_file_location("run_hfss_quality_gate", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _args(**overrides):
    values = {
        "skip_compile": False,
        "skip_pytest": False,
        "skip_smoke": False,
        "compile_target": [],
        "pytest_target": [],
        "compile_timeout_s": 120,
        "pytest_timeout_s": 300,
        "smoke_timeout_s": 600,
        "smoke_output": None,
        "version": "2026.1",
        "non_graphical": True,
        "keep_open": False,
        "profile": "home",
        "host_python": None,
        "strict_profile": False,
    }
    values.update(overrides)
    return Namespace(**values)


def test_build_gate_commands_runs_compile_pytest_then_smoke() -> None:
    gate = _load_gate_module()

    commands = gate.build_gate_commands(_args(), host_python=Path("D:/Python/python.exe"))

    assert [command.name for command in commands] == ["py_compile", "pytest", "aedt_smoke"]
    assert Path(commands[0].command[0]) == Path("D:/Python/python.exe")
    assert commands[0].command[1:3] == ["-m", "py_compile"]
    assert Path(commands[1].command[0]) == Path("D:/Python/python.exe")
    assert commands[1].command[1:3] == ["-m", "pytest"]
    basetemp = commands[1].command[commands[1].command.index("--basetemp") + 1]
    cache_arg = next(item for item in commands[1].command if item.startswith("cache_dir="))
    assert Path(basetemp).name.startswith("hfss_quality_gate_")
    assert Path(cache_arg.removeprefix("cache_dir=")).name.startswith("hfss_quality_gate_")
    assert Path(commands[2].command[0]) == Path("D:/Python/python.exe")
    assert commands[2].command[1] == "tools/hfss/create_hfss3dlayout_smoke_project.py"
    assert "--graphical" not in commands[2].command


def test_build_gate_commands_can_skip_smoke_for_dry_validation() -> None:
    gate = _load_gate_module()

    commands = gate.build_gate_commands(_args(skip_smoke=True), host_python=Path("python.exe"))

    assert [command.name for command in commands] == ["py_compile", "pytest"]


def test_run_gate_stops_after_first_failed_step(monkeypatch) -> None:
    gate = _load_gate_module()

    class FakeProfile:
        name = "unit"
        version = "2026.1"
        host_python = Path("python.exe")

        def to_dict(self):
            return {"profile_id": self.name, "host_python": str(self.host_python), "version": self.version}

    class FakeCheck:
        name = "host_python"
        path = Path("python.exe")
        ok = True
        message = "unit"

    calls: list[list[str]] = []

    def fake_runner(command: Sequence[str], cwd: Path, timeout_s: int):
        calls.append(list(command))
        return subprocess.CompletedProcess(command, 1, stdout="compile failed", stderr="")

    monkeypatch.setattr(gate, "get_hfss_profile", lambda name: FakeProfile())
    monkeypatch.setattr(gate, "validate_hfss_profile", lambda profile: [FakeCheck()])

    payload = gate.run_gate(_args(), runner=fake_runner)

    assert payload["status"] == "failed"
    assert payload["stage"] == "py_compile"
    assert len(calls) == 1
    assert payload["steps"][0]["stdout_tail"] == "compile failed"
