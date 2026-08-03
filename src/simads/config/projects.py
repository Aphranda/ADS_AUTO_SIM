"""Project configuration helpers for ADS automation workflows.

Project configs describe repository-owned assets such as plans, layouts,
results, run manifests, reports, and references. Machine-specific ADS paths
remain in ``ads_profiles.json``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .profiles import repo_root


@dataclass(frozen=True)
class ProjectAdsConfig:
    library: str | None = None
    template_cell: str | None = None
    substrate: str | None = None
    stackup_config: Path | None = None
    setup_view: str | None = None
    rfpro_emsetup_view: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "library": self.library,
            "template_cell": self.template_cell,
            "substrate": self.substrate,
            "stackup_config": str(self.stackup_config) if self.stackup_config is not None else None,
            "setup_view": self.setup_view,
            "rfpro_emsetup_view": self.rfpro_emsetup_view,
        }


@dataclass(frozen=True)
class ProjectFrequency:
    start_ghz: float | None = None
    stop_ghz: float | None = None
    passband_start_ghz: float | None = None
    passband_stop_ghz: float | None = None

    def to_dict(self) -> dict[str, float | None]:
        return {
            "start_ghz": self.start_ghz,
            "stop_ghz": self.stop_ghz,
            "passband_start_ghz": self.passband_start_ghz,
            "passband_stop_ghz": self.passband_stop_ghz,
        }


@dataclass(frozen=True)
class SweepConfig:
    sweep_id: str
    pipeline_id: str | None = None
    plan: Path | None = None
    layouts_dir: Path | None = None
    results_dir: Path | None = None
    summary: Path | None = None
    profile: str | None = None
    target_profile: str | None = None
    device_id: str | None = None
    template_cell: str | None = None
    setup_view: str | None = None
    rfpro_emsetup_view: str | None = None
    generator: dict[str, object] = field(default_factory=dict)
    optimizer: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "sweep_id": self.sweep_id,
            "pipeline_id": self.pipeline_id,
            "plan": str(self.plan) if self.plan is not None else None,
            "layouts_dir": str(self.layouts_dir) if self.layouts_dir is not None else None,
            "results_dir": str(self.results_dir) if self.results_dir is not None else None,
            "summary": str(self.summary) if self.summary is not None else None,
            "profile": self.profile,
            "target_profile": self.target_profile,
            "device_id": self.device_id,
            "template_cell": self.template_cell,
            "setup_view": self.setup_view,
            "rfpro_emsetup_view": self.rfpro_emsetup_view,
            "generator": self.generator,
            "optimizer": self.optimizer,
        }


@dataclass(frozen=True)
class ProjectConfig:
    project_id: str
    name: str
    schema_version: str
    project_root: Path
    plans_dir: Path
    layouts_dir: Path
    results_dir: Path
    runs_dir: Path
    reports_dir: Path
    references_dir: Path
    device_family: str | None = None
    primary_device_type: str | None = None
    default_profile: str | None = None
    target_profile: str | None = None
    pipeline_id: str | None = None
    frequency: ProjectFrequency = ProjectFrequency()
    ads: ProjectAdsConfig = ProjectAdsConfig()
    active_sweep: str | None = None
    sweeps: dict[str, SweepConfig] = field(default_factory=dict)

    def dirs(self) -> dict[str, Path]:
        return {
            "project_root": self.project_root,
            "plans": self.plans_dir,
            "layouts": self.layouts_dir,
            "results": self.results_dir,
            "runs": self.runs_dir,
            "reports": self.reports_dir,
            "references": self.references_dir,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "name": self.name,
            "device_family": self.device_family,
            "primary_device_type": self.primary_device_type,
            "default_profile": self.default_profile,
            "target_profile": self.target_profile,
            "pipeline_id": self.pipeline_id,
            "active_sweep": self.active_sweep,
            "project_root": str(self.project_root),
            "plans_dir": str(self.plans_dir),
            "layouts_dir": str(self.layouts_dir),
            "results_dir": str(self.results_dir),
            "runs_dir": str(self.runs_dir),
            "reports_dir": str(self.reports_dir),
            "references_dir": str(self.references_dir),
            "frequency": self.frequency.to_dict(),
            "ads": self.ads.to_dict(),
            "sweeps": {name: sweep.to_dict() for name, sweep in self.sweeps.items()},
        }

    def get_sweep(self, sweep_id: str | None = None) -> SweepConfig | None:
        key = sweep_id or self.active_sweep
        if key is None:
            return None
        try:
            return self.sweeps[key]
        except KeyError as exc:
            names = ", ".join(sorted(self.sweeps))
            raise ValueError(f"unknown sweep {key!r} for project {self.project_id!r}; expected one of: {names}") from exc


def default_projects_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "config" / "projects"


def default_project_config_path(project_id: str, root: Path | None = None) -> Path:
    return default_projects_dir(root) / f"{project_id}.json"


def root_relative_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _optional_root_relative_path(root: Path, value: Any) -> Path | None:
    if value in (None, ""):
        return None
    return root_relative_path(root, Path(str(value)))


def _optional_float(data: dict[str, Any], key: str) -> float | None:
    value = data.get(key)
    if value in (None, ""):
        return None
    return float(value)


def _path_from_mapping(root: Path, data: dict[str, Any], key: str, fallback: str) -> Path:
    return root_relative_path(root, Path(str(data.get(key, fallback))))


def sweep_from_mapping(root: Path, sweep_id: str, data: dict[str, Any]) -> SweepConfig:
    generator = _resolve_nested_paths(root, data.get("generator"), {"script", "layout_generator"})
    optimizer = _resolve_nested_paths(root, data.get("optimizer"), {"script", "dataset", "seed_params", "prediction_report"})
    return SweepConfig(
        sweep_id=sweep_id,
        pipeline_id=str(data["pipeline_id"]) if data.get("pipeline_id") else None,
        plan=_optional_root_relative_path(root, data.get("plan")),
        layouts_dir=_optional_root_relative_path(root, data.get("layouts_dir")),
        results_dir=_optional_root_relative_path(root, data.get("results_dir")),
        summary=_optional_root_relative_path(root, data.get("summary")),
        profile=str(data["profile"]) if data.get("profile") else None,
        target_profile=str(data["target_profile"]) if data.get("target_profile") else None,
        device_id=str(data["device_id"]) if data.get("device_id") else None,
        template_cell=str(data["template_cell"]) if data.get("template_cell") else None,
        setup_view=str(data["setup_view"]) if data.get("setup_view") else None,
        rfpro_emsetup_view=str(data["rfpro_emsetup_view"]) if data.get("rfpro_emsetup_view") else None,
        generator=generator,
        optimizer=optimizer,
    )


def _resolve_nested_paths(root: Path, value: Any, path_keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, object] = {}
    for key, item in value.items():
        if key in path_keys and item not in (None, ""):
            output[str(key)] = root_relative_path(root, Path(str(item)))
        else:
            output[str(key)] = item
    return output


def project_from_mapping(data: dict[str, Any], *, root: Path | None = None) -> ProjectConfig:
    base = root or repo_root()
    project_id = str(data["project_id"])
    project_root_fallback = f"projects/{project_id}"
    project_root = _path_from_mapping(base, data, "project_root", project_root_fallback)
    frequency_data = data.get("frequency") if isinstance(data.get("frequency"), dict) else {}
    ads_data = data.get("ads") if isinstance(data.get("ads"), dict) else {}
    sweep_data = data.get("sweeps") if isinstance(data.get("sweeps"), dict) else {}
    sweeps = {
        str(sweep_id): sweep_from_mapping(base, str(sweep_id), mapping)
        for sweep_id, mapping in sweep_data.items()
        if isinstance(mapping, dict)
    }

    return ProjectConfig(
        schema_version=str(data.get("schema_version", "0.1.0")),
        project_id=project_id,
        name=str(data.get("name", project_id)),
        device_family=str(data["device_family"]) if data.get("device_family") else None,
        primary_device_type=str(data["primary_device_type"]) if data.get("primary_device_type") else None,
        default_profile=str(data["default_profile"]) if data.get("default_profile") else None,
        target_profile=str(data["target_profile"]) if data.get("target_profile") else None,
        pipeline_id=str(data["pipeline_id"]) if data.get("pipeline_id") else None,
        active_sweep=str(data["active_sweep"]) if data.get("active_sweep") else None,
        project_root=project_root,
        plans_dir=_path_from_mapping(base, data, "plans_dir", f"{project_root_fallback}/plans"),
        layouts_dir=_path_from_mapping(base, data, "layouts_dir", f"{project_root_fallback}/layouts"),
        results_dir=_path_from_mapping(base, data, "results_dir", f"{project_root_fallback}/results"),
        runs_dir=_path_from_mapping(base, data, "runs_dir", f"{project_root_fallback}/runs"),
        reports_dir=_path_from_mapping(base, data, "reports_dir", f"{project_root_fallback}/reports"),
        references_dir=_path_from_mapping(base, data, "references_dir", f"{project_root_fallback}/references"),
        frequency=ProjectFrequency(
            start_ghz=_optional_float(frequency_data, "start_ghz"),
            stop_ghz=_optional_float(frequency_data, "stop_ghz"),
            passband_start_ghz=_optional_float(frequency_data, "passband_start_ghz"),
            passband_stop_ghz=_optional_float(frequency_data, "passband_stop_ghz"),
        ),
        ads=ProjectAdsConfig(
            library=str(ads_data["library"]) if ads_data.get("library") else None,
            template_cell=str(ads_data["template_cell"]) if ads_data.get("template_cell") else None,
            substrate=str(ads_data["substrate"]) if ads_data.get("substrate") else None,
            stackup_config=_optional_root_relative_path(base, ads_data.get("stackup_config")),
            setup_view=str(ads_data["setup_view"]) if ads_data.get("setup_view") else None,
            rfpro_emsetup_view=str(ads_data["rfpro_emsetup_view"]) if ads_data.get("rfpro_emsetup_view") else None,
        ),
        sweeps=sweeps,
    )


def load_project_data(project_id: str, *, root: Path | None = None, path: Path | None = None) -> dict[str, Any]:
    config_path = path or default_project_config_path(project_id, root)
    if not config_path.exists():
        raise FileNotFoundError(f"project config not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"project config must be a JSON object: {config_path}")
    return data


def load_project(project_id: str, *, root: Path | None = None, path: Path | None = None) -> ProjectConfig:
    return project_from_mapping(load_project_data(project_id, root=root, path=path), root=root)


def project_names(*, root: Path | None = None) -> list[str]:
    projects_dir = default_projects_dir(root)
    if not projects_dir.exists():
        return []
    return sorted(path.stem for path in projects_dir.glob("*.json"))
