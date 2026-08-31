#!/usr/bin/env python3
"""Train a small TX_BAND1 MCFIL CNN ranker and emit next HFSS candidates."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_PARAMS = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil" / "tx_band1_mcfil_r0_params.json"
ITER_ROOT = REPO_ROOT / "projects" / "RFSOC_RF" / "layouts" / "tx_band1_mcfil_iter"
DEFAULT_PARAM_DIRS = (ITER_ROOT / "round1", ITER_ROOT / "round2")
DEFAULT_FEEDBACK = REPO_ROOT / "projects" / "RFSOC_RF" / "hfss_runs" / "tx_band1_mcfil_all_tx_feedback.csv"
DEFAULT_OUT_DIR = ITER_ROOT / "round3"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON must contain an object: {path}")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def candidate_param_path(candidate: str, base_params: Path, params_dirs: list[Path]) -> Path | None:
    if candidate == "tx_band1_mcfil_alumina_manual_ports":
        return base_params
    candidate_names = [
        candidate,
        candidate.removesuffix("_p2up_graphical"),
        candidate.removesuffix("_p2up_hidden_graphical"),
    ]
    candidate_names = list(dict.fromkeys(candidate_names))
    for params_dir in params_dirs:
        for name in candidate_names:
            direct = params_dir / f"{name}_params.json"
            if direct.exists():
                return direct
            seed = params_dir / f"{name}_seed_params.json"
            if seed.exists():
                return seed
    return None


def section_features(params: dict[str, Any]) -> list[list[float]]:
    rows: list[list[float]] = []
    for section in sorted(params["coupled_sections"], key=lambda item: int(item["section"])):
        tuning = section.get("tuning", {})
        length = float(section["length_mm"]) + float(tuning.get("length_delta_mm", 0.0))
        gaps = [float(item) for item in section.get("coupling_gaps_mm", [])]
        gap = (sum(gaps) / len(gaps) if gaps else 0.0) + float(tuning.get("gap_delta_mm", 0.0))
        widths = [float(strip["width_mm"]) for strip in section.get("strips", [])]
        width = (sum(widths) / len(widths) if widths else 0.0) + float(tuning.get("width_delta_mm", 0.0))
        outer = 1.0 if int(section["section"]) in {1, 5} else 0.0
        rows.append([length, gap, width, outer])
    return rows


def tuning_vectors(params: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    length: list[float] = []
    gap: list[float] = []
    width: list[float] = []
    for section in sorted(params["coupled_sections"], key=lambda item: int(item["section"])):
        tuning = section.get("tuning", {})
        length.append(float(tuning.get("length_delta_mm", 0.0)))
        gap.append(float(tuning.get("gap_delta_mm", 0.0)))
        width.append(float(tuning.get("width_delta_mm", 0.0)))
    return length, gap, width


def tuning_signature(params: dict[str, Any], *, ndigits: int = 6) -> tuple[float, ...]:
    length, gap, width = tuning_vectors(params)
    values: list[float] = []
    for triple in zip(length, gap, width, strict=True):
        values.extend(round(float(value), ndigits) for value in triple)
    return tuple(values)


def existing_param_signatures(params_dirs: list[Path]) -> set[tuple[float, ...]]:
    signatures: set[tuple[float, ...]] = set()
    for params_dir in params_dirs:
        if not params_dir.exists():
            continue
        for path in params_dir.glob("*_params.json"):
            try:
                signatures.add(tuning_signature(load_json(path)))
            except Exception:
                continue
    return signatures


def set_tuning(params: dict[str, Any], name: str, length: list[float], gap: list[float], width: list[float], metadata: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(params)
    out["layout_id"] = name
    out["ports"] = {
        "status": "confirmed",
        "p1_source_entity": 2,
        "p2_source_entity": 9,
        "review_note": "Confirmed TX_BAND1 MCFIL ports: P1 on right lower strip, P2 on left upper strip.",
    }
    out["iteration"] = metadata
    for section in out["coupled_sections"]:
        idx = int(section["section"]) - 1
        tuning = section.setdefault("tuning", {})
        tuning["length_delta_mm"] = round(float(length[idx]), 6)
        tuning["gap_delta_mm"] = round(float(gap[idx]), 6)
        tuning["width_delta_mm"] = round(float(width[idx]), 6)
        tuning["x_delta_mm"] = float(tuning.get("x_delta_mm", 0.0))
        tuning["y_delta_mm"] = float(tuning.get("y_delta_mm", 0.0))
    return out


def min_gap(params: dict[str, Any]) -> float:
    values: list[float] = []
    for section in params["coupled_sections"]:
        delta = float(section.get("tuning", {}).get("gap_delta_mm", 0.0))
        values.extend(float(gap) + delta for gap in section.get("coupling_gaps_mm", []))
    return min(values) if values else float("nan")


def build_dataset(feedback: list[dict[str, str]], base_params: Path, params_dirs: list[Path]) -> tuple[list[dict[str, Any]], list[list[list[float]]], list[float]]:
    records: list[dict[str, Any]] = []
    x: list[list[list[float]]] = []
    y: list[float] = []
    seen_signatures: set[tuple[float, ...]] = set()
    for row in feedback:
        path = candidate_param_path(row["candidate"], base_params, params_dirs)
        if path is None:
            continue
        params = load_json(path)
        signature = tuning_signature(params)
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        score = float(row["tx_score"])
        record = dict(row)
        record["params_json"] = str(path)
        record["features"] = section_features(params)
        record["length_delta_mm"], record["gap_delta_mm"], record["width_delta_mm"] = tuning_vectors(params)
        records.append(record)
        x.append(record["features"])
        y.append(score)
    if len(records) < 2:
        raise ValueError("At least two scored candidates are required for CNN ranking")
    return records, x, y


def train_cnn(x: list[list[list[float]]], y: list[float], *, epochs: int, seed: int, checkpoint: Path) -> dict[str, Any]:
    import torch
    from torch import nn

    torch.manual_seed(seed)
    xt = torch.tensor(x, dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.float32).view(-1, 1)
    x_mean = xt.mean(dim=(0, 1), keepdim=True)
    x_std = xt.std(dim=(0, 1), keepdim=True).clamp_min(1e-6)
    y_mean = yt.mean()
    y_std = yt.std().clamp_min(1.0)
    xn = (xt - x_mean) / x_std
    yn = (yt - y_mean) / y_std

    class TxBandMcfilSectionCnn(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(4, 16, kernel_size=3, padding=1),
                nn.GELU(),
                nn.Conv1d(16, 16, kernel_size=3, padding=1),
                nn.GELU(),
                nn.AdaptiveAvgPool1d(1),
                nn.Flatten(),
                nn.Linear(16, 16),
                nn.GELU(),
                nn.Linear(16, 1),
            )

        def forward(self, value: Any) -> Any:
            return self.net(value.transpose(1, 2))

    model = TxBandMcfilSectionCnn()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.03, weight_decay=0.01)
    best_loss = float("inf")
    best_state = None
    for _ in range(epochs):
        optimizer.zero_grad()
        pred = model(xn)
        loss = torch.nn.functional.mse_loss(pred, yn)
        loss.backward()
        optimizer.step()
        if float(loss) < best_loss:
            best_loss = float(loss)
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if best_state:
        model.load_state_dict(best_state)
    with torch.no_grad():
        pred_score = (model(xn) * y_std + y_mean).view(-1).detach().cpu().tolist()
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": "TxBandMcfilSectionCnn",
            "model_state": model.state_dict(),
            "x_mean": x_mean,
            "x_std": x_std,
            "y_mean": y_mean,
            "y_std": y_std,
            "features": "5 sections x [length, gap, mean_width, outer_flag]",
            "epochs": epochs,
            "seed": seed,
            "train_loss": best_loss,
        },
        checkpoint,
    )
    return {"train_loss": best_loss, "train_pred_score": pred_score, "checkpoint": str(checkpoint)}


def predict_scores(checkpoint: Path, x: list[list[list[float]]]) -> list[float]:
    import torch
    from torch import nn

    class TxBandMcfilSectionCnn(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(4, 16, kernel_size=3, padding=1),
                nn.GELU(),
                nn.Conv1d(16, 16, kernel_size=3, padding=1),
                nn.GELU(),
                nn.AdaptiveAvgPool1d(1),
                nn.Flatten(),
                nn.Linear(16, 16),
                nn.GELU(),
                nn.Linear(16, 1),
            )

        def forward(self, value: Any) -> Any:
            return self.net(value.transpose(1, 2))

    ckpt = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = TxBandMcfilSectionCnn()
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    xt = torch.tensor(x, dtype=torch.float32)
    xn = (xt - ckpt["x_mean"]) / ckpt["x_std"]
    with torch.no_grad():
        pred = model(xn) * ckpt["y_std"] + ckpt["y_mean"]
    return pred.view(-1).detach().cpu().tolist()


def generate_pool(best_params: dict[str, Any], best_row: dict[str, Any], *, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    best_l, best_g, best_w = tuning_vectors(best_params)
    peak = float(best_row["peak_freq_ghz"])
    lo = float(best_row["lo_stopband_max_s21_db"])
    high_s11 = float(best_row.get("worst_s11_high_passband_db", best_row.get("worst_s11_passband_db", "-10")))
    high_s22 = float(best_row.get("worst_s22_high_passband_db", best_row.get("worst_s22_passband_db", "-10")))
    length_bias = 0.004 if peak > 18.75 else 0.0
    gap_relax = 0.004 if lo > -40.0 else 0.0
    high_rl_bad = max(high_s11, high_s22) > -10.0

    pool: list[dict[str, Any]] = []
    anchors = [
        ("match_width_m006", 0.000, [0.002, 0.004, 0.006, 0.004, 0.002], [-0.006, -0.003, 0.0, -0.003, -0.006]),
        ("match_width_m010", 0.000, [0.002, 0.004, 0.006, 0.004, 0.002], [-0.010, -0.004, 0.0, -0.004, -0.010]),
        ("outer_gap_stronger_width_m006", 0.000, [-0.004, 0.004, 0.006, 0.004, -0.004], [-0.006, -0.003, 0.0, -0.003, -0.006]),
        ("center_gap_relax_keep_len", 0.000, [0.000, 0.004, 0.008, 0.004, 0.000], [0, 0, 0, 0, 0]),
        ("taper_len_match", 0.000, [0.000, 0.004, 0.006, 0.004, 0.000], [-0.006, -0.002, 0.0, -0.002, -0.006]),
        ("edge_short_center_hold", 0.000, [0.000, 0.004, 0.006, 0.004, 0.000], [-0.008, -0.002, 0.0, -0.002, -0.008]),
    ]
    if high_rl_bad:
        anchors.extend(
            [
                ("hf_edge_match_gap_relax", 0.000, [0.010, 0.006, 0.004, 0.006, 0.010], [-0.004, -0.002, 0.0, -0.002, -0.004]),
                ("hf_edge_match_width_m014", 0.000, [0.006, 0.004, 0.004, 0.004, 0.006], [-0.014, -0.006, -0.002, -0.006, -0.014]),
                ("hf_edge_outer_short_gap_relax", 0.000, [0.012, 0.004, 0.004, 0.004, 0.012], [-0.010, -0.004, 0.0, -0.004, -0.010]),
            ]
        )
    for index, (suffix, l_add, g_add, w_add) in enumerate(anchors, start=1):
        length = [value + l_add + length_bias for value in best_l]
        if suffix == "taper_len_match":
            length = [best_l[0] - 0.006, best_l[1] + 0.004, best_l[2] + 0.010, best_l[3] + 0.004, best_l[4] - 0.006]
        if suffix == "edge_short_center_hold":
            length = [best_l[0] - 0.012, best_l[1] + 0.000, best_l[2] + 0.006, best_l[3] + 0.000, best_l[4] - 0.012]
        gap = [g + add + gap_relax for g, add in zip(best_g, g_add, strict=True)]
        width = [w + add for w, add in zip(best_w, w_add, strict=True)]
        pool.append({"seed_rank": index, "suffix": suffix, "length": length, "gap": gap, "width": width})

    for index in range(40):
        length = [
            best_l[0] + rng.uniform(-0.014, 0.006),
            best_l[1] + rng.uniform(-0.004, 0.012),
            best_l[2] + rng.uniform(0.000, 0.016),
            best_l[3] + rng.uniform(-0.004, 0.012),
            best_l[4] + rng.uniform(-0.014, 0.006),
        ]
        # Keep the model near CNN002; recover LO with central gap relaxation while probing outer coupling.
        gap = [best_g[i] + gap_relax + rng.uniform(-0.006, 0.010) for i in range(5)]
        if high_rl_bad:
            gap[0] += rng.uniform(0.002, 0.012)
            gap[4] += rng.uniform(0.002, 0.012)
        width = [
            best_w[0] + rng.uniform(-0.012, 0.000),
            best_w[1] + rng.uniform(-0.005, 0.002),
            best_w[2] + rng.uniform(-0.003, 0.003),
            best_w[3] + rng.uniform(-0.005, 0.002),
            best_w[4] + rng.uniform(-0.012, 0.000),
        ]
        if high_rl_bad:
            width[0] += rng.uniform(-0.006, 0.002)
            width[4] += rng.uniform(-0.006, 0.002)
        pool.append({"seed_rank": len(pool) + 1, "suffix": f"rand{index + 1:02d}", "length": length, "gap": gap, "width": width})
    return pool


def build_layout(params_path: Path, out_dir: Path, layout_id: str) -> None:
    script = REPO_ROOT / "tools" / "hfss" / "build_mcfil_dxf_hfss_layout.py"
    subprocess.run([sys.executable, str(script), "--params-in", str(params_path), "--layout-id", layout_id, "--out-dir", str(out_dir)], cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train/rank TX_BAND1 MCFIL CNN candidates.")
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--base-params", type=Path, default=BASE_PARAMS)
    parser.add_argument("--params-dir", type=Path, action="append", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--round-id", default="round3")
    parser.add_argument("--epochs", type=int, default=1600)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--build-top-k", type=int, default=4)
    args = parser.parse_args()

    feedback = read_csv(args.feedback)
    params_dirs = args.params_dir or list(DEFAULT_PARAM_DIRS)
    records, x_train, y_train = build_dataset(feedback, args.base_params, params_dirs)
    best = max(records, key=lambda row: float(row["tx_score"]))
    best_params = load_json(Path(best["params_json"]))
    scored_signatures = existing_param_signatures(params_dirs)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = args.out_dir / "tx_band1_mcfil_section_cnn.pt"
    train = train_cnn(x_train, y_train, epochs=args.epochs, seed=args.seed, checkpoint=checkpoint)

    pool = generate_pool(best_params, best, seed=args.seed)
    base_params = load_json(args.base_params)
    candidate_params: list[dict[str, Any]] = []
    pool_features: list[list[list[float]]] = []
    for item in pool:
        name = f"tx_band1_mcfil_{args.round_id.replace('round', 'r')}_cnn{item['seed_rank']:03d}_{item['suffix']}"
        params = set_tuning(
            base_params,
            name,
            item["length"],
            item["gap"],
            item["width"],
            {
                "round": args.round_id,
                "source": "tools/make_tx_band_mcfil_cnn_iteration.py",
                "feedback_source": str(args.feedback),
                "parent_candidate": best["candidate"],
                "strategy": "cnn_ranked_match_and_nonuniform_length_feedback",
            },
        )
        mg = min_gap(params)
        if not math.isfinite(mg) or mg < 0.035:
            continue
        if tuning_signature(params) in scored_signatures:
            continue
        candidate_params.append(params)
        pool_features.append(section_features(params))
    if not candidate_params:
        raise ValueError("No non-duplicate candidates remained after filtering scored tuning vectors")

    predictions = predict_scores(checkpoint, pool_features)
    rows: list[dict[str, Any]] = []
    for params, pred in zip(candidate_params, predictions, strict=True):
        length, gap, width = tuning_vectors(params)
        rows.append(
            {
                "candidate": params["layout_id"],
                "predicted_tx_score": f"{pred:.3f}",
                "parent": best["candidate"],
                "parent_tx_score": best["tx_score"],
                "min_gap_mm": f"{min_gap(params):.6g}",
                "length_delta_mm": ";".join(f"{value:.6g}" for value in length),
                "gap_delta_mm": ";".join(f"{value:.6g}" for value in gap),
                "width_delta_mm": ";".join(f"{value:.6g}" for value in width),
                "params_json": str(args.out_dir / f"{params['layout_id']}_params.json"),
                "layout_json": str(args.out_dir / f"{params['layout_id']}_layout.json"),
            }
        )
    rows.sort(key=lambda row: float(row["predicted_tx_score"]), reverse=True)
    selected = rows[: args.top_k]
    selected_names = {row["candidate"] for row in rows[: args.build_top_k]}
    params_by_name = {params["layout_id"]: params for params in candidate_params}
    for row in selected:
        params = params_by_name[row["candidate"]]
        params_path = args.out_dir / f"{params['layout_id']}_params.json"
        params_path.write_text(json.dumps(params, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if params["layout_id"] in selected_names:
            build_layout(params_path, args.out_dir, params["layout_id"])
    plan_path = args.out_dir / f"tx_band1_mcfil_{args.round_id}_cnn_candidate_plan.csv"
    write_csv(plan_path, selected)
    report = {
        "status": "ok",
        "model": "TxBandMcfilSectionCnn",
        "training_samples": len(records),
        "params_dirs": [str(path) for path in params_dirs],
        "best_parent": best["candidate"],
        "best_parent_score": best["tx_score"],
        "train": train,
        "candidate_plan": str(plan_path),
        "built_layouts": sorted(selected_names),
    }
    (args.out_dir / f"tx_band1_mcfil_{args.round_id}_cnn_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
