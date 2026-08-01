"""ADS workspace path helpers.

This module is intentionally ADS-Python independent. It only handles cell names,
workspace paths, and command-plan metadata that can be validated with normal
Python before any ADS process is started.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AdsCellRef:
    workspace: Path
    library: str
    cell: str
    view: str = "layout"

    @property
    def library_dir(self) -> Path:
        return self.workspace / self.library

    @property
    def cell_dir(self) -> Path:
        return find_cell_dir(self.library_dir, self.cell)

    @property
    def view_dir(self) -> Path:
        return self.cell_dir / self.view

    @property
    def lcv(self) -> tuple[str, str, str]:
        return (self.library, self.cell, self.view)

    def label(self) -> str:
        return f"{self.library}:{self.cell}:{self.view}"


@dataclass(frozen=True)
class AdsCommandPlan:
    tool: str
    python: Path
    script: Path
    args: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] | None = None

    def argv(self) -> list[str]:
        return [str(self.python), str(self.script), *self.args]

    def command_line(self) -> str:
        return " ".join(_quote(arg) for arg in self.argv())


def ads_encoded_cell_dir_name(cell_name: str) -> str:
    return "".join(f"%{char}" if "A" <= char <= "Z" else char for char in cell_name)


def find_cell_dir(lib_dir: Path, cell_name: str) -> Path:
    direct = lib_dir / cell_name
    if direct.exists():
        return direct

    encoded = lib_dir / ads_encoded_cell_dir_name(cell_name)
    if encoded.exists():
        return encoded

    for itemdef in lib_dir.glob("*/itemdef.ael"):
        try:
            text = itemdef.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if f'create_item("{cell_name}"' in text:
            return itemdef.parent

    return direct


def _quote(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(char.isspace() for char in text):
        return f'"{text}"'
    return text
