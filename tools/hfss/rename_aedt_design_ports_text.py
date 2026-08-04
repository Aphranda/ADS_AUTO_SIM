#!/usr/bin/env python3
"""Safely rename ports inside named PlanarEMCircuit blocks of an AEDT file."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _backup_project(project: Path) -> list[str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied: list[str] = []
    ignore_runtime_locks = shutil.ignore_patterns("*.semaphore", "*.lock", "*.tmp")
    for src in [project, project.with_suffix(".aedb"), project.with_suffix(".aedtresults")]:
        if not src.exists():
            continue
        dst = src.with_name(f"{src.stem}.before_text_port_rename_{stamp}{src.suffix}")
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore_runtime_locks)
        else:
            shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def _find_planar_blocks(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(r"(?m)^(\t*)\$begin 'PlanarEMCircuit'\r?\n")
    blocks: list[tuple[int, int, str]] = []
    matches = list(pattern.finditer(text))
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else text.find("$end 'DataInstances'", start)
        if end < 0:
            end = len(text)
        block = text[start:end]
        end_marker = re.search(r"(?m)^\t*\$end 'PlanarEMCircuit'\r?$", block)
        if end_marker:
            end = start + end_marker.end()
            block = text[start:end]
        name_match = re.search(r"(?m)^\s*Name='([^']+)'", block)
        if name_match:
            blocks.append((start, end, name_match.group(1)))
    return blocks


def _parse_mapping(values: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"mapping must be OLD=NEW, got {value!r}")
        old, new = value.split("=", 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            raise ValueError(f"mapping must be OLD=NEW, got {value!r}")
        pairs.append((old, new))
    return pairs


def _replace_in_selected_lines(block: str, old: str, new: str, *, indicators: tuple[str, ...]) -> tuple[str, int]:
    total = 0
    out = []
    for line in block.splitlines(keepends=True):
        if "PC(" in line:
            # PC('component_symbol_id', 'Pin_T1') references the connector
            # component's internal pin and must not be renamed to PortN.
            out.append(line)
            continue
        if any(indicator in line for indicator in indicators):
            line, count1 = re.subn(rf"'{re.escape(old)}'", f"'{new}'", line)
            line, count2 = re.subn(rf"@{re.escape(old)};", f"@{new};", line)
            total += count1 + count2
        out.append(line)
    return "".join(out), total


def _find_named_blocks(text: str, name: str) -> list[tuple[int, int]]:
    pattern = re.compile(
        rf"(?ms)^(\s*)\$begin '{re.escape(name)}'\r?\n.*?^\1\$end '{re.escape(name)}'\r?$"
    )
    return [(match.start(), match.end()) for match in pattern.finditer(text)]


def rename_design_ports(args: argparse.Namespace) -> dict[str, Any]:
    text = args.project.read_text(encoding="utf-8-sig", errors="replace")
    mappings = _parse_mapping(args.rename)
    blocks = _find_planar_blocks(text)
    payload: dict[str, Any] = {
        "project": str(args.project),
        "design": args.design,
        "mappings": [{"old": old, "new": new} for old, new in mappings],
        "execute": args.execute,
        "blocks": [{"name": name, "start": start, "end": end} for start, end, name in blocks],
    }
    target = next(((start, end) for start, end, name in blocks if name == args.design), None)
    if target is None:
        payload["status"] = "missing_design"
        return payload

    start, end = target
    block = text[start:end]
    named_blocks = _find_named_blocks(text, args.design)
    payload["named_blocks"] = [{"start": block_start, "end": block_end} for block_start, block_end in named_blocks]
    changes = []
    for old, new in mappings:
        before_count = block.count(f"'{old}'") + block.count(f"@{old};")
        block, count = _replace_in_selected_lines(
            block,
            old,
            new,
            indicators=(
                "PortName=",
                "NetName=",
                "NetInterfacePorts=",
                "Interface(",
                "SchPortInst(",
                "PortName(",
                "$begin '",
                "$end '",
                "Pin=",
            ),
        )
        after_old_count = block.count(f"'{old}'") + block.count(f"@{old};")
        new_count = block.count(f"'{new}'") + block.count(f"@{new};")
        changes.append(
            {
                "old": old,
                "new": new,
                "before_old_count": before_count,
                "replacements": count,
                "after_old_count": after_old_count,
                "after_new_count": new_count,
            }
        )
    text_changes = changes
    replacements_by_named_block: list[dict[str, Any]] = []
    new_text = text[:start] + block + text[end:]
    offset = len(block) - (end - start)
    for original_block_start, original_block_end in named_blocks:
        block_start = original_block_start + (offset if original_block_start > end else 0)
        block_end = original_block_end + (offset if original_block_end > end else 0)
        named_block = new_text[block_start:block_end]
        if block_start <= start < block_end:
            continue
        entry: dict[str, Any] = {"start": block_start, "end": block_end, "changes": []}
        for old, new in mappings:
            before_count = named_block.count(f"'{old}'") + named_block.count(f"@{old};")
            named_block, count = _replace_in_selected_lines(
                named_block,
                old,
                new,
                indicators=("Pin(", "PinName(", "Terminal("),
            )
            entry["changes"].append({"old": old, "new": new, "before_old_count": before_count, "replacements": count})
        replacements_by_named_block.append(entry)
        new_text = new_text[:block_start] + named_block + new_text[block_end:]
        delta = len(named_block) - (block_end - block_start)
        offset += delta
    payload["changes"] = text_changes
    payload["named_block_changes"] = replacements_by_named_block
    if any(item["before_old_count"] == 0 for item in changes):
        payload["status"] = "missing_old_name"
        return payload
    if not args.execute:
        payload["status"] = "dry_run"
        return payload

    payload["backups"] = _backup_project(args.project)
    args.project.write_text(new_text, encoding="utf-8")
    payload["status"] = "renamed"
    payload["written"] = True
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename AEDT ports inside one PlanarEMCircuit design block.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--rename", action="append", required=True, help="OLD=NEW mapping. Repeat as needed.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = rename_design_ports(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
