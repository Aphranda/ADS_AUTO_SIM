"""JSON exporter for layout geometry."""

from __future__ import annotations

import json
from pathlib import Path

from simads.geometry import Layout, to_dict


def write_layout_json(path: Path, layout: Layout) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_dict(layout), ensure_ascii=False, indent=2), encoding="utf-8")

