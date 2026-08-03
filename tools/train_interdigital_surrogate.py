#!/usr/bin/env python3
"""Train the refined-parameter interdigital S-parameter surrogate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random
import sys

import numpy as np

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.nn.interdigital_features import AUX_FEATURES, curve_aux_features, interdigital_score
from simads.nn.interdigital_surrogate import InterdigitalSParamSurrogate, require_torch


def repo_root() -> Path:
    return _SIM_ROOT


def split_indices(n: int, val_fraction: float, seed: int) -> tuple[list[int], list[int]]:
    indices = list(range(n))
    random.Random(seed).shuffle(indices)
    if n < 4 or val_fraction <= 0.0:
        return indices, indices
    val_n = max(1, int(round(n * val_fraction)))
    return indices[val_n:], indices[:val_n]


def mean_std_masked(y: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.zeros(y.shape[1:], dtype=np.float32)
    std = np.ones(y.shape[1:], dtype=np.float32)
    for index in np.ndindex(y.shape[1:]):
        values = y[(slice(None), *index)][valid[(slice(None), *index)]]
        values = values[np.isfinite(values)]
        if values.size:
            mean[index] = float(np.mean(values))
            sigma = float(np.std(values))
            std[index] = sigma if sigma > 1e-6 else 1.0
    return mean, std


def normalize_aux(y_aux: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    finite = np.isfinite(y_aux)
    filled = np.nan_to_num(y_aux, nan=0.0).astype(np.float32)
    mean = np.zeros(y_aux.shape[1], dtype=np.float32)
    std = np.ones(y_aux.shape[1], dtype=np.float32)
    for col in range(y_aux.shape[1]):
        values = y_aux[:, col][finite[:, col]]
        if values.size:
            mean[col] = float(np.mean(values))
            sigma = float(np.std(values))
            std[col] = sigma if sigma > 1e-6 else 1.0
    return ((filled - mean) / std).astype(np.float32), finite, mean, std


def masked_weighted_mse(pred: "torch.Tensor", target: "torch.Tensor", valid: "torch.Tensor", weights: "torch.Tensor") -> "torch.Tensor":
    torch = require_torch()
    mask = valid.to(dtype=pred.dtype)
    weighted = (pred - target) ** 2 * mask * weights
    denom = torch.clamp((mask * weights).sum(), min=1.0)
    return weighted.sum() / denom


def masked_aux_mse(pred: "torch.Tensor", target: "torch.Tensor", valid: "torch.Tensor") -> "torch.Tensor":
    torch = require_torch()
    mask = valid.to(dtype=pred.dtype)
    denom = torch.clamp(mask.sum(), min=1.0)
    return (((pred - target) ** 2) * mask).sum() / denom


def branch_inputs(data: np.lib.npyio.NpzFile, indices: list[int] | None = None) -> dict[str, np.ndarray]:
    key_map = {
        "x_resonator": "x_resonator_norm",
        "x_gap": "x_gap_norm",
        "x_feed": "x_feed_norm",
        "x_derived": "x_derived_norm",
    }
    out: dict[str, np.ndarray] = {}
    for out_key, data_key in key_map.items():
        values = data[data_key].astype(np.float32)
        out[out_key] = values if indices is None else values[indices]
    return out


def model_kwargs(inputs: dict[str, "torch.Tensor"]) -> dict[str, "torch.Tensor"]:
    return {
        "x_resonator": inputs["x_resonator"],
        "x_gap": inputs["x_gap"],
        "x_feed": inputs["x_feed"],
        "x_derived": inputs["x_derived"],
    }


def write_predictions(path: Path, names: np.ndarray, freq_ghz: np.ndarray, pred_db: np.ndarray) -> None:
    rows: list[dict[str, str]] = []
    for idx, name in enumerate(names):
        aux = curve_aux_features(freq_ghz, pred_db[idx])
        metrics = {feature: float(aux[col]) for col, feature in enumerate(AUX_FEATURES)}
        row = {
            "candidate": str(name),
            "pred_score": f"{interdigital_score(metrics):.6g}",
            **{f"pred_{key}": f"{value:.6g}" for key, value in metrics.items()},
        }
        for port_idx, port in enumerate(("s11", "s21", "s22")):
            for freq_idx, freq in enumerate(freq_ghz):
                label = f"pred_{port}_{float(freq):.2f}g_db".replace(".", "p")
                row[label] = f"{float(pred_db[idx, port_idx, freq_idx]):.6g}"
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Train refined-parameter interdigital S-parameter surrogate.")
    parser.add_argument("--dataset", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_refined_nn_dataset.npz")
    parser.add_argument("--out", type=Path, default=root / "projects" / "bfp_6_8g_i7_fr4" / "results" / "interdigital_refined_surrogate.pt")
    parser.add_argument("--predictions-out", type=Path, default=None)
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--aux-loss-weight", type=float, default=0.15)
    parser.add_argument("--s11-loss-weight", type=float, default=0.25)
    parser.add_argument("--s21-loss-weight", type=float, default=1.0)
    parser.add_argument("--s22-loss-weight", type=float, default=0.25)
    return parser.parse_args()


def main() -> None:
    torch = require_torch()
    args = parse_args()
    data = np.load(args.dataset, allow_pickle=True)
    metadata = json.loads(str(data["metadata_json"]))
    freq_ghz = data["freq_ghz"].astype(np.float32)
    names = data["candidate_names"]
    y_db = data["y_s_db"].astype(np.float32)
    valid = data["valid_s_mask"].astype(bool)
    y_mean, y_std = mean_std_masked(y_db, valid)
    y_norm = np.nan_to_num((y_db - y_mean) / y_std, nan=0.0).astype(np.float32)
    y_aux_norm, y_aux_valid, y_aux_mean, y_aux_std = normalize_aux(data["y_aux"].astype(np.float32))

    torch.manual_seed(args.seed)
    train_idx, val_idx = split_indices(y_db.shape[0], args.val_fraction, args.seed)
    inputs_np = branch_inputs(data)
    inputs = {key: torch.tensor(value, dtype=torch.float32) for key, value in inputs_np.items()}
    y_tensor = torch.tensor(y_norm, dtype=torch.float32)
    valid_tensor = torch.tensor(valid, dtype=torch.bool)
    aux_tensor = torch.tensor(y_aux_norm, dtype=torch.float32)
    aux_valid_tensor = torch.tensor(y_aux_valid, dtype=torch.bool)

    model = InterdigitalSParamSurrogate(
        input_features=int(data["x_raw"].shape[1]),
        resonator_features=int(data["x_resonator_norm"].shape[1]),
        gap_features=int(data["x_gap_norm"].shape[1]),
        feed_features=int(data["x_feed_norm"].shape[1]),
        derived_features=int(data["x_derived_norm"].shape[1]),
        num_freqs=int(y_db.shape[-1]),
        num_sparams=3,
        hidden=args.hidden,
        blocks=args.blocks,
        aux_features=int(y_aux_norm.shape[1]),
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    weights = torch.tensor([args.s11_loss_weight, args.s21_loss_weight, args.s22_loss_weight], dtype=torch.float32).view(3, 1)

    best_state = None
    best_val = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        train_inputs = {key: value[train_idx] for key, value in inputs.items()}
        pred, aux_pred = model.forward_with_aux(**model_kwargs(train_inputs))
        curve_loss = masked_weighted_mse(pred, y_tensor[train_idx], valid_tensor[train_idx], weights)
        aux_loss = masked_aux_mse(aux_pred, aux_tensor[train_idx], aux_valid_tensor[train_idx])
        loss = curve_loss + args.aux_loss_weight * aux_loss
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_inputs = {key: value[val_idx] for key, value in inputs.items()}
            val_pred, val_aux_pred = model.forward_with_aux(**model_kwargs(val_inputs))
            val_curve = masked_weighted_mse(val_pred, y_tensor[val_idx], valid_tensor[val_idx], weights)
            val_aux = masked_aux_mse(val_aux_pred, aux_tensor[val_idx], aux_valid_tensor[val_idx])
            val_loss = val_curve + args.aux_loss_weight * val_aux
        if float(val_loss) < best_val:
            best_val = float(val_loss)
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        if epoch == 1 or epoch % 50 == 0 or epoch == args.epochs:
            print(
                f"epoch={epoch:04d} train_loss={float(loss.detach()):.6g} "
                f"curve={float(curve_loss.detach()):.6g} aux={float(aux_loss.detach()):.6g} "
                f"val={float(val_loss):.6g}"
            )

    if best_state is not None:
        model.load_state_dict(best_state)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state": model.state_dict(),
        "model_config": {
            "input_features": int(data["x_raw"].shape[1]),
            "resonator_features": int(data["x_resonator_norm"].shape[1]),
            "gap_features": int(data["x_gap_norm"].shape[1]),
            "feed_features": int(data["x_feed_norm"].shape[1]),
            "derived_features": int(data["x_derived_norm"].shape[1]),
            "num_freqs": int(y_db.shape[-1]),
            "num_sparams": 3,
            "hidden": args.hidden,
            "blocks": args.blocks,
            "aux_features": int(y_aux_norm.shape[1]),
        },
        "freq_ghz": freq_ghz.tolist(),
        "dataset": str(args.dataset),
        "dataset_metadata": metadata,
        "best_val_loss": best_val,
        "y_mean": y_mean,
        "y_std": y_std,
        "y_aux_mean": y_aux_mean,
        "y_aux_std": y_aux_std,
        "normalization": {
            key: {"mean": data[f"{key}_mean"], "std": data[f"{key}_std"]}
            for key in ("x_resonator", "x_gap", "x_feed", "x_derived", "x_raw", "x_sym", "x_delta")
            if f"{key}_mean" in data.files
        },
        "loss_config": {
            "sparam_loss_weights": {"s11": args.s11_loss_weight, "s21": args.s21_loss_weight, "s22": args.s22_loss_weight},
            "aux_loss_weight": args.aux_loss_weight,
            "aux_features": AUX_FEATURES,
        },
    }
    torch.save(checkpoint, args.out)
    print(f"Wrote model checkpoint: {args.out}")

    model.eval()
    with torch.no_grad():
        pred_norm = model(**model_kwargs(inputs)).detach().cpu().numpy()
    pred_db = pred_norm * y_std + y_mean
    pred_out = args.predictions_out or args.out.with_suffix(".predictions.csv")
    write_predictions(pred_out, names, freq_ghz, pred_db)
    print(f"Wrote surrogate predictions: {pred_out}")


if __name__ == "__main__":
    main()

