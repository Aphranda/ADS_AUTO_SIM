"""Helpers for selecting and rebuilding the BFP filter core only."""

from __future__ import annotations

from simads.hfss.layout_elements import LayoutElementPolicy, candidate_layout_for_policy, select_layout_elements


FILTER_CORE_SCOPE = "bfp-filter-core"
FILTER_CORE_ROLES = {"signal_filter_core", "filter_core"}


def filter_core_policy() -> LayoutElementPolicy:
    return LayoutElementPolicy(
        include_roles=tuple(sorted(FILTER_CORE_ROLES)),
        include_prefixes=("filter_core_",),
        suppress_default_reference_ground_plane=True,
    )


def filter_core_shapes(layout: dict[str, Any]) -> list[dict[str, Any]]:
    return select_layout_elements(layout, filter_core_policy())


def filter_core_delete_names(layout: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for shape in filter_core_shapes(layout):
        name = str(shape.get("name") or "")
        if name and name not in names:
            names.append(name)
    return names


def candidate_layout_for_filter_core(layout: dict[str, Any]) -> dict[str, Any]:
    return candidate_layout_for_policy(layout, filter_core_policy(), layout_scope=FILTER_CORE_SCOPE)


__all__ = [
    "FILTER_CORE_ROLES",
    "FILTER_CORE_SCOPE",
    "candidate_layout_for_filter_core",
    "filter_core_delete_names",
    "filter_core_policy",
    "filter_core_shapes",
]
