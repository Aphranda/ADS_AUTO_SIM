"""ADS installation and workspace profiles.

This module is the stable configuration entry for ADS automation. The legacy
``tools/ads_profiles.py`` file re-exports this API so existing scripts keep
working while the project moves toward ``src/simads``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class ProfileCheck:
    name: str
    path: Path | None
    ok: bool
    message: str


@dataclass(frozen=True)
class AdsProfile:
    name: str
    ads_root: Path
    workspace: Path
    library: str
    template_cell: str
    ads_python_path: Path | None = None
    setup_view: str = "em%Setup"
    rfpro_emsetup_view: str = "emSetup"
    substrate: str | None = None
    substrate_library: str | None = None
    automation_python: Path | None = None

    @property
    def ads_python(self) -> Path:
        return self.ads_python_path or self.ads_root / "tools" / "python" / "python.exe"

    @property
    def host_python(self) -> Path:
        return self.automation_python or Path(sys.executable)

    @property
    def layer_map(self) -> Path:
        return self.workspace / "setup_dxf.opt"

    @property
    def library_path(self) -> Path:
        return self.workspace / self.library

    @staticmethod
    def ads_encoded_cell_name(cell_name: str) -> str:
        return "".join(f"%{char}" if char.isupper() else char for char in cell_name)

    @property
    def template_cell_path(self) -> Path:
        direct = self.library_path / self.template_cell
        if direct.exists():
            return direct
        encoded = self.library_path / self.ads_encoded_cell_name(self.template_cell)
        return encoded if encoded.exists() else direct

    def to_dict(self) -> dict[str, str | None]:
        return {
            "profile_id": self.name,
            "ads_root": str(self.ads_root),
            "ads_python": str(self.ads_python),
            "host_python": str(self.host_python),
            "workspace": str(self.workspace),
            "library": self.library,
            "template_cell": self.template_cell,
            "setup_view": self.setup_view,
            "rfpro_emsetup_view": self.rfpro_emsetup_view,
            "substrate": self.substrate,
            "substrate_library": self.substrate_library,
            "layer_map": str(self.layer_map),
        }


DEFAULT_PROFILE_DATA = {
    "schema_version": "0.1.0",
    "profiles": {
        "company": {
            "ads_root": r"D:\Hardware\Keysight\ADS2026_Update1",
            "ads_python": r"D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe",
            "host_python": r"D:\Microsoft\Python\ads-automation\Scripts\python.exe",
            "workspace": r"D:\Work\ADS\6-8G_Fillter\6-8G_Fillter",
            "library": "6-8G_Fillter_lib",
            "template_cell": "interdigital_9o_ro4350b_508um_v3_wide_mm_coords",
            "setup_view": "em%Setup",
            "rfpro_emsetup_view": "emSetup",
            "substrate": "6-8G_Fillter_lib:substrate1",
        },
        "home": {
            "ads_root": r"D:\Hardware\Keysight\ADS2026_Update1",
            "ads_python": r"D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe",
            "host_python": r"D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe",
            "workspace": r"D:\Work\ADS\BFP\BFP",
            "library": "BFP_lib",
            "template_cell": "BFP",
            "setup_view": "em%Setup",
            "rfpro_emsetup_view": "emSetup",
            "substrate": "BFP_lib:substrate4",
        },
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_config_path() -> Path:
    return repo_root() / "config" / "ads_profiles.json"


def _optional_path(value: object) -> Path | None:
    if value in (None, ""):
        return None
    return Path(str(value))


def _substrate_library(substrate: str | None, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if substrate and ":" in substrate:
        return substrate.split(":", 1)[0]
    return None


def profile_from_mapping(name: str, data: dict[str, object]) -> AdsProfile:
    substrate = str(data["substrate"]) if data.get("substrate") else None
    substrate_library = _substrate_library(substrate, str(data["substrate_library"]) if data.get("substrate_library") else None)
    return AdsProfile(
        name=name,
        ads_root=Path(str(data["ads_root"])),
        ads_python_path=_optional_path(data.get("ads_python")),
        workspace=Path(str(data["workspace"])),
        library=str(data["library"]),
        template_cell=str(data["template_cell"]),
        setup_view=str(data.get("setup_view", "em%Setup")),
        rfpro_emsetup_view=str(data.get("rfpro_emsetup_view", "emSetup")),
        substrate=substrate,
        substrate_library=substrate_library,
        automation_python=_optional_path(data.get("host_python")),
    )


def load_profile_data(path: Path | None = None) -> dict[str, object]:
    config_path = path or default_config_path()
    if not config_path.exists():
        return DEFAULT_PROFILE_DATA
    return json.loads(config_path.read_text(encoding="utf-8-sig"))


def load_profiles(path: Path | None = None) -> dict[str, AdsProfile]:
    data = load_profile_data(path)
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("ads profile config must contain a profiles object")
    return {str(name): profile_from_mapping(str(name), mapping) for name, mapping in profiles.items()}


ADS_PROFILES = load_profiles()


def profile_names() -> list[str]:
    return sorted(ADS_PROFILES)


def get_ads_profile(name: str) -> AdsProfile:
    try:
        return ADS_PROFILES[name]
    except KeyError as exc:
        names = ", ".join(profile_names())
        raise ValueError(f"unknown ADS profile {name!r}; expected one of: {names}") from exc


def resolve_ads_python(profile_name: str, override: Path | None) -> Path:
    return override if override is not None else get_ads_profile(profile_name).ads_python


def resolve_host_python(profile_name: str, override: Path | None = None) -> Path:
    return override if override is not None else get_ads_profile(profile_name).host_python


def resolve_workspace(profile_name: str, override: Path | None) -> Path:
    return override if override is not None else get_ads_profile(profile_name).workspace


def resolve_library(profile_name: str, override: str | None) -> str:
    return override if override is not None else get_ads_profile(profile_name).library


def resolve_substrate_library(profile_name: str, override: str | None = None) -> str | None:
    return override if override is not None else get_ads_profile(profile_name).substrate_library


def resolve_substrate(profile_name: str, override: str | None = None) -> str | None:
    return override if override is not None else get_ads_profile(profile_name).substrate


def resolve_layer_map(profile_name: str, workspace: Path, override: Path | None) -> Path:
    return override if override is not None else workspace / get_ads_profile(profile_name).layer_map.name


def validate_profile(profile: AdsProfile, *, require_template: bool = False) -> list[ProfileCheck]:
    checks = [
        ProfileCheck("ads_root", profile.ads_root, profile.ads_root.exists(), "ADS installation root"),
        ProfileCheck("ads_python", profile.ads_python, profile.ads_python.exists(), "ADS Python executable"),
        ProfileCheck("host_python", profile.host_python, profile.host_python.exists(), "host automation Python"),
        ProfileCheck("workspace", profile.workspace, profile.workspace.exists(), "ADS workspace path"),
        ProfileCheck("library", profile.library_path, profile.library_path.exists(), "ADS library directory"),
        ProfileCheck("layer_map", profile.layer_map, profile.layer_map.exists(), "DXF layer map"),
    ]
    if require_template:
        checks.append(
            ProfileCheck(
                "template_cell",
                profile.template_cell_path,
                profile.template_cell_path.exists(),
                "ADS template cell directory",
            )
        )
    return checks
