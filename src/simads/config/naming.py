"""Config-driven naming helpers for generated simulation artifacts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from simads.runtime.manifest import safe_id

from .stackups import StackupConfig


DEFAULT_LEGACY_STACKUP_TOKENS = (
    "fr4_210um",
    "fr4_2104um",
    "ro4350b_508um",
)


def _safe_lower_token(value: str) -> str:
    token = safe_id(value).strip("._-").lower()
    return token or "stackup"


def stackup_name_token(stackup: StackupConfig | str) -> str:
    if isinstance(stackup, StackupConfig):
        raw_naming = stackup.raw.get("naming") if isinstance(stackup.raw, dict) else None
        if isinstance(raw_naming, dict) and raw_naming.get("token"):
            return _safe_lower_token(str(raw_naming["token"]))
        return _safe_lower_token(stackup.stackup_id)
    return _safe_lower_token(stackup)


def stackup_legacy_tokens(stackup: StackupConfig) -> tuple[str, ...]:
    tokens: list[str] = []
    raw_naming = stackup.raw.get("naming") if isinstance(stackup.raw, dict) else None
    if isinstance(raw_naming, dict):
        raw_tokens = raw_naming.get("replace_tokens")
        if isinstance(raw_tokens, list):
            tokens.extend(str(token) for token in raw_tokens if str(token).strip())
    tokens.extend(DEFAULT_LEGACY_STACKUP_TOKENS)
    seen: set[str] = set()
    output: list[str] = []
    for token in tokens:
        normalized = token.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(normalized)
    return tuple(output)


def name_has_token(name: str, token: str) -> bool:
    return token.lower() in name.lower()


def name_with_stackup_token(name: str, stackup: StackupConfig | str) -> str:
    base = safe_id(name).strip("._-")
    token = stackup_name_token(stackup)
    if name_has_token(base, token):
        return base

    if isinstance(stackup, StackupConfig):
        for legacy in stackup_legacy_tokens(stackup):
            pattern = re.compile(rf"(?i)(^|[_\-.]){re.escape(legacy)}($|[_\-.])")
            match = pattern.search(base)
            if match:
                return f"{base[:match.start(1)]}{match.group(1)}{token}{match.group(2)}{base[match.end(2):]}"

    return f"{base}_{token}"


def path_with_stackup_token(path: Path, stackup: StackupConfig | str) -> Path:
    return path.with_name(name_with_stackup_token(path.name, stackup))


def stackup_naming_metadata(stackup: StackupConfig, config_path: Path | None = None) -> dict[str, Any]:
    return {
        "stackup_id": stackup.stackup_id,
        "stackup_token": stackup_name_token(stackup),
        "stackup_config": str(config_path) if config_path is not None else None,
        "signal_layer": stackup.geometry.signal_layer,
        "reference_ground_layer": stackup.geometry.reference_ground_layer,
        "via_top_layer": stackup.geometry.via_top_layer,
        "via_bottom_layer": stackup.geometry.via_bottom_layer,
        "signal_to_reference_height_mm": stackup.signal_to_reference_height_mm,
        "total_thickness_mm": stackup.total_thickness_mm,
    }


__all__ = [
    "name_with_stackup_token",
    "path_with_stackup_token",
    "stackup_legacy_tokens",
    "stackup_name_token",
    "stackup_naming_metadata",
]
