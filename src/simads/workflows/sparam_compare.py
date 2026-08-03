"""Compare two S-parameter traces on a common frequency grid."""

from __future__ import annotations

import argparse
import csv
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from simads.domain import SimulationResultSpec, SweepSpec
from simads.runtime import (
    SimulationManifestPayload,
    SimulationRunContext,
    artifact_entry,
    write_simulation_manifests,
)
from simads.scoring import choose_frequency_column, choose_sparam_column, frequency_to_ghz, interp, series_to_db

SPARAMS = ("s11", "s21", "s12", "s22")
KEY_FREQS_GHZ = (5.0, 6.0, 7.0, 8.0, 9.0)


@dataclass(frozen=True)
class SParamTrace:
    label: str
    source: Path
    freq_ghz: list[float]
    traces_db: dict[str, list[float]]

    def interpolated(self, name: str, freq_ghz: float) -> float:
        return interp(self.freq_ghz, self.traces_db[name], freq_ghz)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def load_sparam_trace(path: Path, *, label: str | None = None) -> SParamTrace:
    if path.suffix.lower() == ".s2p":
        return load_s2p_trace(path, label=label)
    rows = read_csv_rows(path)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    columns = list(rows[0])
    freq_col = choose_frequency_column(columns)
    if freq_col is None:
        raise ValueError(f"CSV has no frequency column: {path}")
    freq_ghz = frequency_to_ghz([row[freq_col] for row in rows])
    traces: dict[str, list[float]] = {}
    for name in SPARAMS:
        col = choose_sparam_column(columns, name)
        if col is not None:
            traces[name] = series_to_db([row[col] for row in rows])
    if "s21" not in traces:
        raise ValueError(f"CSV has no S21 column: {path}")
    return SParamTrace(label=label or path.stem, source=path, freq_ghz=freq_ghz, traces_db=traces)


def load_s2p_trace(path: Path, *, label: str | None = None) -> SParamTrace:
    import sys

    repo_root = Path(__file__).resolve().parents[3]
    tools_dir = repo_root / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    from analyze_filter_s2p import read_s2p

    samples = read_s2p(path)
    if not samples:
        raise ValueError(f"no S-parameter samples found: {path}")
    return SParamTrace(
        label=label or path.stem,
        source=path,
        freq_ghz=[row[0] for row in samples],
        traces_db={
            "s11": [row[1] for row in samples],
            "s21": [row[2] for row in samples],
            "s12": [row[3] for row in samples],
            "s22": [row[4] for row in samples],
        },
    )


def common_grid(left: SParamTrace, right: SParamTrace, *, grid: str = "left", points: int | None = None) -> list[float]:
    low = max(min(left.freq_ghz), min(right.freq_ghz))
    high = min(max(left.freq_ghz), max(right.freq_ghz))
    if low >= high:
        raise ValueError(f"traces do not overlap: {left.source} vs {right.source}")
    if points is not None:
        if points < 2:
            raise ValueError("points must be >= 2")
        step = (high - low) / (points - 1)
        return [low + step * idx for idx in range(points)]
    source = right.freq_ghz if grid == "right" else left.freq_ghz
    values = [freq for freq in source if low <= freq <= high]
    if not values:
        return [low, high]
    return values


def compare_traces(
    left: SParamTrace,
    right: SParamTrace,
    *,
    grid: str = "left",
    points: int | None = None,
    sparams: Iterable[str] = ("s11", "s21", "s22"),
) -> list[dict[str, str]]:
    names = [name.lower() for name in sparams if name.lower() in left.traces_db and name.lower() in right.traces_db]
    if "s21" not in names:
        raise ValueError("both traces must contain S21")
    freqs = common_grid(left, right, grid=grid, points=points)
    rows: list[dict[str, str]] = []
    for freq in freqs:
        row = {"freq_ghz": f"{freq:.9g}"}
        for name in names:
            left_value = left.interpolated(name, freq)
            right_value = right.interpolated(name, freq)
            row[f"{left.label}_{name}_db"] = f"{left_value:.6g}"
            row[f"{right.label}_{name}_db"] = f"{right_value:.6g}"
            row[f"delta_{name}_db"] = f"{right_value - left_value:.6g}"
            row[f"abs_delta_{name}_db"] = f"{abs(right_value - left_value):.6g}"
        rows.append(row)
    return rows


def summarize_compare(rows: list[dict[str, str]], *, sparams: Iterable[str] = ("s11", "s21", "s22")) -> list[dict[str, str]]:
    summaries: list[dict[str, str]] = []
    for name in sparams:
        abs_col = f"abs_delta_{name}_db"
        delta_col = f"delta_{name}_db"
        if not rows or abs_col not in rows[0]:
            continue
        abs_values = [float(row[abs_col]) for row in rows]
        delta_values = [float(row[delta_col]) for row in rows]
        pass_abs = [float(row[abs_col]) for row in rows if 6.0 <= float(row["freq_ghz"]) <= 8.0]
        summary = {
            "sparam": name,
            "points": str(len(rows)),
            "max_abs_delta_db": f"{max(abs_values):.6g}",
            "mean_abs_delta_db": f"{sum(abs_values) / len(abs_values):.6g}",
            "rms_delta_db": f"{math.sqrt(sum(value * value for value in delta_values) / len(delta_values)):.6g}",
            "passband_mean_abs_delta_db": f"{sum(pass_abs) / len(pass_abs):.6g}" if pass_abs else "nan",
        }
        for freq in KEY_FREQS_GHZ:
            nearest = min(rows, key=lambda row: abs(float(row["freq_ghz"]) - freq))
            summary[f"delta_at_{freq:g}g_db"] = nearest[delta_col]
        summaries.append(summary)
    return summaries


def write_rows(path: Path, rows: list[dict[str, str]]) -> Path:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def plot_compare_svg(
    left: SParamTrace,
    right: SParamTrace,
    rows: list[dict[str, str]],
    out: Path,
    *,
    sparams: Iterable[str] = ("s21",),
    title: str | None = None,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    freq = [float(row["freq_ghz"]) for row in rows]
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    colors = {"s11": "#1f77b4", "s21": "#c44e52", "s22": "#8172b2"}
    for name in sparams:
        lname = f"{left.label}_{name}_db"
        rname = f"{right.label}_{name}_db"
        if rows and lname in rows[0] and rname in rows[0]:
            ax.plot(freq, [float(row[lname]) for row in rows], color=colors.get(name), linewidth=1.2, label=f"{left.label} {name.upper()}")
            ax.plot(
                freq,
                [float(row[rname]) for row in rows],
                color=colors.get(name),
                linewidth=1.2,
                linestyle="--",
                label=f"{right.label} {name.upper()}",
            )
    ax.axvspan(6.0, 8.0, color="#7bc96f", alpha=0.14, label="6-8G passband")
    ax.axvline(5.0, color="#d62728", alpha=0.62, linewidth=1.0, linestyle=":", label="5G stop target")
    ax.set_title(title or f"{left.label} vs {right.label}")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(min(freq), max(freq))
    ax.set_ylim(-60.0, 2.0)
    ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    ax.legend(loc="lower left", fontsize=8)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def run_compare(
    *,
    left_path: Path,
    right_path: Path,
    out_csv: Path,
    summary_csv: Path,
    svg: Path | None,
    left_label: str = "ads",
    right_label: str = "hfss",
    grid: str = "left",
    points: int | None = None,
    sparams: Iterable[str] = ("s11", "s21", "s22"),
) -> dict[str, Path]:
    left = load_sparam_trace(left_path, label=left_label)
    right = load_sparam_trace(right_path, label=right_label)
    rows = compare_traces(left, right, grid=grid, points=points, sparams=sparams)
    summary = summarize_compare(rows, sparams=sparams)
    written = {
        "compare_csv": write_rows(out_csv, rows),
        "summary_csv": write_rows(summary_csv, summary),
    }
    if svg is not None:
        written["svg"] = plot_compare_svg(left, right, rows, svg, sparams=[name for name in sparams if name != "s12"])
    return written


def write_compare_manifest(
    *,
    run_dir: Path,
    run_id: str,
    project_id: str,
    round_id: str,
    candidate_id: str,
    profile_id: str,
    ads_path: Path,
    hfss_path: Path,
    written: dict[str, Path],
    elapsed_s: float,
) -> dict[str, Path]:
    rows = read_csv_rows(written["compare_csv"])
    freqs = [float(row["freq_ghz"]) for row in rows]
    payload = SimulationManifestPayload(
        context=SimulationRunContext(
            project_id=project_id,
            round_id=round_id,
            candidate_id=candidate_id,
            profile_id=profile_id,
            simulator="sparam_compare",
            run_id=run_id,
            run_dir=run_dir,
            device_id="filter.interdigital",
            profile_snapshot={
                "left_backend": "ads",
                "right_backend": "hfss",
                "compare_version": "sparam_compare_v1",
            },
        ),
        sweep=SweepSpec(start_ghz=min(freqs), stop_ghz=max(freqs), points=len(freqs), sweep_type="Aligned"),
        inputs={
            "ads_trace": str(ads_path),
            "hfss_trace": str(hfss_path),
        },
        outputs={
            "compare_csv": str(written["compare_csv"]),
            "summary_csv": str(written["summary_csv"]),
            "svg": str(written["svg"]) if "svg" in written else None,
        },
        result=SimulationResultSpec(
            simulator="sparam_compare",
            trace_csv=written["compare_csv"],
            score_csv=written["summary_csv"],
            svg=written.get("svg"),
        ),
    )
    artifacts = [
        artifact_entry("ads_trace", ads_path, producer="ADS RFPro/FEM"),
        artifact_entry("hfss_trace", hfss_path, producer="HFSS 3D Layout"),
        artifact_entry("compare_csv", written["compare_csv"], producer="compare_ads_hfss_sparams.py"),
        artifact_entry("summary", written["summary_csv"], producer="compare_ads_hfss_sparams.py"),
        artifact_entry("svg", written.get("svg"), producer="compare_ads_hfss_sparams.py"),
        artifact_entry("state", run_dir / "state.json", producer="compare_ads_hfss_sparams.py"),
    ]
    return write_simulation_manifests(
        run_dir=run_dir,
        run_id=run_id,
        payload=payload,
        artifacts=artifacts,
        status="completed",
        stage="completed",
        elapsed_s=elapsed_s,
        message="ADS/HFSS S-parameter comparison completed.",
    )


def parse_sparams(value: str) -> list[str]:
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare ADS and HFSS S-parameter traces.")
    parser.add_argument("--ads", type=Path, required=True, help="ADS RFPro CSV or S2P.")
    parser.add_argument("--hfss", type=Path, required=True, help="HFSS trace CSV or S2P.")
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--svg", type=Path, default=None)
    parser.add_argument("--ads-label", default="ads")
    parser.add_argument("--hfss-label", default="hfss")
    parser.add_argument("--grid", choices=["left", "right"], default="left")
    parser.add_argument("--points", type=int, default=None, help="Optional uniform grid point count over the overlap.")
    parser.add_argument("--sparams", default="s11,s21,s22")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4")
    parser.add_argument("--round-id", default="manual")
    parser.add_argument("--candidate-id", default=None)
    parser.add_argument("--profile-id", default="ads_hfss_compare")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--run-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.monotonic()
    written = run_compare(
        left_path=args.ads,
        right_path=args.hfss,
        out_csv=args.out_csv,
        summary_csv=args.summary_csv,
        svg=args.svg,
        left_label=args.ads_label,
        right_label=args.hfss_label,
        grid=args.grid,
        points=args.points,
        sparams=parse_sparams(args.sparams),
    )
    if args.write_manifest:
        context = SimulationRunContext(
            project_id=args.project_id,
            round_id=args.round_id,
            candidate_id=args.candidate_id or args.out_csv.parent.name,
            profile_id=args.profile_id,
            simulator="sparam_compare",
            run_id=args.run_id,
            run_dir=args.run_dir,
        )
        run_id = context.resolved_run_id()
        repo_root = Path(__file__).resolve().parents[3]
        run_dir = context.resolved_run_dir(repo_root, run_id)
        manifest_paths = write_compare_manifest(
            run_dir=run_dir,
            run_id=run_id,
            project_id=args.project_id,
            round_id=args.round_id,
            candidate_id=context.candidate_id,
            profile_id=args.profile_id,
            ads_path=args.ads,
            hfss_path=args.hfss,
            written=written,
            elapsed_s=time.monotonic() - started,
        )
        written.update({f"manifest_{key}": path for key, path in manifest_paths.items()})
    for kind, path in written.items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()
