"""Machine profile detection from local network adapter fingerprints."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid
from typing import Any

from .profiles import repo_root


MAC_RE = re.compile(r"(?:[0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}")
VIRTUAL_ADAPTER_HINTS = (
    "bluetooth",
    "hyper-v",
    "loopback",
    "pseudo",
    "tap",
    "teredo",
    "virtual",
    "vmware",
    "vpn",
    "wintun",
)


@dataclass(frozen=True)
class MachineProfile:
    name: str
    description: str | None
    mac_sha256_16: tuple[str, ...]
    ads_profile: str | None = None
    hfss_profile: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "mac_sha256_16": list(self.mac_sha256_16),
            "ads_profile": self.ads_profile,
            "hfss_profile": self.hfss_profile,
        }


@dataclass(frozen=True)
class MachineDetection:
    selected: str | None
    source: str
    mac_sha256_16: tuple[str, ...]
    candidates: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "selected": self.selected,
            "source": self.source,
            "mac_sha256_16": list(self.mac_sha256_16),
            "candidates": list(self.candidates),
        }


def default_machine_config_path() -> Path:
    return repo_root() / "config" / "machine_profiles.json"


def normalize_mac(value: str) -> str:
    normalized = "".join(ch for ch in value if ch.isalnum()).lower()
    if len(normalized) != 12:
        raise ValueError(f"invalid MAC address: {value!r}")
    return normalized


def mac_hash(value: str) -> str:
    return hashlib.sha256(normalize_mac(value).encode("ascii")).hexdigest()[:16]


def _non_virtual_adapter(line: str) -> bool:
    lowered = line.lower()
    return not any(hint in lowered for hint in VIRTUAL_ADAPTER_HINTS)


def _macs_from_getmac() -> list[str]:
    try:
        completed = subprocess.run(
            ["getmac", "/fo", "csv", "/v", "/nh"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return []
    output: list[str] = []
    for line in completed.stdout.splitlines():
        if not _non_virtual_adapter(line):
            continue
        output.extend(match.group(0) for match in MAC_RE.finditer(line))
    return output


def local_mac_hashes() -> tuple[str, ...]:
    macs = _macs_from_getmac()
    node = uuid.getnode()
    if (node >> 40) % 2 == 0:
        macs.append(":".join(f"{(node >> shift) & 0xFF:02x}" for shift in range(40, -1, -8)))
    seen: set[str] = set()
    hashes: list[str] = []
    for item in macs:
        try:
            digest = mac_hash(item)
        except ValueError:
            continue
        if digest not in seen:
            seen.add(digest)
            hashes.append(digest)
    return tuple(hashes)


def machine_profile_from_mapping(name: str, data: dict[str, Any]) -> MachineProfile:
    hashes = tuple(str(item).lower() for item in data.get("mac_sha256_16", []) if str(item).strip())
    return MachineProfile(
        name=name,
        description=str(data["description"]) if data.get("description") else None,
        mac_sha256_16=hashes,
        ads_profile=str(data["ads_profile"]) if data.get("ads_profile") else None,
        hfss_profile=str(data["hfss_profile"]) if data.get("hfss_profile") else None,
    )


def load_machine_profile_data(path: Path | None = None) -> dict[str, Any]:
    config_path = path or default_machine_config_path()
    if not config_path.exists():
        return {"schema_version": "0.1.0", "profiles": {}}
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"machine profile config must be a JSON object: {config_path}")
    return data


def load_machine_profiles(path: Path | None = None) -> dict[str, MachineProfile]:
    profiles = load_machine_profile_data(path).get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("machine profile config must contain a profiles object")
    return {str(name): machine_profile_from_mapping(str(name), mapping) for name, mapping in profiles.items()}


def machine_profile_names(path: Path | None = None) -> list[str]:
    return sorted(load_machine_profiles(path))


def detect_machine_profile(path: Path | None = None) -> MachineDetection:
    override = os.environ.get("SIMADS_MACHINE_PROFILE")
    profiles = load_machine_profiles(path)
    if override:
        return MachineDetection(
            selected=override if override in profiles else None,
            source="SIMADS_MACHINE_PROFILE",
            mac_sha256_16=local_mac_hashes(),
            candidates=tuple(profiles),
        )
    local_hashes = local_mac_hashes()
    local_set = set(local_hashes)
    matches = [name for name, profile in profiles.items() if local_set.intersection(profile.mac_sha256_16)]
    selected = matches[0] if len(matches) == 1 else None
    source = "mac_sha256_16" if selected else ("ambiguous_mac_sha256_16" if matches else "unmatched_mac_sha256_16")
    return MachineDetection(selected=selected, source=source, mac_sha256_16=local_hashes, candidates=tuple(matches or profiles))


def resolve_machine_profile(name: str | None = None, *, path: Path | None = None) -> str:
    if name and name != "auto":
        return name
    detection = detect_machine_profile(path)
    if detection.selected:
        return detection.selected
    candidates = ", ".join(detection.candidates)
    hashes = ", ".join(detection.mac_sha256_16)
    raise ValueError(f"unable to auto-detect machine profile; candidates={candidates}; local_mac_sha256_16={hashes}")


def resolve_backend_profile(backend: str, name: str | None = None, *, path: Path | None = None) -> str:
    if name and name != "auto":
        return name
    machine_name = resolve_machine_profile(name, path=path)
    profile = load_machine_profiles(path)[machine_name]
    if backend == "ads" and profile.ads_profile:
        return profile.ads_profile
    if backend == "hfss" and profile.hfss_profile:
        return profile.hfss_profile
    return machine_name


__all__ = [
    "MachineDetection",
    "MachineProfile",
    "default_machine_config_path",
    "detect_machine_profile",
    "load_machine_profile_data",
    "load_machine_profiles",
    "local_mac_hashes",
    "mac_hash",
    "machine_profile_names",
    "normalize_mac",
    "resolve_backend_profile",
    "resolve_machine_profile",
]
