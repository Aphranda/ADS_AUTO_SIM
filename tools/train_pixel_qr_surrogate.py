#!/usr/bin/env python3
"""Train a small CNN surrogate for pixel QR S-parameter prediction.

S21 is the primary feedback target. S11/S22 are trained with lower curve-loss
weights so the model carries reflection context without letting return loss
dominate candidate ranking.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random
import sys

import numpy as np

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from simads.nn import (
    PixelQrS21Surrogate,
    bandpass_frequency_weights,
    masked_aux_mse,
    masked_weighted_mse,
    require_torch,
    s21_aux_feature_tensor,
    s21_bandpass_features,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def split_indices(n: int, val_fraction: float, seed: int) -> tuple[list[int], list[int]]:
    indices = list(range(n))
    random.Random(seed).shuffle(indices)
    if n < 4 or val_fraction <= 0.0:
        return indices, indices
    val_n = max(1, int(round(n * val_fraction)))
    return indices[val_n:], indices[:val_n]


def s21_view(curves: "torch.Tensor") -> "torch.Tensor":
    if curves.ndim == 3:
        return curves[:, 1, :]
    return curves


def write_predictions(path: Path, names: np.ndarray, freq_ghz: np.ndarray, pred: np.ndarray) -> None:
    pred_s21 = pred[:, 1, :] if pred.ndim == 3 else pred
    rows: list[dict[str, str]] = []
    for idx, name in enumerate(names):
        features = s21_bandpass_features(freq_ghz.tolist(), pred_s21[idx].tolist())
        row = {
            "candidate": str(name),
            "passband_min_s21_db": f"{features.passband_min_db:.6g}",
            "passband_avg_s21_db": f"{features.passband_avg_db:.6g}",
            "passband_ripple_db": f"{features.passband_ripple_db:.6g}",
            "s21_5g_db": f"{features.s21_5g_db:.6g}",
            "low_stop_max_s21_db": f"{features.low_stop_max_db:.6g}",
            "high_stop_max_s21_db": f"{features.high_stop_max_db:.6g}",
            "bandpass_score_s21": f"{features.bandpass_score:.6g}",
        }
        for freq_idx, freq in enumerate(freq_ghz):
            label = f"s21_{float(freq):.2f}g_db".replace(".", "p")
            row[label] = f"{float(pred_s21[idx, freq_idx]):.6g}"
            if pred.ndim == 3:
                row[f"s11_{float(freq):.2f}g_db".replace(".", "p")] = f"{float(pred[idx, 0, freq_idx]):.6g}"
                row[f"s22_{float(freq):.2f}g_db".replace(".", "p")] = f"{float(pred[idx, 2, freq_idx]):.6g}"
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train pixel QR S21 CNN surrogate.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=repo_root() / "projects" / "pixel_qr_bpf_fr4_210um" / "results" / "pixel_qr_s21_nn_dataset.npz",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=repo_root() / "projects" / "pixel_qr_bpf_fr4_210um" / "results" / "pixel_qr_s21_surrogate.pt",
    )
    parser.add_argument("--predictions-out", type=Path, default=None)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=96)
    parser.add_argument(
        "--aux-loss-weight",
        type=float,
        default=0.2,
        help="Weight for the auxiliary feature head loss. Set 0 to disable.",
    )
    parser.add_argument(
        "--curve-feature-loss-weight",
        type=float,
        default=0.1,
        help="Weight for feature loss computed from the predicted S21 curve.",
    )
    parser.add_argument("--s11-loss-weight", type=float, default=0.1)
    parser.add_argument("--s21-loss-weight", type=float, default=1.0)
    parser.add_argument("--s22-loss-weight", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    torch = require_torch()
    args = parse_args()
    data = np.load(args.dataset, allow_pickle=True)
    x = torch.tensor(data["x_mask"], dtype=torch.float32)
    geom = torch.tensor(data["x_geom"], dtype=torch.float32) if "x_geom" in data.files else None
    if "y_s_db" in data.files:
        y = torch.tensor(np.nan_to_num(data["y_s_db"], nan=0.0), dtype=torch.float32)
        valid = torch.tensor(data["valid_s_mask"] if "valid_s_mask" in data.files else data["valid_freq_mask"], dtype=torch.bool)
        y_s21 = y[:, 1, :]
        valid_s21 = valid[:, 1, :]
        num_sparams = int(y.shape[1])
        sparam_names = [str(value) for value in json.loads(str(data["metadata_json"])).get("sparam_names", ["s11", "s21", "s22"])]
    else:
        y = torch.tensor(np.nan_to_num(data["y_s21_db"], nan=0.0), dtype=torch.float32)
        valid = torch.tensor(data["valid_freq_mask"], dtype=torch.bool)
        y_s21 = y
        valid_s21 = valid
        num_sparams = 1
        sparam_names = ["s21"]
    freq_ghz = data["freq_ghz"].astype(np.float32)
    names = data["candidate_names"]
    metadata = json.loads(str(data["metadata_json"]))

    torch.manual_seed(args.seed)
    train_idx, val_idx = split_indices(x.shape[0], args.val_fraction, args.seed)
    model = PixelQrS21Surrogate(
        matrix_n=int(x.shape[-1]),
        num_freqs=int(y.shape[-1]),
        num_sparams=num_sparams,
        channels=args.channels,
        hidden=args.hidden,
        coord_channels=True,
        mask_channels=int(x.shape[1]),
        geom_features=0 if geom is None else int(geom.shape[1]),
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    freq_weights_1d = torch.tensor(bandpass_frequency_weights(freq_ghz.tolist()), dtype=torch.float32)
    if num_sparams == 3:
        sparam_weights = torch.tensor(
            [args.s11_loss_weight, args.s21_loss_weight, args.s22_loss_weight],
            dtype=torch.float32,
        )
        curve_weights = sparam_weights.view(-1, 1) * freq_weights_1d.view(1, -1)
    else:
        sparam_weights = torch.tensor([args.s21_loss_weight], dtype=torch.float32)
        curve_weights = freq_weights_1d * args.s21_loss_weight
    freq_tensor = torch.tensor(freq_ghz, dtype=torch.float32)
    aux_target, aux_valid = s21_aux_feature_tensor(y_s21, valid_s21, freq_tensor)

    best_state = None
    best_val = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        train_geom = None if geom is None else geom[train_idx]
        pred, aux_pred = model.forward_with_aux(x[train_idx], train_geom)
        pred_s21 = s21_view(pred)
        curve_loss = masked_weighted_mse(pred, y[train_idx], valid[train_idx], curve_weights)
        aux_loss = masked_aux_mse(aux_pred, aux_target[train_idx], aux_valid[train_idx])
        pred_features, pred_features_valid = s21_aux_feature_tensor(pred_s21, valid_s21[train_idx], freq_tensor)
        feature_loss = masked_aux_mse(
            pred_features,
            aux_target[train_idx],
            aux_valid[train_idx] & pred_features_valid,
        )
        loss = curve_loss + args.aux_loss_weight * aux_loss + args.curve_feature_loss_weight * feature_loss
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_geom = None if geom is None else geom[val_idx]
            val_pred, val_aux_pred = model.forward_with_aux(x[val_idx], val_geom)
            val_pred_s21 = s21_view(val_pred)
            val_curve_loss = masked_weighted_mse(val_pred, y[val_idx], valid[val_idx], curve_weights)
            val_aux_loss = masked_aux_mse(val_aux_pred, aux_target[val_idx], aux_valid[val_idx])
            val_pred_features, val_pred_features_valid = s21_aux_feature_tensor(val_pred_s21, valid_s21[val_idx], freq_tensor)
            val_feature_loss = masked_aux_mse(
                val_pred_features,
                aux_target[val_idx],
                aux_valid[val_idx] & val_pred_features_valid,
            )
            val_loss = (
                val_curve_loss
                + args.aux_loss_weight * val_aux_loss
                + args.curve_feature_loss_weight * val_feature_loss
            )
        if float(val_loss) < best_val:
            best_val = float(val_loss)
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        if epoch == 1 or epoch % 50 == 0 or epoch == args.epochs:
            print(
                f"epoch={epoch:04d} train_loss={float(loss.detach()):.6g} "
                f"curve={float(curve_loss.detach()):.6g} aux={float(aux_loss.detach()):.6g} "
                f"feat={float(feature_loss.detach()):.6g} val_loss={float(val_loss):.6g}"
            )

    if best_state is not None:
        model.load_state_dict(best_state)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "model_config": {
                "matrix_n": int(x.shape[-1]),
                "num_freqs": int(y.shape[-1]),
                "num_sparams": num_sparams,
                "channels": args.channels,
                "hidden": args.hidden,
                "coord_channels": True,
                "mask_channels": int(x.shape[1]),
                "geom_features": 0 if geom is None else int(geom.shape[1]),
                "aux_features": int(aux_target.shape[1]),
            },
            "freq_ghz": freq_ghz.tolist(),
            "dataset": str(args.dataset),
            "dataset_metadata": metadata,
            "best_val_loss": best_val,
            "loss_config": {
                "curve": "masked weighted MSE on S-parameter dB curves; S21 primary, S11/S22 low-weight auxiliary",
                "sparam_names": sparam_names,
                "sparam_loss_weights": {
                    "s11": args.s11_loss_weight if num_sparams == 3 else 0.0,
                    "s21": args.s21_loss_weight,
                    "s22": args.s22_loss_weight if num_sparams == 3 else 0.0,
                },
                "aux_features": "passband_min,ripple,s21_5g,s21_6g,s21_8g,s21_9g,high_stop_max",
                "aux_loss_weight": args.aux_loss_weight,
                "curve_feature_loss_weight": args.curve_feature_loss_weight,
            },
        },
        args.out,
    )
    print(f"Wrote model checkpoint: {args.out}")

    model.eval()
    with torch.no_grad():
        pred_all = model(x, geom).detach().cpu().numpy()
    pred_out = args.predictions_out or args.out.with_suffix(".predictions.csv")
    write_predictions(pred_out, names, freq_ghz, pred_all)
    print(f"Wrote surrogate predictions: {pred_out}")


if __name__ == "__main__":
    main()
