from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_module():
    module_path = Path("tools/hfss/duplicate_hfss3dlayout_design.py")
    spec = importlib.util.spec_from_file_location("duplicate_hfss3dlayout_design", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_duplicate_design_dry_run_finishes_without_session(tmp_path: Path) -> None:
    module = _load_module()
    args = module.parse_args(
        [
            "--project",
            str(tmp_path / "unit.aedt"),
            "--source-design",
            "BFP",
            "--target-design",
            "BFP_candidate",
        ]
    )

    payload = module.duplicate_design(args)

    assert payload["status"] == "dry_run"
    assert payload["execute"] is False


def test_duplicate_design_blocks_existing_target_without_delete(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()

    class FakeApp:
        design_list = ["BFP", "BFP_candidate"]

    class FakeSession:
        app = FakeApp()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def metadata(self):
            return {}

    monkeypatch.setattr(module, "open_hfss3dlayout_session", lambda config, lifecycle: FakeSession())
    args = module.parse_args(
        [
            "--project",
            str(tmp_path / "unit.aedt"),
            "--source-design",
            "BFP",
            "--target-design",
            "BFP_candidate",
            "--execute",
        ]
    )

    payload = module.duplicate_design(args)

    assert payload["status"] == "target_design_exists"


def test_duplicate_design_executes_with_delete_existing_and_save(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    calls: list[tuple[str, object]] = []

    class FakeApp:
        def __init__(self):
            self.design_list = ["BFP", "BFP_candidate"]

        def delete_design(self, name):
            calls.append(("delete", name))
            self.design_list.remove(name)
            return True

        def set_active_design(self, name):
            calls.append(("active", name))

        def duplicate_design(self, name, save_after_duplicate=False):
            calls.append(("duplicate", (name, save_after_duplicate)))
            self.design_list.append(name)
            return True

        def save_project(self, path, overwrite=True):
            calls.append(("save", (path, overwrite)))
            return True

    class FakeSession:
        def __init__(self):
            self.app = FakeApp()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def metadata(self):
            return {"aedt_ready": {"design_name": "BFP"}}

    monkeypatch.setattr(module, "open_hfss3dlayout_session", lambda config, lifecycle: FakeSession())
    args = module.parse_args(
        [
            "--project",
            str(tmp_path / "unit.aedt"),
            "--source-design",
            "BFP",
            "--target-design",
            "BFP_candidate",
            "--delete-existing",
            "--execute",
            "--save",
        ]
    )

    payload = module.duplicate_design(args)

    assert payload["status"] == "duplicated"
    assert payload["created_design_detected"] is True
    assert ("delete", "BFP_candidate") in calls
    assert ("active", "BFP") in calls
    assert ("duplicate", ("BFP_candidate", False)) in calls
    assert calls[-1][0] == "save"
