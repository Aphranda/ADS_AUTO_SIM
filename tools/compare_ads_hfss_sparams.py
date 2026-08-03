#!/usr/bin/env python3
"""Compare ADS and HFSS S-parameter traces."""

from __future__ import annotations

import sys
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.workflows.sparam_compare import main


if __name__ == "__main__":
    main()
