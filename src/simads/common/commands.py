"""Command planning helpers shared by CLI wrappers and workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandPlan:
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


def _quote(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(char.isspace() for char in text):
        return f'"{text}"'
    return text
