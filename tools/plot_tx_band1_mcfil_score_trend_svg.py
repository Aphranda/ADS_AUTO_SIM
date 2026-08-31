#!/usr/bin/env python3
"""Render TX Band1 MCFIL score trend from feedback CSV as a compact SVG."""

from __future__ import annotations

import argparse
import csv
import math
import re
from html import escape
from pathlib import Path


def parse_float(value: str) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def parse_round(candidate: str) -> int | None:
    match = re.search(r"_r(\d+)", candidate)
    return int(match.group(1)) if match else None


def load_rows(path: Path) -> list[dict[str, str | float | int]]:
    rows: list[dict[str, str | float | int]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        for index, row in enumerate(csv.DictReader(fp), 1):
            score = parse_float(row.get("tx_score", ""))
            round_no = parse_round(row.get("candidate", ""))
            if score is None or round_no is None:
                continue
            rows.append(
                {
                    "index": index,
                    "round": round_no,
                    "candidate": row["candidate"],
                    "score": score,
                }
            )
    return rows


def nice_bounds(values: list[float]) -> tuple[float, float]:
    low = min(values)
    high = max(values)
    pad = max((high - low) * 0.10, 10.0)
    low = math.floor((low - pad) / 25.0) * 25.0
    high = math.ceil((high + pad) / 25.0) * 25.0
    return low, high


def points_to_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    first, *rest = points
    parts = [f"M {first[0]:.2f} {first[1]:.2f}"]
    parts.extend(f"L {x:.2f} {y:.2f}" for x, y in rest)
    return " ".join(parts)


def render_svg(rows: list[dict[str, str | float | int]], output: Path) -> None:
    if not rows:
        raise ValueError("no valid score rows found")

    by_round: dict[int, dict[str, str | float | int]] = {}
    for row in rows:
        round_no = int(row["round"])
        if round_no not in by_round or float(row["score"]) > float(by_round[round_no]["score"]):
            by_round[round_no] = row

    round_rows = [by_round[key] for key in sorted(by_round)]
    best = max(rows, key=lambda item: float(item["score"]))
    last_round = max(int(row["round"]) for row in rows)
    y_values = [float(row["score"]) for row in round_rows]
    y_values.extend([0.0, float(best["score"])])
    y_min, y_max = nice_bounds(y_values)
    x_min = min(int(row["round"]) for row in round_rows)
    x_max = max(int(row["round"]) for row in round_rows)

    width = 980
    height = 285
    left = 76
    right = 28
    top = 50
    bottom = 48
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(round_no: int) -> float:
        if x_max == x_min:
            return left + plot_w / 2
        return left + (round_no - x_min) / (x_max - x_min) * plot_w

    def sy(score: float) -> float:
        return top + (y_max - score) / (y_max - y_min) * plot_h

    score_points = [(sx(int(row["round"])), sy(float(row["score"]))) for row in round_rows]
    best_points: list[tuple[float, float]] = []
    current_best = -math.inf
    for row in round_rows:
        current_best = max(current_best, float(row["score"]))
        best_points.append((sx(int(row["round"])), sy(current_best)))

    y_ticks = [y_min + (y_max - y_min) * i / 4 for i in range(5)]
    x_ticks = [1, 10, 20, 30, 40, 50, 60, 70, 80]
    x_ticks = [tick for tick in x_ticks if x_min <= tick <= x_max]
    zero_y = sy(0.0)
    best_x = sx(int(best["round"]))
    best_y = sy(float(best["score"]))
    last = max(rows, key=lambda item: (int(item["round"]), int(item["index"])))
    last_x = sx(int(last["round"]))
    last_y = sy(float(last["score"]))

    circles = []
    for row in round_rows:
        x = sx(int(row["round"]))
        y = sy(float(row["score"]))
        circles.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.1" fill="#1f77b4" opacity="0.86"/>')

    grid_lines = []
    y_labels = []
    for tick in y_ticks:
        y = sy(tick)
        grid_lines.append(f'<line x1="{left}" y1="{y:.2f}" x2="{width - right}" y2="{y:.2f}" class="grid"/>')
        y_labels.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" class="axis-label">{tick:.0f}</text>')

    x_labels = []
    for tick in x_ticks:
        x = sx(tick)
        grid_lines.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}" class="grid xgrid"/>')
        x_labels.append(f'<text x="{x:.2f}" y="{height - 20}" text-anchor="middle" class="axis-label">R{tick}</text>')

    best_candidate = escape(str(best["candidate"]))
    last_candidate = escape(str(last["candidate"]))
    subtitle = (
        f"有效反馈 {len(rows)} 条 | 已迭代至 R{last_round} | "
        f"当前最优 R{int(best['round'])} / tx_score {float(best['score']):.3f}"
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="TX Band1 MCFIL score trend">
  <style>
    text{{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;letter-spacing:0}}
    .title{{font-size:20px;font-weight:700;fill:#172033}}
    .subtitle{{font-size:12px;fill:#586474}}
    .axis{{stroke:#263241;stroke-width:1.2}}
    .grid{{stroke:#d8e0ea;stroke-width:1}}
    .xgrid{{stroke-dasharray:3 5}}
    .axis-label{{font-size:10px;fill:#657183}}
    .label{{font-size:11px;fill:#273142}}
    .small{{font-size:10px;fill:#657183}}
    .round-score{{fill:none;stroke:#1f77b4;stroke-width:2.2}}
    .best-score{{fill:none;stroke:#2e7d32;stroke-width:2.8}}
    .zero{{stroke:#94a3b8;stroke-width:1;stroke-dasharray:6 5}}
    .mark{{fill:#ffffff;stroke:#172033;stroke-width:1.3}}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="4" fill="#ffffff" stroke="#d5dce6"/>
  <text x="24" y="29" class="title">评分趋势曲线</text>
  <text x="178" y="29" class="subtitle">{escape(subtitle)}</text>

  <g>
    {''.join(grid_lines)}
    <line x1="{left}" y1="{zero_y:.2f}" x2="{width - right}" y2="{zero_y:.2f}" class="zero"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis"/>
    <line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" class="axis"/>
    {''.join(y_labels)}
    {''.join(x_labels)}
    <text x="22" y="{top + plot_h / 2:.2f}" transform="rotate(-90 22 {top + plot_h / 2:.2f})" text-anchor="middle" class="axis-label">tx_score</text>
    <text x="{left + plot_w / 2:.2f}" y="{height - 7}" text-anchor="middle" class="axis-label">迭代轮次</text>
  </g>

  <path d="{points_to_path(score_points)}" class="round-score"/>
  <path d="{points_to_path(best_points)}" class="best-score"/>
  {''.join(circles)}

  <circle cx="{best_x:.2f}" cy="{best_y:.2f}" r="6.0" fill="#ffffff" stroke="#2e7d32" stroke-width="2.4"/>
  <text x="{best_x + 10:.2f}" y="{best_y - 12:.2f}" class="label" font-weight="700">Best R{int(best['round'])}</text>
  <text x="{best_x + 10:.2f}" y="{best_y + 3:.2f}" class="small">{float(best['score']):.3f}</text>
  <circle cx="{last_x:.2f}" cy="{last_y:.2f}" r="4.6" fill="#ffffff" stroke="#d97706" stroke-width="1.8"/>
  <text x="{last_x - 8:.2f}" y="{last_y - 10:.2f}" text-anchor="end" class="small">R{int(last['round'])} {float(last['score']):.3f}</text>

  <g transform="translate({width - 258} {top + plot_h - 82:.0f})">
    <rect x="0" y="0" width="230" height="64" rx="4" fill="#f8fafc" stroke="#cbd5e1"/>
    <line x1="14" y1="21" x2="54" y2="21" stroke="#1f77b4" stroke-width="2.2"/>
    <circle cx="34" cy="21" r="3.1" fill="#1f77b4"/>
    <text x="66" y="25" class="label">单轮最高评分</text>
    <line x1="14" y1="45" x2="54" y2="45" stroke="#2e7d32" stroke-width="2.8"/>
    <text x="66" y="49" class="label">累计最优评分</text>
  </g>

  <text x="24" y="{height - 17}" class="small">Best: {best_candidate}</text>
  <text x="{width - 28}" y="{height - 17}" text-anchor="end" class="small">Latest: {last_candidate}</text>
</svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("feedback_csv", type=Path)
    parser.add_argument("output_svg", type=Path)
    args = parser.parse_args()
    render_svg(load_rows(args.feedback_csv), args.output_svg)


if __name__ == "__main__":
    main()
