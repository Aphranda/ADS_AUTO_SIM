#!/usr/bin/env python3
"""Plot SVG charts for the SP10T switch measured S2P data (HMC7992 x3 = SP10T).

Reads the measured Touchstone files in docs/test/SP10T_S2P (1.s2p..10.s2p,
file number == RF port number) and writes report-style SVG charts:

- sp10t_measured_s21_overlay_all.svg   : S21 of all 10 states, colored by group
- sp10t_measured_rl_group_overlay.svg  : S11/S22 of group representatives
- sp10t_measured_group_avg_s21.svg     : group-average S21
- sp10t_measured_il_6g_vs_8g.svg       : S21 @ 6 GHz vs 8 GHz grouped bars
- sp10t_measured_metrics.json          : per-state evaluation metrics (0.5-8 GHz)
- sp10t_measured_isolation_typical.svg : conservative isolation of RF7-RF8 / RF9-RF10
- sp10t_measured_isolation_metrics.json: two representative isolation-pair metrics

Grouping (derived from measured insertion loss / delay):
  group C (direct, 1 switch) : RF9, RF10
  group B (2 switches, short): RF2, RF3, RF6, RF7
  group A (2 switches, long) : RF1, RF4, RF5, RF8
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from simads.scoring.connector import read_s2p  # noqa: E402

GROUP_C = [9, 10]
GROUP_B = [2, 3, 6, 7]
GROUP_A = [1, 4, 5, 8]
ISOLATION_PAIRS = {"RF7-RF8": "78.s2p", "RF9-RF10": "910.s2p"}
ISOLATION_TOPOLOGY = {"RF7-RF8": "two-stage", "RF9-RF10": "one-stage"}
GROUP_COLOR = {  # green=direct, orange=two-stage short, red=two-stage long
    "C": "#2e7d32",
    "B": "#d97706",
    "A": "#b42318",
}
F_6G = 6.0
F_8G = 8.0

# HMC7992 datasheet (Rev. A): insertion loss typ per switch, dB (0.1-2 / 2-4 / 4-6 GHz)
DATASHEET_IL_SINGLE = [(0.1, 0.6), (2.0, 0.6), (2.0, 0.7), (4.0, 0.7), (4.0, 1.0), (6.0, 1.0)]
DATASHEET_FIG_8G_IL_RANGE = (1.1, 1.7)  # Figures 7/10, approximate range across VDD and temperature
CONNECTOR_S2P = REPO_ROOT / "projects" / "hfss_sma_connector" / "simulations" / "single_end_connector_50r_30mm" / "results" / "l40w17" / "l40w17.s2p"


def fr4_trace_loss_db_per_100mm(freq_ghz: float, tand: float = 0.02) -> float:
    """50-ohm microstrip on FR4: dielectric + conductor + roughness loss per 100 mm.

    Assumptions: eps_r=4.4, h=0.8 mm, 1 oz (35 um) copper, sigma=5.8e7 S/m,
    Ra=2 um surface roughness. Width solved for Z0=50 ohm (w ~ 1.54 mm).
    """
    eps_r, h, t, sigma, ra = 4.4, 0.8e-3, 35e-6, 5.8e7, 2.0e-6
    mu0, c = 4 * math.pi * 1e-7, 2.99792458e8
    f = freq_ghz * 1e9

    def z0_eps(w: float) -> tuple[float, float]:
        u = w / h
        if u <= 1:
            ee = (eps_r + 1) / 2 + (eps_r - 1) / 2 * ((1 + 12 / u) ** -0.5 + 0.04 * (1 - u) ** 2)
            z0 = 60 / math.sqrt(ee) * math.log(8 / u + u / 4)
        else:
            ee = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 / u) ** -0.5
            z0 = 120 * math.pi / (math.sqrt(ee) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
        return z0, ee

    w = 1e-3
    for _ in range(200):
        z0, ee = z0_eps(w)
        w *= (z0 / 50.0) ** 0.5
    z0, ee = z0_eps(w)

    l0 = c / f
    ad = 27.3 * (eps_r / (eps_r - 1)) * ((ee - 1) / math.sqrt(ee)) * tand / l0  # dB/m
    delta = 1 / math.sqrt(math.pi * f * mu0 * sigma)  # skin depth, m
    rs = 1 / (sigma * delta)
    ac = 8.686 * rs / (z0 * w)  # dB/m, wide-trace approximation
    ksr = 1 + (2 / math.pi) * math.atan(1.4 * (ra / delta) ** 2)
    ar = ac * (ksr - 1)  # roughness increment, dB/m
    return (ad + ac + ar) * 0.1  # dB per 100 mm


def load_s2p(path: Path) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    samples = read_s2p(path)
    freq = np.array([float(row["freq_ghz"]) for row in samples])
    traces = {
        name: np.array([20.0 * np.log10(max(abs(complex(row[name])), 1e-30)) for row in samples])
        for name in ("s11", "s21", "s12", "s22")
    }
    return freq, traces


def group_of(rf: int) -> str:
    if rf in GROUP_C:
        return "C"
    if rf in GROUP_B:
        return "B"
    if rf in GROUP_A:
        return "A"
    raise ValueError(rf)


def decorate(ax, title: str, refs: tuple[float, ...] = (-3.0, -6.0, -10.0), y_max: float = 0.0) -> None:
    for ref in refs:
        ax.axhline(ref, color="#8a8f98", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.axvline(F_6G, color="#1f3864", alpha=0.55, linewidth=0.9, linestyle="--")
    ax.axvline(F_8G, color="#b42318", alpha=0.65, linewidth=1.0, linestyle="--")
    ax.text(F_6G, y_max - 0.9, "6 GHz", fontsize=7, color="#1f3864", ha="center")
    ax.text(F_8G, y_max - 0.9, "8 GHz", fontsize=7, color="#b42318", ha="center")
    ax.set_title(title)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(0.0, 10.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)


def metrics_for(freq: np.ndarray, traces: dict[str, np.ndarray], band: tuple[float, float]) -> dict:
    m = (freq >= band[0]) & (freq <= band[1])
    out: dict = {}
    for name in ("s11", "s21", "s22"):
        seg = traces[name][m]
        out[f"{name}_worst"] = float(np.max(seg))
        out[f"{name}_worst_f"] = float(freq[m][int(np.argmax(seg))])
        if name == "s21":
            out["s21_avg"] = float(np.mean(seg))
    for fq, key in ((6.0, "at_6g"), (8.0, "at_8g")):
        for name in ("s11", "s21", "s22"):
            idx = int(np.argmin(np.abs(freq - fq)))
            out[f"{name}_{key}"] = float(traces[name][idx])
    out["rl_worst"] = float(np.max(np.maximum(traces["s11"][m], traces["s22"][m])))
    out["rl_worst_f"] = float(freq[m][int(np.argmax(np.maximum(traces["s11"][m], traces["s22"][m])))])
    return out


def plot_s21_overlay(freqs: dict[int, np.ndarray], s21s: dict[int, np.ndarray], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    for rf in sorted(s21s):
        g = group_of(rf)
        ax.plot(freqs[rf], s21s[rf], label=f"RF{rf} (group {g})", color=GROUP_COLOR[g], linewidth=1.15, alpha=0.85)
    decorate(ax, "SP10T measured S21 - all 10 states", y_max=0.0)
    ax.set_ylim(-12.0, 0.0)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7, ncol=1)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_rl_group_overlay(freqs: dict[int, np.ndarray], traces: dict[int, dict[str, np.ndarray]], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    reps = {"C": 9, "B": 2, "A": 1}
    for g, rf in reps.items():
        color = GROUP_COLOR[g]
        ax.plot(freqs[rf], traces[rf]["s11"], label=f"RF{rf} S11 (group {g})", color=color, linewidth=1.3)
        ax.plot(freqs[rf], traces[rf]["s22"], label=f"RF{rf} S22 (group {g})", color=color, linewidth=1.1, linestyle="--", alpha=0.9)
    decorate(ax, "SP10T measured return loss - group representatives", refs=(-10.0,), y_max=-1.0)
    ax.set_ylim(-30.0, 0.0)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_group_avg_s21(freqs: dict[int, np.ndarray], s21s: dict[int, np.ndarray], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    for g, members in (("C", GROUP_C), ("B", GROUP_B), ("A", GROUP_A)):
        stacked = np.stack([s21s[rf] for rf in members])
        ax.plot(freqs[members[0]], stacked.mean(axis=0), label=f"Group {g} avg (RF{members[0]}/{members[-1]} etc.)", color=GROUP_COLOR[g], linewidth=1.9)
    decorate(ax, "SP10T measured S21 - group averages", y_max=0.0)
    ax.set_ylim(-12.0, 0.0)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_rl_6to8_zoom(freqs: dict[int, np.ndarray], traces: dict[int, dict[str, np.ndarray]], out: Path) -> None:
    """Highlight the return-loss cliff above 6 GHz: combined RL of all 10 states, 5-9 GHz."""
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    for rf in sorted(traces):
        g = group_of(rf)
        rl = np.maximum(traces[rf]["s11"], traces[rf]["s22"])
        ax.plot(freqs[rf], rl, label=f"RF{rf} (group {g})", color=GROUP_COLOR[g], linewidth=1.15, alpha=0.8)
    ax.axhline(-10.0, color="#303640", linewidth=1.2, linestyle=":")
    ax.text(8.85, -10.35, "-10 dB target", fontsize=7, color="#303640")
    ax.axvline(F_6G, color="#1f3864", alpha=0.55, linewidth=0.9, linestyle="--")
    ax.axvline(F_8G, color="#b42318", alpha=0.65, linewidth=1.0, linestyle="--")
    ax.text(F_6G, -1.5, "6 GHz", fontsize=7, color="#1f3864", ha="center")
    ax.text(F_8G, -1.5, "8 GHz", fontsize=7, color="#b42318", ha="center")
    ax.set_title("SP10T measured return loss - all 10 states, 5-9 GHz (RL degradation above 6 GHz)")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Return loss (dB)")
    ax.set_xlim(5.0, 9.0)
    ax.set_ylim(-30.0, 0.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7, ncol=1)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def connector_pair_with_100mm_trace_loss() -> tuple[np.ndarray, np.ndarray]:
    """Estimate two SMA+30 mm line models plus the remaining 40 mm FR4 trace."""
    f_conn, conn = load_s2p(CONNECTOR_S2P)
    pair_joint_loss = -2.0 * conn["s21"]
    remaining_40mm = np.array([0.4 * fr4_trace_loss_db_per_100mm(f, 0.02) for f in f_conn])
    return f_conn, np.maximum(pair_joint_loss + remaining_40mm, 0.0)


def plot_fr4_trace_loss(out: Path) -> None:
    """Estimated FR4 trace loss and two-connector extra IL vs frequency."""
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    fgrid = np.linspace(0.5, 8.0, 151)
    lo = np.array([fr4_trace_loss_db_per_100mm(f, 0.015) for f in fgrid])
    hi = np.array([fr4_trace_loss_db_per_100mm(f, 0.025) for f in fgrid])
    nom = np.array([fr4_trace_loss_db_per_100mm(f, 0.02) for f in fgrid])
    ax.fill_between(fgrid, lo, hi, color="#9aa1aa", alpha=0.25, label="tanδ 0.015-0.025 range (100 mm)")
    ax.plot(fgrid, nom, color="#1f3864", linewidth=1.8, label="100 mm, tanδ=0.02 (longest ~100 mm)")
    ax.plot(fgrid, nom * 1.23, color="#b42318", linewidth=1.3, linestyle="--", label="123 mm upper ref (group A equiv.)")
    f_conn, connector_loss = connector_pair_with_100mm_trace_loss()
    m_conn = (f_conn >= 0.5) & (f_conn <= 8.0)
    ax.plot(f_conn[m_conn], connector_loss[m_conn], color="#6a1b9a", linewidth=1.6, label="2 x (SMA + 30 mm line) + 40 mm FR4")
    ax.axvline(F_6G, color="#1f3864", alpha=0.55, linewidth=0.9, linestyle="--")
    ax.axvline(F_8G, color="#b42318", alpha=0.65, linewidth=1.0, linestyle="--")
    ax.text(F_6G, 3.6, "6 GHz", fontsize=7, color="#1f3864", ha="center")
    ax.text(F_8G, 3.6, "8 GHz", fontsize=7, color="#b42318", ha="center")
    ax.set_title("FR4 trace and connector insertion-loss estimates")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Trace loss (dB)")
    ax.set_xlim(0.5, 8.0)
    ax.set_ylim(0.0, 4.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="upper left", fontsize=8)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_il_vs_datasheet(freqs: dict[int, np.ndarray], s21s: dict[int, np.ndarray], out: Path) -> None:
    """Measured group-average S21 vs HMC7992 datasheet switch IL (1x / 2x)."""
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    for g, members in (("C", GROUP_C), ("B", GROUP_B), ("A", GROUP_A)):
        stacked = np.stack([s21s[rf] for rf in members])
        ax.plot(freqs[members[0]], stacked.mean(axis=0), label=f"Measured group {g} avg", color=GROUP_COLOR[g], linewidth=1.8)
    fx = np.array([p[0] for p in DATASHEET_IL_SINGLE])
    fy1 = np.array([-p[1] for p in DATASHEET_IL_SINGLE])
    fy2 = np.array([-2 * p[1] for p in DATASHEET_IL_SINGLE])
    ax.plot(fx, fy1, color="#6f7782", linewidth=1.6, linestyle="--", label="Datasheet switch IL x1 (0.6/0.7/1.0 dB)")
    ax.plot(fx, fy2, color="#303640", linewidth=1.6, linestyle="--", label="Datasheet switch IL x2 (2 switches)")
    ax.axvspan(6.0, 8.0, color="#8a8f98", alpha=0.10)
    ax.text(7.0, -1.4, "outside specified range\n(Fig. 7/10 extend to 8 GHz)", fontsize=7.5, color="#687381", ha="center")
    fig_lo, fig_hi = DATASHEET_FIG_8G_IL_RANGE
    ax.errorbar(7.84, -(fig_lo + fig_hi) / 2, yerr=(fig_hi - fig_lo) / 2, fmt="o", color="#6f7782", capsize=4, markersize=3.5, label="Fig. 7/10 @ 8 GHz x1 (~1.1-1.7 dB)")
    ax.errorbar(7.98, -(fig_lo + fig_hi), yerr=(fig_hi - fig_lo), fmt="o", color="#303640", capsize=4, markersize=3.5, label="Fig. 7/10 @ 8 GHz x2 (~2.2-3.4 dB)")
    ax.axhline(-3.0, color="#8a8f98", alpha=0.45, linewidth=0.8, linestyle=":")
    ax.text(0.6, -3.15, "-3 dB engineering reference", fontsize=7, color="#8a8f98")
    ax.set_title("SP10T measured path IL vs HMC7992 datasheet switch IL")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(0.5, 8.0)
    ax.set_ylim(-10.0, 0.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="lower left", fontsize=7.5)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_il_6g_vs_8g(metrics: dict[int, dict], out: Path) -> None:
    rfs = sorted(metrics)
    x = np.arange(len(rfs))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    v6 = [metrics[rf]["s21_at_6g"] for rf in rfs]
    v8 = [metrics[rf]["s21_at_8g"] for rf in rfs]
    bars6 = ax.bar(x - w / 2, v6, width=w, label="S21 @ 6 GHz (rated max)", color="#1f3864")
    bars8 = ax.bar(x + w / 2, v8, width=w, label="S21 @ 8 GHz (requirement)", color="#c44e52")
    for bars in (bars6, bars8):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.25, f"{bar.get_height():.2f}", ha="center", va="top", fontsize=6)
    for ref in (-3.0, -6.0):
        ax.axhline(ref, color="#8a8f98", alpha=0.5, linewidth=0.9, linestyle=":")
    ax.text(9.35, -3.1, "-3 dB", fontsize=7, color="#8a8f98")
    ax.text(9.35, -6.1, "-6 dB", fontsize=7, color="#8a8f98")
    ax.set_xticks(x)
    ax.set_xticklabels([f"RF{rf}" for rf in rfs], fontsize=8)
    ax.set_ylim(-10.0, 0.0)
    ax.set_ylabel("S21 (dB)")
    ax.set_xlabel("SP10T state (RF port)")
    ax.set_title("SP10T measured insertion loss - 6 GHz rated edge vs 8 GHz extension")
    ax.grid(True, axis="y", which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="lower left", fontsize=8)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def isolation_metrics(freq: np.ndarray, traces: dict[str, np.ndarray]) -> dict:
    conservative_db = np.maximum(traces["s21"], traces["s12"])
    payload: dict = {}
    for fq in (0.5, 1.0, 2.0, 4.0, 6.0, 7.0, 8.0, 10.0):
        idx = int(np.argmin(np.abs(freq - fq)))
        payload[f"isolation_at_{fq:g}g_db"] = float(-conservative_db[idx])
        payload[f"actual_freq_at_{fq:g}g_ghz"] = float(freq[idx])
    for lo, hi, key in ((0.5, 6.0, "0p5_6g"), (6.0, 8.0, "6_8g"), (7.0, 8.0, "7_8g")):
        mask = (freq >= lo) & (freq <= hi)
        segment = conservative_db[mask]
        idx = int(np.argmax(segment))
        payload[f"min_isolation_{key}_db"] = float(-segment[idx])
        payload[f"min_isolation_{key}_freq_ghz"] = float(freq[mask][idx])
    return payload


def plot_isolation_typical(
    freqs: dict[str, np.ndarray], traces: dict[str, dict[str, np.ndarray]], out: Path
) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    colors = {"RF7-RF8": "#1f3864", "RF9-RF10": "#b42318"}
    for label in ISOLATION_PAIRS:
        isolation = -np.maximum(traces[label]["s21"], traces[label]["s12"])
        ax.plot(
            freqs[label],
            isolation,
            color=colors[label],
            linewidth=1.8,
            label=f"{label} ({ISOLATION_TOPOLOGY[label]})",
        )
        for fq in (6.0, 8.0):
            idx = int(np.argmin(np.abs(freqs[label] - fq)))
            value = float(isolation[idx])
            ax.scatter([freqs[label][idx]], [value], color=colors[label], s=20, zorder=3)
            ax.text(freqs[label][idx] + 0.08, value + 0.9, f"{value:.1f} dB", fontsize=7, color=colors[label])
    ax.axvline(6.0, color="#1f3864", alpha=0.5, linewidth=0.9, linestyle="--")
    ax.axvline(8.0, color="#b42318", alpha=0.6, linewidth=0.9, linestyle="--")
    ax.set_title("SP10T measured representative port-to-port isolation")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Isolation (dB, higher is better)")
    ax.set_xlim(0.5, 10.0)
    ax.set_ylim(20.0, 90.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="upper right", fontsize=8)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot SVG charts for the SP10T measured S2P data.")
    parser.add_argument("--s2p-dir", type=Path, default=REPO_ROOT / "docs" / "test" / "SP10T_S2P")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--band-min-ghz", type=float, default=0.5)
    parser.add_argument("--band-max-ghz", type=float, default=8.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    freqs: dict[int, np.ndarray] = {}
    traces: dict[int, dict[str, np.ndarray]] = {}
    for rf in range(1, 11):
        freq, tr = load_s2p(args.s2p_dir / f"{rf}.s2p")
        freqs[rf] = freq
        traces[rf] = tr

    metrics = {
        rf: metrics_for(freqs[rf], traces[rf], (args.band_min_ghz, args.band_max_ghz))
        for rf in range(1, 11)
    }
    payload = {f"RF{rf}": {"group": group_of(rf), **metrics[rf]} for rf in range(1, 11)}
    (out_dir / "sp10t_measured_metrics.json").write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    isolation_freqs: dict[str, np.ndarray] = {}
    isolation_traces: dict[str, dict[str, np.ndarray]] = {}
    isolation_payload: dict[str, dict] = {}
    for label, filename in ISOLATION_PAIRS.items():
        freq, tr = load_s2p(args.s2p_dir / filename)
        isolation_freqs[label] = freq
        isolation_traces[label] = tr
        isolation_payload[label] = {"source_file": filename, **isolation_metrics(freq, tr)}
    (out_dir / "sp10t_measured_isolation_metrics.json").write_text(
        json.dumps(isolation_payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    plot_s21_overlay(freqs, {rf: traces[rf]["s21"] for rf in range(1, 11)}, out_dir / "sp10t_measured_s21_overlay_all.svg")
    plot_rl_group_overlay(freqs, traces, out_dir / "sp10t_measured_rl_group_overlay.svg")
    plot_rl_6to8_zoom(freqs, traces, out_dir / "sp10t_measured_rl_6to8_zoom.svg")
    plot_group_avg_s21(freqs, {rf: traces[rf]["s21"] for rf in range(1, 11)}, out_dir / "sp10t_measured_group_avg_s21.svg")
    plot_il_6g_vs_8g(metrics, out_dir / "sp10t_measured_il_6g_vs_8g.svg")
    plot_il_vs_datasheet(freqs, {rf: traces[rf]["s21"] for rf in range(1, 11)}, out_dir / "sp10t_measured_il_vs_datasheet.svg")
    plot_fr4_trace_loss(out_dir / "sp10t_measured_fr4_trace_loss.svg")
    plot_isolation_typical(isolation_freqs, isolation_traces, out_dir / "sp10t_measured_isolation_typical.svg")
    print(f"Wrote charts + metrics to {out_dir}")


if __name__ == "__main__":
    main()
