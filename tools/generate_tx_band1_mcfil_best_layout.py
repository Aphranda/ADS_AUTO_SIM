#!/usr/bin/env python3
"""Regenerate the TX_BAND1 MCFIL best-candidate layout from feedback history."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BASE_PARAMS = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil" / "tx_band1_mcfil_r0_params.json"
SUMMARY_ROOT = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil_iter"
FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_corrected_tx_feedback.csv"
OUT_DIR = SUMMARY_ROOT / "round23_regenerated"
TARGET = "tx_band1_mcfil_r23_cnn042_rand33"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def round_no(value: str) -> int | None:
    match = re.search(r"_r(\d+)_cnn", value)
    return int(match.group(1)) if match else None


def trace_layout_id(row: dict[str, str]) -> str | None:
    trace = row.get("trace_csv", "")
    name = Path(trace.replace("\\", "/")).name
    return re.sub(r"_hfss_trace\.csv$", "", name) if name.endswith("_hfss_trace.csv") else None


def row_ids(row: dict[str, str]) -> list[str]:
    ids = [row.get("candidate", "")]
    trace_id = trace_layout_id(row)
    if trace_id:
        ids.append(trace_id)
        ids.append(f"{trace_id}_p2up_graphical")
    candidate = row.get("candidate", "")
    for suffix in ("_p2up_graphical", "_p2up_hidden_graphical"):
        if candidate.endswith(suffix):
            ids.append(candidate.removesuffix(suffix))
    return list(dict.fromkeys(item for item in ids if item))


def alias_ids(layout_id: str) -> list[str]:
    return [layout_id, f"{layout_id}_p2up_graphical", f"{layout_id}_p2up_hidden_graphical"]


def avg(values: list[float]) -> float:
    return sum(values) / len(values)


def params_from_summary(base: dict[str, Any], summary_path: Path) -> dict[str, Any]:
    summary = load_json(summary_path)
    layout_id = str(summary["layout_id"])
    sections = sorted(summary["coupled_sections"], key=lambda item: int(item["section"]))
    base_sections = sorted(base["coupled_sections"], key=lambda item: int(item["section"]))
    length: list[float] = []
    gap: list[float] = []
    width: list[float] = []
    for actual, base_section in zip(sections, base_sections, strict=True):
        length.append(round(float(actual["length_mm"]) - float(base_section["length_mm"]), 6))
        actual_gaps = [float(item) for item in actual.get("coupling_gaps_mm", [])]
        base_gaps = [float(item) for item in base_section.get("coupling_gaps_mm", [])]
        gap.append(round(avg(actual_gaps) - avg(base_gaps), 6))
        actual_widths = [float(strip["width_mm"]) for strip in actual.get("strips", [])]
        base_widths = [float(strip["width_mm"]) for strip in base_section.get("strips", [])]
        width.append(round(avg(actual_widths) - avg(base_widths), 6))

    import tools.make_tx_band_mcfil_cnn_iteration as cnn

    return cnn.set_tuning(
        base,
        layout_id,
        length,
        gap,
        width,
        {
            "round": f"round{round_no(layout_id) or 0}",
            "source": "tools/generate_tx_band1_mcfil_best_layout.py",
            "strategy": "recovered_from_dxf_summary",
        },
    )


def mapped_param(params_by_id: dict[str, dict[str, Any]], row: dict[str, str]) -> dict[str, Any] | None:
    for item in row_ids(row):
        if item in params_by_id:
            return params_by_id[item]
    return None


def register(params_by_id: dict[str, dict[str, Any]], layout_id: str, params: dict[str, Any]) -> None:
    for item in alias_ids(layout_id):
        params_by_id[item] = params


def best_parent(rows: list[dict[str, str]], params_by_id: dict[str, dict[str, Any]], current_round: int) -> dict[str, str]:
    eligible: list[dict[str, str]] = []
    for row in rows:
        rn = round_no(" ".join(row_ids(row)))
        if rn is not None and rn >= current_round:
            continue
        if mapped_param(params_by_id, row) is not None:
            eligible.append(row)
    if not eligible:
        raise ValueError(f"no eligible parent before round {current_round}")
    return max(eligible, key=lambda row: float(row["tx_score"]))


def main() -> int:
    import tools.make_tx_band_mcfil_cnn_iteration as cnn

    base = load_json(BASE_PARAMS)
    rows = read_csv(FEEDBACK)
    params_by_id: dict[str, dict[str, Any]] = {}
    register(params_by_id, "tx_band1_mcfil_r0", base)
    register(params_by_id, "tx_band1_mcfil_alumina_manual_ports", base)

    for summary_path in sorted(SUMMARY_ROOT.glob("round*/tx_band1_mcfil_*_dxf_summary.json")):
        params = params_from_summary(base, summary_path)
        register(params_by_id, str(params["layout_id"]), params)

    parents: dict[int, str] = {}
    for current_round in range(13, 24):
        parent = best_parent(rows, params_by_id, current_round)
        parent_params = mapped_param(params_by_id, parent)
        if parent_params is None:
            raise AssertionError("best_parent returned row without params")
        parents[current_round] = row_ids(parent)[0]
        for item in cnn.generate_pool(parent_params, parent, seed=20260831 + current_round):
            layout_id = f"tx_band1_mcfil_r{current_round}_cnn{item['seed_rank']:03d}_{item['suffix']}"
            params = cnn.set_tuning(
                base,
                layout_id,
                item["length"],
                item["gap"],
                item["width"],
                {
                    "round": f"round{current_round}",
                    "source": "tools/generate_tx_band1_mcfil_best_layout.py",
                    "feedback_source": str(FEEDBACK),
                    "parent_candidate": row_ids(parent)[0],
                    "strategy": "replayed_cnn_pool_from_feedback_history",
                },
            )
            if cnn.min_gap(params) >= 0.035:
                register(params_by_id, layout_id, params)

    target_params = deepcopy(params_by_id[TARGET])
    target_params["layout_id"] = TARGET
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    params_path = OUT_DIR / f"{TARGET}_params.json"
    params_path.write_text(json.dumps(target_params, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "hfss" / "build_mcfil_dxf_hfss_layout.py"),
            "--params-in",
            str(params_path),
            "--layout-id",
            TARGET,
            "--out-dir",
            str(OUT_DIR),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    report = {
        "target": TARGET,
        "params_json": str(params_path),
        "layout_svg": str(OUT_DIR / f"{TARGET}_review.svg"),
        "parents": parents,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
