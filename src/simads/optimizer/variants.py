"""Deterministic candidate variant helpers.

The optimizer package handles learned candidate proposal. This module covers
the other common path: engineering-rule variants expressed as data.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


INDEXED_FIELD_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\[(?P<index>-?\d+)\]$")


@dataclass(frozen=True)
class DeterministicVariantConfig:
    schema_version: str
    strategy: str
    project_id: str
    device_id: str
    seeds: dict[str, Path]
    output_fields: list[str]
    field_sources: dict[str, str]
    variants: list[dict[str, Any]]
    plan: Path | None = None


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return data


def resolve_root_relative(root: Path, value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def load_variant_config(path: Path, root: Path) -> DeterministicVariantConfig:
    data = load_json(path)
    seeds_raw = data.get("seeds")
    output_fields = data.get("output_fields")
    field_sources = data.get("field_sources")
    variants = data.get("variants")

    if not isinstance(seeds_raw, dict) or not seeds_raw:
        raise ValueError("seeds must be a non-empty object")
    if not isinstance(output_fields, list) or not all(isinstance(item, str) for item in output_fields):
        raise ValueError("output_fields must be a list of strings")
    if not isinstance(field_sources, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in field_sources.items()):
        raise ValueError("field_sources must be an object mapping output field to parameter source")
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants must be a non-empty list")

    seeds: dict[str, Path] = {}
    for key, value in seeds_raw.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("seeds must map string names to string paths")
        resolved = resolve_root_relative(root, value)
        assert resolved is not None
        seeds[key] = resolved

    missing_sources = [field for field in output_fields if field not in field_sources and field not in {"name", "notes"}]
    if missing_sources:
        raise ValueError(f"missing field_sources for: {', '.join(missing_sources)}")

    plan = resolve_root_relative(root, data.get("plan")) if isinstance(data.get("plan"), str) else None
    return DeterministicVariantConfig(
        schema_version=str(data.get("schema_version", "")),
        strategy=str(data.get("strategy", "")),
        project_id=str(data.get("project_id", "")),
        device_id=str(data.get("device_id", "")),
        seeds=seeds,
        output_fields=list(output_fields),
        field_sources=dict(field_sources),
        variants=list(variants),
        plan=plan,
    )


def load_seed_parameters(path: Path) -> dict[str, Any]:
    data = load_json(path)
    params = data.get("parameters")
    if not isinstance(params, dict):
        raise ValueError(f"{path}: missing object field 'parameters'")
    return dict(params)


def get_indexed_value(params: dict[str, Any], source: str) -> Any:
    match = INDEXED_FIELD_RE.match(source)
    if not match:
        return params[source]
    values = params[match.group("name")]
    if not isinstance(values, list):
        values = list(values)
    return values[int(match.group("index"))]


def apply_updates(params: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    updated = dict(params)
    for key, value in updates.items():
        match = INDEXED_FIELD_RE.match(key)
        if not match:
            updated[key] = value
            continue
        name = match.group("name")
        values = list(updated[name])
        values[int(match.group("index"))] = value
        updated[name] = values
    return updated


def format_plan_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def validate_config(config: DeterministicVariantConfig) -> list[str]:
    errors: list[str] = []
    if config.strategy != "deterministic_variants":
        errors.append("strategy must be deterministic_variants")
    if not config.schema_version:
        errors.append("schema_version is required")
    if not config.project_id:
        errors.append("project_id is required")
    if not config.device_id:
        errors.append("device_id is required")

    for seed_name, seed_path in config.seeds.items():
        if not seed_path.is_file():
            errors.append(f"seed file does not exist: {seed_name} -> {seed_path}")

    seen_names: set[str] = set()
    for index, variant in enumerate(config.variants):
        if not isinstance(variant, dict):
            errors.append(f"variants[{index}] must be an object")
            continue
        name = variant.get("name")
        seed = variant.get("seed")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"variants[{index}].name must be a non-empty string")
        elif name in seen_names:
            errors.append(f"variants[{index}].name is duplicated: {name}")
        else:
            seen_names.add(name)
        if seed not in config.seeds:
            errors.append(f"variants[{index}].seed references unknown seed: {seed}")
        updates = variant.get("updates", {})
        if not isinstance(updates, dict):
            errors.append(f"variants[{index}].updates must be an object")

    return errors


def build_plan_rows(config: DeterministicVariantConfig) -> list[dict[str, str]]:
    seed_params = {name: load_seed_parameters(path) for name, path in config.seeds.items()}
    rows: list[dict[str, str]] = []

    for variant in config.variants:
        seed_name = str(variant["seed"])
        params = apply_updates(seed_params[seed_name], variant.get("updates", {}))
        params["name"] = variant["name"]
        row: dict[str, str] = {}
        for field in config.output_fields:
            if field == "name":
                row[field] = str(variant["name"])
            elif field == "notes":
                row[field] = str(variant.get("notes", ""))
            else:
                row[field] = format_plan_value(get_indexed_value(params, config.field_sources[field]))
        rows.append(row)
    return rows


def write_plan(path: Path, fieldnames: Iterable[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
