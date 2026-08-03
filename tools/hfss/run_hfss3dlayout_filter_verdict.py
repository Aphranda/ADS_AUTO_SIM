#!/usr/bin/env python3
"""Compatibility CLI for the HFSS 3D Layout verdict workflow."""

from __future__ import annotations

from pathlib import Path
import sys


SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.hfss.workflow import main


if __name__ == "__main__":
    main()
