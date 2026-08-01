"""ADS dataset path and export helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Sequence

from simads.ads.workspace import AdsCommandPlan
from simads.config import AdsProfile


VALID_TRACES = ("S11", "S21", "S12", "S22")


@dataclass(frozen=True)
class DatasetExportPlan:
    profile_id: str
    workspace: Path
    dataset_path: Path
    output_path: Path
    delimiter: str = "tab"
    output_format: str = "ads-display"
    traces: tuple[str, ...] = ("S21",)

    def to_manifest(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "workspace": str(self.workspace),
            "dataset_path": str(self.dataset_path),
            "output_path": str(self.output_path),
            "delimiter": self.delimiter,
            "output_format": self.output_format,
            "traces": list(self.traces),
        }


def db_from_mag(value: float) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-30))


def phase_deg(value: complex) -> float:
    return math.degrees(math.atan2(value.imag, value.real))


def delimiter_text(name: str) -> str:
    if name == "tab":
        return "\t"
    if name == "comma":
        return ","
    raise ValueError(f"unsupported delimiter: {name}")


def dataset_path(workspace: Path, cell: str, suffix: str = "a") -> Path:
    stem = cell.removesuffix(".ds")
    if stem.endswith(f"_FEM_{suffix}"):
        name = stem
    elif stem.endswith("_FEM"):
        name = f"{stem}_{suffix}"
    else:
        name = f"{stem}_FEM_{suffix}"
    return workspace / "data" / f"{name}.ds"


def write_full_table(rows: list[dict[str, float]], path: Path, delimiter: str) -> None:
    if not rows:
        raise ValueError("no rows to export")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def write_ads_display_like_table(rows: list[dict[str, float]], path: Path, traces: Sequence[str]) -> None:
    if not rows:
        raise ValueError("no rows to export")
    normalized_traces = tuple(trace.upper() for trace in traces)
    unknown = [trace for trace in normalized_traces if trace not in VALID_TRACES]
    if unknown:
        raise ValueError(f"unknown traces: {', '.join(unknown)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        for idx, trace in enumerate(normalized_traces):
            if idx:
                fp.write("\n\n")
            fp.write(f"freq\tdB({trace}_fitted)\n")
            key = trace.lower()
            for row in rows:
                fp.write(f"{row['frequency_hz']:.17E}\t{row[f'{key}_db']:.17E}\n")


def write_dataset_export(rows: list[dict[str, float]], plan: DatasetExportPlan) -> None:
    if plan.output_format == "ads-display":
        write_ads_display_like_table(rows, plan.output_path, plan.traces)
        return
    if plan.output_format == "full":
        write_full_table(rows, plan.output_path, delimiter_text(plan.delimiter))
        return
    raise ValueError(f"unsupported dataset export format: {plan.output_format}")


def build_dataset_export_plan(
    profile: AdsProfile,
    *,
    out: Path,
    cell: str | None = None,
    dataset: Path | None = None,
    suffix: str = "a",
    delimiter: str = "tab",
    output_format: str = "ads-display",
    traces: tuple[str, ...] = ("S21",),
) -> DatasetExportPlan:
    if dataset is None and not cell:
        raise ValueError("either cell or dataset is required")
    normalized_traces = tuple(trace.upper() for trace in traces)
    unknown = [trace for trace in normalized_traces if trace not in VALID_TRACES]
    if unknown:
        raise ValueError(f"unknown traces: {', '.join(unknown)}")
    return DatasetExportPlan(
        profile_id=profile.name,
        workspace=profile.workspace,
        dataset_path=dataset or dataset_path(profile.workspace, cell or "", suffix),
        output_path=out,
        delimiter=delimiter,
        output_format=output_format,
        traces=normalized_traces,
    )


def build_export_command(
    plan: DatasetExportPlan,
    *,
    ads_python: Path,
    script: Path,
) -> AdsCommandPlan:
    args = [
        "--workspace",
        str(plan.workspace),
        "--dataset",
        str(plan.dataset_path),
        "--out",
        str(plan.output_path),
        "--delimiter",
        plan.delimiter,
        "--format",
        plan.output_format,
        "--traces",
        *plan.traces,
    ]
    return AdsCommandPlan("export_ads_fem_dataset", ads_python, script, tuple(args), cwd=script.parents[1])
