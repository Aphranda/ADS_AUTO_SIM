#!/usr/bin/env python3
"""Compatibility CLI for ADS/HFSS verdict summaries."""

from __future__ import annotations

import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.workflows.verdict_summary import main


if __name__ == "__main__":
    main()
