"""HFSS/AEDT installation and workspace profiles."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any

from .machine import resolve_backend_profile
from .profiles import ProfileCheck, repo_root
from .projects import root_relative_path


@dataclass(frozen=True)
class HfssProfile:
    name: str
    ansys_root: Path
    ansysedt: Path
    workspace_dir: Path
    version: str = "2026.1"
    host_python_path: Path | None = None
    route: str = "reliable"
    stackup_config: Path | None = None
    non_graphical: bool = True

    @property
    def host_python(self) -> Path:
        return self.host_python_path or Path(sys.executable)

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.name,
            "ansys_root": str(self.ansys_root),
            "ansysedt": str(self.ansysedt),
            "host_python": str(self.host_python),
            "workspace_dir": str(self.workspace_dir),
            "version": self.version,
            "route": self.route,
            "stackup_config": str(self.stackup_config) if self.stackup_config is not None else None,
            "non_graphical": self.non_graphical,
        }


def default_hfss_config_path() -> Path:
    return repo_root() / "config" / "hfss_profiles.json"


def _optional_path(value: object) -> Path | None:
    if value in (None, ""):
        return None
    return Path(str(value))


def hfss_profile_from_mapping(name: str, data: dict[str, Any], *, root: Path | None = None) -> HfssProfile:
    base = root or repo_root()
    stackup = _optional_path(data.get("stackup_config"))
    return HfssProfile(
        name=name,
        ansys_root=Path(str(data["ansys_root"])),
        ansysedt=Path(str(data["ansysedt"])),
        host_python_path=_optional_path(data.get("host_python")),
        workspace_dir=Path(str(data["workspace_dir"])),
        version=str(data.get("version", "2026.1")),
        route=str(data.get("route", "reliable")),
        stackup_config=root_relative_path(base, stackup) if stackup is not None else None,
        non_graphical=bool(data.get("non_graphical", True)),
    )


def load_hfss_profile_data(path: Path | None = None) -> dict[str, Any]:
    config_path = path or default_hfss_config_path()
    if not config_path.exists():
        return {"schema_version": "0.1.0", "profiles": {}}
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"HFSS profile config must be a JSON object: {config_path}")
    return data


def load_hfss_profiles(path: Path | None = None) -> dict[str, HfssProfile]:
    data = load_hfss_profile_data(path)
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("HFSS profile config must contain a profiles object")
    return {str(name): hfss_profile_from_mapping(str(name), mapping) for name, mapping in profiles.items()}


def hfss_profile_names(path: Path | None = None, *, include_auto: bool = False) -> list[str]:
    names = sorted(load_hfss_profiles(path))
    return ["auto", *names] if include_auto else names


def get_hfss_profile(name: str) -> HfssProfile:
    resolved = resolve_backend_profile("hfss", name) if name == "auto" else name
    profiles = load_hfss_profiles()
    try:
        return profiles[resolved]
    except KeyError as exc:
        names = ", ".join(hfss_profile_names(include_auto=True))
        raise ValueError(f"unknown HFSS profile {name!r}; expected one of: {names}") from exc


def validate_hfss_profile(profile: HfssProfile) -> list[ProfileCheck]:
    checks = [
        ProfileCheck("ansys_root", profile.ansys_root, profile.ansys_root.exists(), "ANSYS installation root"),
        ProfileCheck("ansysedt", profile.ansysedt, profile.ansysedt.exists(), "AEDT executable"),
        ProfileCheck("host_python", profile.host_python, profile.host_python.exists(), "host pyAEDT Python"),
        ProfileCheck("workspace_dir", profile.workspace_dir, profile.workspace_dir.exists(), "HFSS workspace directory"),
    ]
    if profile.stackup_config is not None:
        checks.append(ProfileCheck("stackup_config", profile.stackup_config, profile.stackup_config.exists(), "PCB stackup config"))
    return checks


__all__ = [
    "HfssProfile",
    "default_hfss_config_path",
    "get_hfss_profile",
    "hfss_profile_from_mapping",
    "hfss_profile_names",
    "load_hfss_profile_data",
    "load_hfss_profiles",
    "validate_hfss_profile",
]
