from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_module():
    module_path = Path("tools/hfss/check_hfss_script_classes.py")
    spec = importlib.util.spec_from_file_location("check_hfss_script_classes", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_hfss_script_registry_covers_current_tool_scripts() -> None:
    module = _load_module()

    payload = module.validate_registry(module.load_registry())

    assert payload["status"] == "ok"
    assert payload["missing"] == []
    assert payload["stale"] == []


def test_probe_prefixed_scripts_are_not_production_allowed() -> None:
    module = _load_module()
    registry = {
        "schema_version": "1.0",
        "scripts": {
            "tools/hfss/probe_bad.py": {
                "class": "production",
                "runtime": "host/pyaedt",
                "production_allowed": True,
            }
        },
    }

    payload = module.validate_registry(registry, repo_root=Path("unit-root"))

    assert payload["status"] == "failed"
    assert any("probe/try/scan script must be class=probe" in item for item in payload["errors"])
