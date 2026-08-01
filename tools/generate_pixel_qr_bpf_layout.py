#!/usr/bin/env python3
"""Compatibility wrapper for tools/layout/generate_pixel_qr_bpf_layout.py."""

from __future__ import annotations

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "layout" / "generate_pixel_qr_bpf_layout.py"), run_name="__main__")
