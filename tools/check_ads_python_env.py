#!/usr/bin/env python3
"""Check whether the current Python can import Keysight ADS automation APIs."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.config import get_ads_profile, profile_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ADS Python import smoke test.")
    parser.add_argument("--profile", default="auto", choices=profile_names(include_auto=True), help="Use ADS root from a configured profile.")
    parser.add_argument("--ads-root", type=Path, default=None, help="Explicit ADS root used to set HPEESOF_DIR.")
    return parser.parse_args()


def ensure_hpeesof_dir(ads_root: Path | None = None) -> None:
    if ads_root is not None:
        os.environ["HPEESOF_DIR"] = str(ads_root)
        print(f"HPEESOF_DIR set from profile/argument: {os.environ['HPEESOF_DIR']}", flush=True)
        return
    if os.environ.get("HPEESOF_DIR"):
        print(f"HPEESOF_DIR already set: {os.environ['HPEESOF_DIR']}", flush=True)
        return
    executable = Path(sys.executable).resolve()
    if executable.parts[-3:-1] == ("tools", "python"):
        os.environ["HPEESOF_DIR"] = str(executable.parents[2])
        print(f"HPEESOF_DIR inferred: {os.environ['HPEESOF_DIR']}", flush=True)
    else:
        print("HPEESOF_DIR is not set and cannot be inferred from this Python.", flush=True)


def import_module(name: str) -> object:
    print(f"Importing {name}...", flush=True)
    __import__(name)
    module = sys.modules[name]
    print(f"Imported {name}", flush=True)
    return module


def test_import_keysight_ads_de_example(ads_root: Path | None = None) -> None:
    ensure_hpeesof_dir(ads_root)
    de = import_module("keysight.ads.de")
    try:
        version = de.version()
    except Exception as exc:
        raise RuntimeError("Imported keysight.ads.de, but de.version() failed.") from exc
    assert version >= 630, "Version of keysight.ads.de is not as expected."
    print(f"Import of keysight.ads.de successful in ADS version {version}.")

    optional_modules = [
        "keysight.ads.ael",
        "keysight.ads.dataset",
        "keysight.edatoolbox",
        "keysight.pwdatatools",
    ]
    for module_name in optional_modules:
        try:
            import_module(module_name)
        except ImportError as exc:
            print(f"WARN: failed to import {module_name}: {exc}", flush=True)

    print(f"HPEESOF_DIR={os.environ.get('HPEESOF_DIR', '')}")
    print(f"Python={sys.executable}")


def main() -> None:
    args = parse_args()
    ads_root = args.ads_root
    if args.profile is not None:
        ads_root = get_ads_profile(args.profile).ads_root
    test_import_keysight_ads_de_example(ads_root)


if __name__ == "__main__":
    main()
