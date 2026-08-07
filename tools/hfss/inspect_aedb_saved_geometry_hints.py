#!/usr/bin/env python3
"""Extract saved geometry hints from a mixed binary/text AEDB edb.def file.

This is not a full EDB parser. It is a conservative read-only helper for
triage when PyEDB/AEDT live APIs are unavailable. It locates named tokens such
as ports, nets, and polygon IDs, then extracts plausible little-endian doubles
near those records so humans can compare saved coordinates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct
from typing import Any

UNIT_TO_MM = {"mm": 1.0, "mil": 0.0254, "m": 1000.0}


def _json_default(value: Any) -> str:
    return str(value)


def _clean_text(data: bytes, *, limit: int = 400) -> str:
    text = data.decode("utf-8", errors="replace")
    chars = []
    for char in text:
        code = ord(char)
        if char in "\t " or 32 <= code < 127:
            chars.append(char)
        elif char in "\r\n":
            chars.append(" ")
        else:
            chars.append(" ")
    return re.sub(r"\s+", " ", "".join(chars)).strip()[:limit]


def _plausible_doubles(data: bytes, base_offset: int, *, min_abs: float, max_abs: float) -> list[dict[str, Any]]:
    values = []
    for rel in range(0, max(0, len(data) - 7)):
        try:
            value = struct.unpack("<d", data[rel : rel + 8])[0]
        except struct.error:
            continue
        if value != value:
            continue
        if min_abs <= abs(value) <= max_abs:
            values.append({"offset": base_offset + rel, "rel": rel, "value_m": value, "value_mm": value * 1000.0})
    return values


def _coordinate_pairs(values: list[dict[str, Any]], *, max_gap: int = 8) -> list[dict[str, Any]]:
    pairs = []
    by_offset = {item["offset"]: item for item in values}
    for item in values:
        for gap in range(1, max_gap + 1):
            other = by_offset.get(item["offset"] + gap)
            if other:
                pairs.append(
                    {
                        "x_offset": item["offset"],
                        "y_offset": other["offset"],
                        "gap_bytes": gap,
                        "x_m": item["value_m"],
                        "y_m": other["value_m"],
                        "x_mm": item["value_mm"],
                        "y_mm": other["value_mm"],
                    }
                )
    return pairs


def _parse_unit_value(value: str) -> float | None:
    match = re.fullmatch(r"\s*([-+0-9.eE]+)\s*(mm|mil|m)\s*", value)
    if not match:
        return None
    return float(match.group(1)) * UNIT_TO_MM[match.group(2)]


def _explicit_coordinates(text: str) -> list[dict[str, Any]]:
    coords = []
    for match in re.finditer(r"\bx='([^']+)'\s*,\s*y='([^']+)'", text):
        x_mm = _parse_unit_value(match.group(1))
        y_mm = _parse_unit_value(match.group(2))
        coords.append({"x": match.group(1), "y": match.group(2), "x_mm": x_mm, "y_mm": y_mm})
    return coords


def _object_tokens(text: str) -> list[str]:
    tokens = re.findall(r"\b(?:poly|rect|line|via|text|arc|path)_[A-Za-z0-9_]+\b", text)
    return list(dict.fromkeys(tokens))


def _token_occurrences(data: bytes, token: str, args: argparse.Namespace) -> list[dict[str, Any]]:
    needle = token.encode("utf-8")
    output = []
    start = 0
    while True:
        pos = data.find(needle, start)
        if pos < 0:
            break
        lo = max(0, pos - args.before)
        hi = min(len(data), pos + len(needle) + args.after)
        window = data[lo:hi]
        doubles = _plausible_doubles(window, lo, min_abs=args.min_abs_m, max_abs=args.max_abs_m)
        clean = _clean_text(window, limit=args.text_limit)
        output.append(
            {
                "token": token,
                "offset": pos,
                "window_start": lo,
                "window_end": hi,
                "text": clean,
                "explicit_coordinates": _explicit_coordinates(clean),
                "object_tokens": _object_tokens(clean),
                "doubles": doubles[: args.max_doubles],
                "coordinate_pairs": _coordinate_pairs(doubles)[: args.max_pairs],
                "doubles_truncated": len(doubles) > args.max_doubles,
            }
        )
        if 0 <= args.max_occurrences <= len(output):
            break
        start = pos + len(needle)
    return output


def _summarize_token_hits(occurrences: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"occurrences": len(occurrences)}
    pair_points = []
    for occurrence in occurrences:
        for pair in occurrence.get("coordinate_pairs", []):
            x_mm = pair["x_mm"]
            y_mm = pair["y_mm"]
            if -200.0 <= x_mm <= 200.0 and -200.0 <= y_mm <= 200.0:
                pair_points.append({"offset": occurrence["offset"], "x_mm": x_mm, "y_mm": y_mm, "gap_bytes": pair["gap_bytes"]})
    summary["candidate_points_mm"] = pair_points[:20]
    summary["candidate_points_truncated"] = len(pair_points) > 20
    summary["explicit_coordinates_mm"] = [
        {"offset": occurrence["offset"], **coord}
        for occurrence in occurrences
        for coord in occurrence.get("explicit_coordinates", [])
    ][:20]
    summary["object_tokens"] = list(
        dict.fromkeys(token for occurrence in occurrences for token in occurrence.get("object_tokens", []))
    )[:40]
    return summary


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    edb_def = args.edb / "edb.def" if args.edb.is_dir() else args.edb
    data = edb_def.read_bytes()
    token_results = {token: _token_occurrences(data, token, args) for token in args.token}
    return {
        "edb_def": str(edb_def),
        "size_bytes": len(data),
        "tokens": token_results,
        "summary": {token: _summarize_token_hits(items) for token, items in token_results.items()},
        "notes": [
            "Coordinates are heuristic little-endian double extractions near text tokens.",
            "Use candidate points as saved-state hints only; confirm final geometry in AEDT when live APIs are available.",
        ],
    }


def _print_summary(payload: dict[str, Any]) -> None:
    print(f"edb_def={payload['edb_def']}")
    for token, item in payload.get("summary", {}).items():
        print(f"\n[{token}] occurrences={item.get('occurrences')}")
        for point in item.get("candidate_points_mm", [])[:8]:
            print(
                "  offset={offset} x={x_mm:.3f}mm y={y_mm:.3f}mm gap={gap_bytes}".format(
                    **point
                )
            )
        for coord in item.get("explicit_coordinates_mm", [])[:6]:
            print(f"  explicit offset={coord['offset']} x={coord['x']} y={coord['y']} -> {coord['x_mm']:.3f}mm,{coord['y_mm']:.3f}mm")
        if item.get("object_tokens"):
            print("  objects=" + ", ".join(item["object_tokens"][:12]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect saved AEDB geometry hints.")
    parser.add_argument("--edb", type=Path, required=True, help="AEDB folder or edb.def path.")
    parser.add_argument("--token", action="append", required=True)
    parser.add_argument("--before", type=int, default=160)
    parser.add_argument("--after", type=int, default=420)
    parser.add_argument("--min-abs-m", type=float, default=1e-6)
    parser.add_argument("--max-abs-m", type=float, default=0.25)
    parser.add_argument("--max-occurrences", type=int, default=8)
    parser.add_argument("--max-doubles", type=int, default=80)
    parser.add_argument("--max-pairs", type=int, default=80)
    parser.add_argument("--text-limit", type=int, default=1200)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.summary:
        _print_summary(payload)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
