"""Scoring-system registry for Touchstone S-parameter result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringSystemSpec:
    system: str
    nports: int
    profile_dir: str
    score_key: str
    supports_baseline: bool
    metric_family: str
    primary_metrics: tuple[str, ...]

    @property
    def touchstone_suffix(self) -> str:
        return f"s{self.nports}p"


SCORING_SYSTEM_SPECS = {
    "filter": ScoringSystemSpec(
        system="filter",
        nports=2,
        profile_dir="filters",
        score_key="status",
        supports_baseline=False,
        metric_family="bandpass_filter",
        primary_metrics=(
            "s21_stopband_rejection",
            "s21_passband_minimum",
            "s21_passband_ripple",
            "s11_s22_passband_return",
        ),
    ),
    "connector": ScoringSystemSpec(
        system="connector",
        nports=2,
        profile_dir="connectors",
        score_key="connector_score",
        supports_baseline=True,
        metric_family="two_port_launch",
        primary_metrics=(
            "s21_insertion_loss",
            "s21_extra_loss_vs_baseline",
            "s11_s22_return_loss",
            "s11_s22_weighted_balance",
            "smith_impedance_hint",
        ),
    ),
    "sp8t": ScoringSystemSpec(
        system="sp8t",
        nports=4,
        profile_dir="sp8t",
        score_key="sp8t_score",
        supports_baseline=True,
        metric_family="four_port_switch_path",
        primary_metrics=(
            "s21_s43_through_loss",
            "s21_s43_extra_loss_vs_baseline",
            "s11_s22_s33_s44_return_loss",
            "near_end_isolation_s31_s13",
            "far_end_isolation_s42_s24",
            "diagonal_isolation_s41_s14_s32_s23",
        ),
    ),
}

SCORING_SYSTEM_NPORTS = {system: spec.nports for system, spec in SCORING_SYSTEM_SPECS.items()}
SCORING_SYSTEM_DIRS = {system: spec.profile_dir for system, spec in SCORING_SYSTEM_SPECS.items()}


def get_scoring_system_spec(system: str) -> ScoringSystemSpec:
    try:
        return SCORING_SYSTEM_SPECS[system]
    except KeyError as exc:
        raise ValueError(f"unknown scoring system: {system}") from exc


__all__ = [
    "SCORING_SYSTEM_DIRS",
    "SCORING_SYSTEM_NPORTS",
    "SCORING_SYSTEM_SPECS",
    "ScoringSystemSpec",
    "get_scoring_system_spec",
]
