#!/usr/bin/env python3
"""Summarize suspected saved-geometry launch gaps from AEDB hint JSON files."""

from __future__ import annotations

import argparse
import json
from math import hypot
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _coords_for_token(data: dict[str, Any], token: str) -> list[dict[str, Any]]:
    coords = []
    for occurrence in data.get("tokens", {}).get(token, []):
        for coord in occurrence.get("explicit_coordinates", []):
            if coord.get("x_mm") is None or coord.get("y_mm") is None:
                continue
            coords.append({"token": token, "offset": occurrence.get("offset"), "x_mm": coord["x_mm"], "y_mm": coord["y_mm"], "raw": coord})
    return coords


def _points_from_pairs(data: dict[str, Any], tokens: list[str]) -> list[dict[str, Any]]:
    points = []
    for token in tokens:
        for occurrence in data.get("tokens", {}).get(token, []):
            for pair in occurrence.get("coordinate_pairs", []):
                x_mm = pair.get("x_mm")
                y_mm = pair.get("y_mm")
                if x_mm is None or y_mm is None:
                    continue
                if -200.0 <= x_mm <= 200.0 and -200.0 <= y_mm <= 200.0:
                    points.append(
                        {
                            "token": token,
                            "offset": occurrence.get("offset"),
                            "x_mm": x_mm,
                            "y_mm": y_mm,
                            "gap_bytes": pair.get("gap_bytes"),
                        }
                    )
    return points


def _nearest(point: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    ranked = []
    for candidate in candidates:
        dx = candidate["x_mm"] - point["x_mm"]
        dy = candidate["y_mm"] - point["y_mm"]
        ranked.append((hypot(dx, dy), dx, dy, candidate))
    ranked.sort(key=lambda item: item[0])
    distance, dx, dy, candidate = ranked[0]
    return {"distance_mm": distance, "dx_mm": dx, "dy_mm": dy, "candidate": candidate}


def summarize(args: argparse.Namespace) -> dict[str, Any]:
    connector_data = json.loads(args.connector_hints.read_text(encoding="utf-8-sig"))
    object_data = json.loads(args.object_hints.read_text(encoding="utf-8-sig"))
    port1_coords = _coords_for_token(connector_data, args.port1_token)
    port2_coords = _coords_for_token(connector_data, args.port2_token)
    object_points = _points_from_pairs(object_data, args.object_token)

    filtered_objects = [
        point
        for point in object_points
        if args.min_object_x_mm <= point["x_mm"] <= args.max_object_x_mm
        and args.min_object_y_mm <= point["y_mm"] <= args.max_object_y_mm
        and point.get("gap_bytes") == 8
    ]
    port1_filtered = [
        point
        for point in port1_coords
        if args.min_port1_x_mm <= point["x_mm"] <= args.max_port1_x_mm
        and args.min_port1_y_mm <= point["y_mm"] <= args.max_port1_y_mm
    ]
    port2_filtered = [
        point
        for point in port2_coords
        if args.min_port2_x_mm <= point["x_mm"] <= args.max_port2_x_mm
        and args.min_port2_y_mm <= point["y_mm"] <= args.max_port2_y_mm
    ]

    port1_nearest = [_nearest(point, filtered_objects) | {"source": point} for point in port1_filtered if _nearest(point, filtered_objects)]
    port2_nearest = [_nearest(point, filtered_objects) | {"source": point} for point in port2_filtered if _nearest(point, filtered_objects)]
    port1_nearest.sort(key=lambda item: item["distance_mm"])
    port2_nearest.sort(key=lambda item: item["distance_mm"])

    return {
        "connector_hints": str(args.connector_hints),
        "object_hints": str(args.object_hints),
        "object_tokens": args.object_token,
        "port1_candidates": port1_filtered,
        "port2_candidates": port2_filtered,
        "object_points_considered": filtered_objects[: args.max_points],
        "object_points_total": len(filtered_objects),
        "nearest_object_from_port1": port1_nearest[: args.max_nearest],
        "nearest_object_from_port2": port2_nearest[: args.max_nearest],
        "diagnosis": _diagnose(port1_nearest, port2_nearest, args.warn_gap_mm, args.healthy_baseline),
    }


def _diagnose(
    port1_nearest: list[dict[str, Any]],
    port2_nearest: list[dict[str, Any]],
    warn_gap_mm: float,
    healthy_baseline: bool,
) -> list[str]:
    findings = []
    findings.append(
        "distance-to-extracted-RF-object is a geometry hint only; connector face excitation can be physically separated "
        "from PCB copper by the connector pin/solder launch."
    )
    if healthy_baseline:
        findings.append("healthy baseline mode: do not classify connector-face distance as a fault.")
        return findings
    if port1_nearest and port1_nearest[0]["distance_mm"] > warn_gap_mm:
        findings.append(
            "connector-side port is far from the nearest extracted RF object, but this is not sufficient evidence of an open "
            f"({port1_nearest[0]['distance_mm']:.3f} mm > {warn_gap_mm:.3f} mm)"
        )
    if port2_nearest and port2_nearest[0]["distance_mm"] <= warn_gap_mm:
        findings.append(
            "PCB-side Port2 is close to an extracted RF object "
            f"({port2_nearest[0]['distance_mm']:.3f} mm <= {warn_gap_mm:.3f} mm)"
        )
    if port1_nearest and port2_nearest and port1_nearest[0]["distance_mm"] > port2_nearest[0]["distance_mm"] * 5:
        findings.append("gap asymmetry should be compared against a known-good launch before drawing a fault conclusion")
    return findings


def _print_summary(payload: dict[str, Any]) -> None:
    print(f"object_points_total={payload['object_points_total']}")
    for label in ("nearest_object_from_port1", "nearest_object_from_port2"):
        print(f"\n{label}:")
        for item in payload.get(label, [])[:4]:
            source = item["source"]
            candidate = item["candidate"]
            print(
                "  d={:.3f}mm dx={:.3f} dy={:.3f} source=({:.3f},{:.3f}) object=({:.3f},{:.3f}) token={}".format(
                    item["distance_mm"],
                    item["dx_mm"],
                    item["dy_mm"],
                    source["x_mm"],
                    source["y_mm"],
                    candidate["x_mm"],
                    candidate["y_mm"],
                    candidate["token"],
                )
            )
    for finding in payload.get("diagnosis", []):
        print(f"diagnosis: {finding}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize saved launch geometry gap.")
    parser.add_argument("--connector-hints", type=Path, required=True)
    parser.add_argument("--object-hints", type=Path, required=True)
    parser.add_argument("--port1-token", default="Port1")
    parser.add_argument("--port2-token", default="Port2")
    parser.add_argument("--object-token", action="append", default=["rect_1881", "line__291", "line__294"])
    parser.add_argument("--min-port1-x-mm", type=float, default=-45.0)
    parser.add_argument("--max-port1-x-mm", type=float, default=-35.0)
    parser.add_argument("--min-port1-y-mm", type=float, default=-30.0)
    parser.add_argument("--max-port1-y-mm", type=float, default=-20.0)
    parser.add_argument("--min-port2-x-mm", type=float, default=-36.0)
    parser.add_argument("--max-port2-x-mm", type=float, default=-30.0)
    parser.add_argument("--min-port2-y-mm", type=float, default=-6.0)
    parser.add_argument("--max-port2-y-mm", type=float, default=-2.0)
    parser.add_argument("--min-object-x-mm", type=float, default=-45.0)
    parser.add_argument("--max-object-x-mm", type=float, default=-30.0)
    parser.add_argument("--min-object-y-mm", type=float, default=-18.0)
    parser.add_argument("--max-object-y-mm", type=float, default=-2.0)
    parser.add_argument("--warn-gap-mm", type=float, default=2.0)
    parser.add_argument("--healthy-baseline", action="store_true")
    parser.add_argument("--max-points", type=int, default=80)
    parser.add_argument("--max-nearest", type=int, default=8)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = summarize(args)
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
