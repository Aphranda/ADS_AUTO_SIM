"""Write-safety guards for ADS workspace mutations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SAFETY_POLICY_VERSION = "ads_write_safety_v1"


class AdsWriteSafetyError(RuntimeError):
    """Raised when an ADS workspace write violates the safety policy."""


def ads_decode_cell_name(value: str) -> str:
    """Decode ADS uppercase directory names such as ``%B%F%P`` to ``BFP``."""
    decoded: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "%" and i + 1 < len(value):
            decoded.append(value[i + 1])
            i += 2
            continue
        decoded.append(value[i])
        i += 1
    return "".join(decoded)


def normalize_cell_name(value: str | Path) -> str:
    token = str(value).strip().replace("\\", "/").rstrip("/").split("/")[-1]
    return ads_decode_cell_name(token).casefold()


def cells_match(left: str | Path, right: str | Path) -> bool:
    return normalize_cell_name(left) == normalize_cell_name(right)


@dataclass(frozen=True)
class AdsWriteContext:
    profile_id: str
    workspace: Path
    library: str
    template_cell: str
    target_cell: str
    force: bool = False

    def to_manifest(self) -> dict[str, object]:
        return {
            "policy_version": SAFETY_POLICY_VERSION,
            "profile_id": self.profile_id,
            "workspace": str(self.workspace),
            "library": self.library,
            "template_cell": self.template_cell,
            "target_cell": self.target_cell,
            "target_is_template": cells_match(self.target_cell, self.template_cell),
            "force": self.force,
        }


def validate_ads_cell_write(context: AdsWriteContext, *, operation: str) -> dict[str, object]:
    if cells_match(context.target_cell, context.template_cell) and not context.force:
        raise AdsWriteSafetyError(
            f"{operation} refused: target cell equals template cell "
            f"(target_cell={context.target_cell}, template_cell={context.template_cell}). "
            "Rerun with --force only for an intentional template write."
        )
    return {**context.to_manifest(), "operation": operation, "allowed": True}


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        _resolved(path).relative_to(_resolved(parent))
        return True
    except ValueError:
        return False


def guard_directory_delete(delete_path: Path, *, required_parent: Path, operation: str) -> None:
    if _resolved(delete_path) == _resolved(required_parent):
        raise AdsWriteSafetyError(f"{operation} refused: delete target is the required parent directory: {delete_path}")
    if not is_relative_to(delete_path, required_parent):
        raise AdsWriteSafetyError(
            f"{operation} refused: delete target is outside required parent "
            f"(target={delete_path}, required_parent={required_parent})."
        )


def validate_substrate_patch(path: Path, *, force: bool, will_modify: bool) -> None:
    if will_modify and not force:
        raise AdsWriteSafetyError(
            f"substrate patch refused: {path} would be modified. "
            "Rerun with --force for an intentional ADS substrate change."
        )


__all__ = [
    "AdsWriteContext",
    "AdsWriteSafetyError",
    "SAFETY_POLICY_VERSION",
    "ads_decode_cell_name",
    "cells_match",
    "guard_directory_delete",
    "is_relative_to",
    "normalize_cell_name",
    "validate_ads_cell_write",
    "validate_substrate_patch",
]
