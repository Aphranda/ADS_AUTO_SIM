"""Generic layout element selection helpers."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class LayoutElementPolicy:
    include_roles: tuple[str, ...] = ()
    include_names: tuple[str, ...] = ()
    include_prefixes: tuple[str, ...] = ()
    include_kinds: tuple[str, ...] = ()
    include_layers: tuple[str, ...] = ()
    include_regions: tuple[str, ...] = ()
    include_bbox_mm: tuple[float, float, float, float] | None = None
    exclude_roles: tuple[str, ...] = ()
    exclude_names: tuple[str, ...] = ()
    exclude_prefixes: tuple[str, ...] = ()
    exclude_kinds: tuple[str, ...] = ()
    exclude_layers: tuple[str, ...] = ()
    suppress_default_reference_ground_plane: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "LayoutElementPolicy":
        mapping = dict(data or {})
        include = mapping.get("include", {})
        exclude = mapping.get("exclude", {})
        draw = mapping.get("draw", {})
        regions = mapping.get("regions", [])
        if isinstance(regions, str):
            regions = [regions]
        bbox = include.get("bbox_mm", mapping.get("include_bbox_mm"))
        include_bbox_mm = None
        if isinstance(bbox, list) and len(bbox) >= 4:
            include_bbox_mm = tuple(float(value) for value in bbox[:4])
        return cls(
            include_roles=tuple(str(item) for item in _as_list(include.get("roles"))),
            include_names=tuple(str(item) for item in _as_list(include.get("names"))),
            include_prefixes=tuple(str(item) for item in _as_list(include.get("prefixes"))),
            include_kinds=tuple(str(item) for item in _as_list(include.get("kinds"))),
            include_layers=tuple(str(item) for item in _as_list(include.get("layers"))),
            include_regions=tuple(str(item) for item in _as_list(include.get("regions", regions))),
            include_bbox_mm=include_bbox_mm,
            exclude_roles=tuple(str(item) for item in _as_list(exclude.get("roles"))),
            exclude_names=tuple(str(item) for item in _as_list(exclude.get("names"))),
            exclude_prefixes=tuple(str(item) for item in _as_list(exclude.get("prefixes"))),
            exclude_kinds=tuple(str(item) for item in _as_list(exclude.get("kinds"))),
            exclude_layers=tuple(str(item) for item in _as_list(exclude.get("layers"))),
            suppress_default_reference_ground_plane=bool(
                isinstance(draw, dict) and draw.get("suppress_default_reference_ground_plane")
            ),
            metadata=deepcopy(mapping.get("metadata")) if isinstance(mapping.get("metadata"), dict) else {},
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "include": {
                "roles": list(self.include_roles),
                "names": list(self.include_names),
                "prefixes": list(self.include_prefixes),
                "kinds": list(self.include_kinds),
                "layers": list(self.include_layers),
                "regions": list(self.include_regions),
                "bbox_mm": list(self.include_bbox_mm) if self.include_bbox_mm is not None else None,
            },
            "exclude": {
                "roles": list(self.exclude_roles),
                "names": list(self.exclude_names),
                "prefixes": list(self.exclude_prefixes),
                "kinds": list(self.exclude_kinds),
                "layers": list(self.exclude_layers),
            },
            "draw": {
                "suppress_default_reference_ground_plane": self.suppress_default_reference_ground_plane,
            },
            "metadata": deepcopy(self.metadata),
        }


def load_layout_element_policy(path: Path) -> LayoutElementPolicy:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"layout element policy must be a JSON object: {path}")
    return LayoutElementPolicy.from_mapping(data)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _metadata(shape: dict[str, Any]) -> dict[str, Any]:
    metadata = shape.get("metadata")
    return dict(metadata) if isinstance(metadata, dict) else {}


def _shape_bbox(shape: dict[str, Any]) -> tuple[float, float, float, float] | None:
    if "points" in shape and isinstance(shape.get("points"), list) and shape["points"]:
        xs = [float(point[0]) for point in shape["points"] if isinstance(point, list) and len(point) >= 2]
        ys = [float(point[1]) for point in shape["points"] if isinstance(point, list) and len(point) >= 2]
        if xs and ys:
            return min(xs), min(ys), max(xs), max(ys)
    if all(key in shape for key in ("x", "y", "w", "h")):
        x0 = float(shape["x"])
        y0 = float(shape["y"])
        return x0, y0, x0 + float(shape["w"]), y0 + float(shape["h"])
    return None


def _intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 < bx0 or ax0 > bx1 or ay1 < by0 or ay0 > by1)


def _matches_any(text: str, values: Iterable[str]) -> bool:
    return any(text == value for value in values)


def _matches_prefix(text: str, prefixes: Iterable[str]) -> bool:
    return any(text == prefix or text.startswith(prefix) for prefix in prefixes)


def shape_matches_policy(
    shape: dict[str, Any],
    policy: LayoutElementPolicy,
    *,
    editable_regions: dict[str, Any] | None = None,
) -> bool:
    metadata = _metadata(shape)
    name = str(shape.get("name") or "")
    kind = str(shape.get("kind") or "")
    layer = str(shape.get("layer") or "")
    role = str(metadata.get("role") or "")

    if policy.exclude_names and _matches_any(name, policy.exclude_names):
        return False
    if policy.exclude_prefixes and _matches_prefix(name, policy.exclude_prefixes):
        return False
    if policy.exclude_kinds and _matches_any(kind, policy.exclude_kinds):
        return False
    if policy.exclude_layers and _matches_any(layer, policy.exclude_layers):
        return False
    if policy.exclude_roles and _matches_any(role, policy.exclude_roles):
        return False

    if policy.include_kinds and not _matches_any(kind, policy.include_kinds):
        return False
    if policy.include_layers and not _matches_any(layer, policy.include_layers):
        return False

    matched_selectors = False
    has_selectors = bool(
        policy.include_names
        or policy.include_prefixes
        or policy.include_roles
        or policy.include_regions
        or policy.include_bbox_mm is not None
    )
    if policy.include_names and _matches_any(name, policy.include_names):
        matched_selectors = True
    if policy.include_prefixes and _matches_prefix(name, policy.include_prefixes):
        matched_selectors = True
    if policy.include_roles and _matches_any(role, policy.include_roles):
        matched_selectors = True

    if policy.include_regions and editable_regions:
        bbox = _shape_bbox(shape)
        if bbox is not None:
            for region_name in policy.include_regions:
                region = editable_regions.get(region_name)
                if isinstance(region, list) and len(region) >= 4:
                    region_box = tuple(float(value) for value in region[:4])
                    if _intersects(bbox, region_box):
                        matched_selectors = True
                        break

    if policy.include_bbox_mm is not None:
        bbox = _shape_bbox(shape)
        if bbox is not None and _intersects(bbox, policy.include_bbox_mm):
            matched_selectors = True

    if has_selectors:
        return matched_selectors
    return bool(policy.include_kinds or policy.include_layers) or not (
        policy.include_kinds
        or policy.include_layers
        or policy.include_names
        or policy.include_prefixes
        or policy.include_roles
        or policy.include_regions
        or policy.include_bbox_mm is not None
    )


def select_layout_elements(layout: dict[str, Any], policy: LayoutElementPolicy) -> list[dict[str, Any]]:
    metadata = layout.get("metadata") if isinstance(layout.get("metadata"), dict) else {}
    editable_regions = metadata.get("editable_regions") if isinstance(metadata.get("editable_regions"), dict) else {}
    return [
        shape
        for shape in layout.get("shapes", [])
        if isinstance(shape, dict) and shape_matches_policy(shape, policy, editable_regions=editable_regions)
    ]


def filter_shapes_by_bbox(layout: dict[str, Any], bbox: tuple[float, float, float, float]) -> list[dict[str, Any]]:
    policy = LayoutElementPolicy(include_bbox_mm=bbox)
    return select_layout_elements(layout, policy)


def candidate_layout_for_policy(layout: dict[str, Any], policy: LayoutElementPolicy, *, layout_scope: str) -> dict[str, Any]:
    candidate = deepcopy(layout)
    metadata = dict(candidate.get("metadata") if isinstance(candidate.get("metadata"), dict) else {})
    metadata["layout_scope"] = layout_scope
    metadata["layout_element_policy"] = policy.to_mapping()
    if policy.suppress_default_reference_ground_plane:
        metadata["suppress_default_reference_ground_plane"] = True
    candidate["metadata"] = metadata
    editable_regions = metadata.get("editable_regions") if isinstance(metadata.get("editable_regions"), dict) else {}
    candidate["shapes"] = [
        shape
        for shape in candidate.get("shapes", [])
        if isinstance(shape, dict)
        and (shape.get("kind") == "boundary" or shape_matches_policy(shape, policy, editable_regions=editable_regions))
    ]
    return candidate


__all__ = [
    "LayoutElementPolicy",
    "candidate_layout_for_policy",
    "filter_shapes_by_bbox",
    "load_layout_element_policy",
    "select_layout_elements",
    "shape_matches_policy",
]
