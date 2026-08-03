"""Standard pipeline contracts for ADS automation workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .profiles import AdsProfile, repo_root
from .projects import ProjectConfig, SweepConfig, root_relative_path
from simads.devices import get_device
from simads.scoring import TARGET_SCORE_VERSIONS, TARGET_PROFILES


@dataclass(frozen=True)
class PipelineCheck:
    name: str
    path: Path | None
    ok: bool
    message: str


@dataclass(frozen=True)
class PipelineLayoutConfig:
    sweep_script: Path | None = None
    layout_generator_script: Path | None = None
    layout_output_dir: Path | None = None
    params_output_dir: Path | None = None
    require_layout_json: bool = True
    require_params_json: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "sweep_script": str(self.sweep_script) if self.sweep_script is not None else None,
            "layout_generator_script": str(self.layout_generator_script) if self.layout_generator_script is not None else None,
            "layout_output_dir": str(self.layout_output_dir) if self.layout_output_dir is not None else None,
            "params_output_dir": str(self.params_output_dir) if self.params_output_dir is not None else None,
            "require_layout_json": self.require_layout_json,
            "require_params_json": self.require_params_json,
        }


@dataclass(frozen=True)
class PipelineAdsConfig:
    import_script: Path | None = None
    clone_setup_script: Path | None = None
    rfpro_script: Path | None = None
    dataset_export_script: Path | None = None
    template_cell: str | None = None
    setup_view: str | None = None
    rfpro_emsetup_view: str | None = None
    workspace_profile: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "import_script": str(self.import_script) if self.import_script is not None else None,
            "clone_setup_script": str(self.clone_setup_script) if self.clone_setup_script is not None else None,
            "rfpro_script": str(self.rfpro_script) if self.rfpro_script is not None else None,
            "dataset_export_script": str(self.dataset_export_script) if self.dataset_export_script is not None else None,
            "template_cell": self.template_cell,
            "setup_view": self.setup_view,
            "rfpro_emsetup_view": self.rfpro_emsetup_view,
            "workspace_profile": self.workspace_profile,
        }


@dataclass(frozen=True)
class PipelineLayerConfig:
    metal_layer: str = "cond"
    via_layer: str = "pcvia1"
    boundary_layer: str = "EM_BOUNDARY"
    layer_map_version: str = "profile-default-v1"
    layer_map_strategy: str = "profile-default"
    layer_map_required: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "metal_layer": self.metal_layer,
            "via_layer": self.via_layer,
            "boundary_layer": self.boundary_layer,
            "layer_map_version": self.layer_map_version,
            "layer_map_strategy": self.layer_map_strategy,
            "layer_map_required": self.layer_map_required,
        }


@dataclass(frozen=True)
class PipelinePortConfig:
    names: tuple[str, ...] = ("P1", "P2")
    location_source: str = "params_json"
    unit: str = "mm"
    pad_layer: str = "cond"
    reference: str = "ground"

    def to_dict(self) -> dict[str, object]:
        return {
            "names": list(self.names),
            "location_source": self.location_source,
            "unit": self.unit,
            "pad_layer": self.pad_layer,
            "reference": self.reference,
        }


@dataclass(frozen=True)
class PipelineFrequencyConfig:
    start_ghz: float = 4.0
    stop_ghz: float = 10.0
    passband_start_ghz: float = 6.0
    passband_stop_ghz: float = 8.0
    points: int = 121
    plan_type: str = "Adaptive"
    max_passes: int = 8

    def to_dict(self) -> dict[str, object]:
        return {
            "start_ghz": self.start_ghz,
            "stop_ghz": self.stop_ghz,
            "passband_start_ghz": self.passband_start_ghz,
            "passband_stop_ghz": self.passband_stop_ghz,
            "points": self.points,
            "plan_type": self.plan_type,
            "max_passes": self.max_passes,
        }


@dataclass(frozen=True)
class PipelineScoringConfig:
    script: Path | None = None
    target_profile: str = "fr4_25db_rl6"
    score_version: str = "fr4_i7_score_v1"
    source: str = "rfpro-csv"

    def to_dict(self) -> dict[str, object]:
        return {
            "script": str(self.script) if self.script is not None else None,
            "target_profile": self.target_profile,
            "score_version": self.score_version,
            "source": self.source,
        }


@dataclass(frozen=True)
class PipelineConfig:
    schema_version: str
    pipeline_id: str
    project_id: str
    sweep_id: str | None = None
    device_id: str = "filter.interdigital"
    profile_id: str | None = None
    units: str = "mm"
    layout: PipelineLayoutConfig = field(default_factory=PipelineLayoutConfig)
    ads: PipelineAdsConfig = field(default_factory=PipelineAdsConfig)
    layer_map: PipelineLayerConfig = field(default_factory=PipelineLayerConfig)
    ports: PipelinePortConfig = field(default_factory=PipelinePortConfig)
    frequency: PipelineFrequencyConfig = field(default_factory=PipelineFrequencyConfig)
    scoring: PipelineScoringConfig = field(default_factory=PipelineScoringConfig)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "pipeline_id": self.pipeline_id,
            "project_id": self.project_id,
            "sweep_id": self.sweep_id,
            "device_id": self.device_id,
            "profile_id": self.profile_id,
            "units": self.units,
            "layout": self.layout.to_dict(),
            "ads": self.ads.to_dict(),
            "layer_map": self.layer_map.to_dict(),
            "ports": self.ports.to_dict(),
            "frequency": self.frequency.to_dict(),
            "scoring": self.scoring.to_dict(),
        }


def default_pipelines_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "config" / "pipelines"


def default_pipeline_config_path(pipeline_id: str, root: Path | None = None) -> Path:
    return default_pipelines_dir(root) / f"{pipeline_id}.json"


def _optional_root_relative_path(root: Path, value: Any) -> Path | None:
    if value in (None, ""):
        return None
    return root_relative_path(root, Path(str(value)))


def _optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


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


def pipeline_from_mapping(data: dict[str, Any], *, root: Path | None = None) -> PipelineConfig:
    base = root or repo_root()
    layout_data = data.get("layout") if isinstance(data.get("layout"), dict) else {}
    ads_data = data.get("ads") if isinstance(data.get("ads"), dict) else {}
    layer_data = data.get("layer_map") if isinstance(data.get("layer_map"), dict) else {}
    port_data = data.get("ports") if isinstance(data.get("ports"), dict) else {}
    frequency_data = data.get("frequency") if isinstance(data.get("frequency"), dict) else {}
    scoring_data = data.get("scoring") if isinstance(data.get("scoring"), dict) else {}

    return PipelineConfig(
        schema_version=str(data.get("schema_version", "0.1.0")),
        pipeline_id=str(data["pipeline_id"]),
        project_id=str(data["project_id"]),
        sweep_id=_optional_str(data.get("sweep_id")),
        device_id=str(data.get("device_id", "filter.interdigital")),
        profile_id=_optional_str(data.get("profile_id")),
        units=str(data.get("units", "mm")),
        layout=PipelineLayoutConfig(
            sweep_script=_optional_root_relative_path(base, layout_data.get("sweep_script")),
            layout_generator_script=_optional_root_relative_path(base, layout_data.get("layout_generator_script")),
            layout_output_dir=_optional_root_relative_path(base, layout_data.get("layout_output_dir")),
            params_output_dir=_optional_root_relative_path(base, layout_data.get("params_output_dir")),
            require_layout_json=bool(layout_data.get("require_layout_json", True)),
            require_params_json=bool(layout_data.get("require_params_json", True)),
        ),
        ads=PipelineAdsConfig(
            import_script=_optional_root_relative_path(base, ads_data.get("import_script")),
            clone_setup_script=_optional_root_relative_path(base, ads_data.get("clone_setup_script")),
            rfpro_script=_optional_root_relative_path(base, ads_data.get("rfpro_script")),
            dataset_export_script=_optional_root_relative_path(base, ads_data.get("dataset_export_script")),
            template_cell=_optional_str(ads_data.get("template_cell")),
            setup_view=_optional_str(ads_data.get("setup_view")),
            rfpro_emsetup_view=_optional_str(ads_data.get("rfpro_emsetup_view")),
            workspace_profile=_optional_str(ads_data.get("workspace_profile")),
        ),
        layer_map=PipelineLayerConfig(
            metal_layer=_optional_str(layer_data.get("metal_layer")) or "cond",
            via_layer=_optional_str(layer_data.get("via_layer")) or "pcvia1",
            boundary_layer=_optional_str(layer_data.get("boundary_layer")) or "EM_BOUNDARY",
            layer_map_version=_optional_str(layer_data.get("layer_map_version")) or "profile-default-v1",
            layer_map_strategy=_optional_str(layer_data.get("layer_map_strategy")) or "profile-default",
            layer_map_required=bool(layer_data.get("layer_map_required", False)),
        ),
        ports=PipelinePortConfig(
            names=tuple(str(item) for item in port_data.get("names", ("P1", "P2"))),
            location_source=_optional_str(port_data.get("location_source")) or "params_json",
            unit=_optional_str(port_data.get("unit")) or "mm",
            pad_layer=_optional_str(port_data.get("pad_layer")) or "cond",
            reference=_optional_str(port_data.get("reference")) or "ground",
        ),
        frequency=PipelineFrequencyConfig(
            start_ghz=float(frequency_data.get("start_ghz", 4.0)),
            stop_ghz=float(frequency_data.get("stop_ghz", 10.0)),
            passband_start_ghz=float(frequency_data.get("passband_start_ghz", 6.0)),
            passband_stop_ghz=float(frequency_data.get("passband_stop_ghz", 8.0)),
            points=int(frequency_data.get("points", 121)),
            plan_type=_optional_str(frequency_data.get("plan_type")) or "Adaptive",
            max_passes=int(frequency_data.get("max_passes", 8)),
        ),
        scoring=PipelineScoringConfig(
            script=_optional_root_relative_path(base, scoring_data.get("script")),
            target_profile=_optional_str(scoring_data.get("target_profile")) or "fr4_25db_rl6",
            score_version=_optional_str(scoring_data.get("score_version"))
            or TARGET_SCORE_VERSIONS.get(_optional_str(scoring_data.get("target_profile")) or "fr4_25db_rl6", "fr4_i7_score_v1"),
            source=_optional_str(scoring_data.get("source")) or "rfpro-csv",
        ),
    )


def load_pipeline_data(pipeline_id: str, *, root: Path | None = None, path: Path | None = None) -> dict[str, Any]:
    config_path = path or default_pipeline_config_path(pipeline_id, root)
    if not config_path.exists():
        raise FileNotFoundError(f"pipeline config not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"pipeline config must be a JSON object: {config_path}")
    return data


def load_pipeline(pipeline_id: str, *, root: Path | None = None, path: Path | None = None) -> PipelineConfig:
    return pipeline_from_mapping(load_pipeline_data(pipeline_id, root=root, path=path), root=root)


def resolve_pipeline_id(
    project: ProjectConfig | None = None,
    sweep: SweepConfig | None = None,
    override: str | None = None,
) -> str | None:
    if override:
        return override
    if sweep and sweep.pipeline_id:
        return sweep.pipeline_id
    if project and project.pipeline_id:
        return project.pipeline_id
    return None


def validate_pipeline(
    pipeline: PipelineConfig,
    *,
    project: ProjectConfig | None = None,
    profile: AdsProfile | None = None,
) -> list[PipelineCheck]:
    checks: list[PipelineCheck] = []

    def add(name: str, ok: bool, message: str, path: Path | None = None) -> None:
        checks.append(PipelineCheck(name, path, ok, message))

    repo = repo_root()
    add("schema_version", pipeline.schema_version == "0.1.0", "pipeline schema version should stay at 0.1.0")
    add("units", pipeline.units == "mm", "pipeline units must be mm")
    add("ports.unit", pipeline.ports.unit == "mm", "port units must be mm")
    add("ports.names", tuple(pipeline.ports.names) == ("P1", "P2"), "ports must be P1/P2")
    add("frequency.start_ghz", pipeline.frequency.start_ghz > 0.0, "start frequency must be positive")
    add(
        "frequency.stop_ghz",
        pipeline.frequency.stop_ghz > pipeline.frequency.start_ghz,
        "stop frequency must be greater than start frequency",
    )
    add(
        "frequency.passband",
        pipeline.frequency.start_ghz <= pipeline.frequency.passband_start_ghz
        < pipeline.frequency.passband_stop_ghz
        <= pipeline.frequency.stop_ghz,
        "passband must be inside the sweep frequency range",
    )
    add("frequency.points", pipeline.frequency.points >= 2, "frequency points must be at least 2")
    add(
        "frequency.plan_type",
        pipeline.frequency.plan_type in {"Adaptive", "Linear"},
        "frequency plan type must be Adaptive or Linear",
    )
    add("frequency.max_passes", pipeline.frequency.max_passes >= 0, "max passes must be non-negative")
    add("ads.template_cell", bool(pipeline.ads.template_cell), "template cell must be set by the pipeline/profile")
    add("ads.setup_view", pipeline.ads.setup_view == "em%Setup", "setup view must stay em%Setup")
    add("ads.rfpro_emsetup_view", pipeline.ads.rfpro_emsetup_view == "emSetup", "RFPro EM setup view must stay emSetup")
    add("layer_map.metal_layer", pipeline.layer_map.metal_layer == "cond", "metal layer must stay cond")
    add("layer_map.via_layer", pipeline.layer_map.via_layer == "pcvia1", "via layer must stay pcvia1")
    add("layer_map.boundary_layer", pipeline.layer_map.boundary_layer == "EM_BOUNDARY", "boundary layer must stay EM_BOUNDARY")
    add("layer_map.version", bool(pipeline.layer_map.layer_map_version), "layer map version must be set")
    add("scoring.target_profile", pipeline.scoring.target_profile in TARGET_PROFILES, "target profile must be known")
    expected_score_version = TARGET_SCORE_VERSIONS.get(pipeline.scoring.target_profile)
    add("scoring.score_version", pipeline.scoring.score_version == expected_score_version, "score version must match target profile")
    try:
        get_device(pipeline.device_id)
        add("device_id", True, f"device registered: {pipeline.device_id}")
    except Exception as exc:
        add("device_id", False, str(exc))

    if project is not None:
        add("project_id", pipeline.project_id == project.project_id, "pipeline project must match project config")
        if project.target_profile:
            add("project.target_profile", pipeline.scoring.target_profile == project.target_profile, "pipeline target profile must match project target profile")
        if project.pipeline_id:
            registered_pipeline_ids = {sweep.pipeline_id for sweep in project.sweeps.values() if sweep.pipeline_id}
            add(
                "project.pipeline_id",
                pipeline.pipeline_id == project.pipeline_id or pipeline.pipeline_id in registered_pipeline_ids,
                "pipeline id must match project default or a registered sweep",
            )
        sweep: SweepConfig | None = None
        if pipeline.sweep_id and pipeline.sweep_id in project.sweeps:
            sweep = project.sweeps[pipeline.sweep_id]
            add("sweep_id", True, "pipeline sweep is registered in project config")
        elif pipeline.sweep_id:
            add("sweep_id", False, "pipeline sweep must be registered in project config")
        elif project.active_sweep:
            sweep = project.get_sweep()
        if sweep is not None:
            if sweep and sweep.pipeline_id:
                add("sweep.pipeline_id", pipeline.pipeline_id == sweep.pipeline_id, "pipeline id must match active sweep")
            if sweep:
                if sweep.template_cell:
                    add("sweep.template_cell", pipeline.ads.template_cell == sweep.template_cell, "pipeline template cell must match active sweep")
                if sweep.setup_view:
                    add("sweep.setup_view", pipeline.ads.setup_view == sweep.setup_view, "pipeline setup view must match active sweep")
                if sweep.rfpro_emsetup_view:
                    add("sweep.rfpro_emsetup_view", pipeline.ads.rfpro_emsetup_view == sweep.rfpro_emsetup_view, "pipeline RFPro EM setup view must match active sweep")

    if profile is not None:
        add("profile_id", pipeline.profile_id in (None, profile.name), "pipeline profile id must match loaded profile")
        add("profile.template_cell", pipeline.ads.template_cell == profile.template_cell, "pipeline template cell must match ADS profile")
        add("profile.setup_view", pipeline.ads.setup_view == profile.setup_view, "pipeline setup view must match ADS profile")
        add("profile.rfpro_emsetup_view", pipeline.ads.rfpro_emsetup_view == profile.rfpro_emsetup_view, "pipeline RFPro EM setup view must match ADS profile")

    path_checks = [
        ("layout.sweep_script", pipeline.layout.sweep_script),
        ("layout.layout_generator_script", pipeline.layout.layout_generator_script),
        ("ads.import_script", pipeline.ads.import_script),
        ("ads.clone_setup_script", pipeline.ads.clone_setup_script),
        ("ads.rfpro_script", pipeline.ads.rfpro_script),
        ("ads.dataset_export_script", pipeline.ads.dataset_export_script),
        ("scoring.script", pipeline.scoring.script),
    ]
    for name, path in path_checks:
        if path is None:
            add(name, False, "missing path")
            continue
        resolved = path if path.is_absolute() else repo / path
        add(name, resolved.exists(), "path must exist", resolved)

    if pipeline.layout.layout_output_dir is not None:
        resolved = pipeline.layout.layout_output_dir if pipeline.layout.layout_output_dir.is_absolute() else repo / pipeline.layout.layout_output_dir
        add("layout.layout_output_dir", resolved.exists(), "layout output dir must exist", resolved)
    if pipeline.layout.params_output_dir is not None:
        resolved = pipeline.layout.params_output_dir if pipeline.layout.params_output_dir.is_absolute() else repo / pipeline.layout.params_output_dir
        add("layout.params_output_dir", resolved.exists(), "params output dir must exist", resolved)

    return checks
