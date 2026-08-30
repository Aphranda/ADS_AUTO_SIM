#!/usr/bin/env python3
"""Compatibility wrapper for ADS installation/workspace profiles."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from simads.config.profiles import (  # noqa: E402,F401
    build_ads_env,
    ADS_PROFILES,
    AdsProfile,
    ProfileCheck,
    get_ads_profile,
    profile_names,
    resolve_ads_python,
    resolve_host_python,
    resolve_layer_map,
    resolve_library,
    resolve_substrate,
    resolve_substrate_library,
    resolve_workspace,
    validate_profile,
)
