"""ADS naming helpers for path-length constrained FEM runs."""

from __future__ import annotations

import hashlib
import re


def ads_safe_name(value: str) -> str:
    clean = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "cell"


def short_ads_cell_name(candidate: str, *, max_len: int = 40) -> str:
    """Return a stable ADS cell name short enough for FEM simulation paths."""
    stem = ads_safe_name(candidate).removesuffix("_mm_coords")
    digest = hashlib.sha1(stem.encode("utf-8")).hexdigest()[:6]
    suffix = f"_{digest}_mm"
    if len(stem) + len("_mm_coords") <= max_len:
        return f"{stem}_mm_coords"

    replacements = {
        "interdigital": "i",
        "round": "r",
        "retest": "rt",
        "base": "b",
        "taper": "tp",
        "asym": "a",
        "parallel": "p",
        "jlc04161h_7628_1p6mm": "jlc",
        "fr4_210um": "fr4",
    }
    compact = stem
    for old, new in replacements.items():
        compact = compact.replace(old, new)
    compact = ads_safe_name(compact)
    budget = max(8, max_len - len(suffix))
    return f"{compact[:budget].rstrip('_')}{suffix}"


def fem_simulation_path_length(
    *,
    workspace: str,
    library: str,
    cell: str,
    layout_view: str = "layout",
    setup_dir: str = "emSetup_FEM",
) -> int:
    return len(f"{workspace}\\{library}\\simulation\\{library}_{cell}\\{layout_view}\\{setup_dir}")


__all__ = ["ads_safe_name", "fem_simulation_path_length", "short_ads_cell_name"]
