from argparse import Namespace

from simads.hfss.workflow import completed_hfss_stage
from simads.runtime import resume_stage_for_failed_step, validate_stage


def test_state_machine_accepts_ads_legacy_and_backend_neutral_stages() -> None:
    for stage in ("ads_imported", "emsetup_ready", "dataset_exported", "geometry_built", "ports_ready", "setup_ready", "results_exported", "scored"):
        assert validate_stage(stage).ok


def test_resume_stage_supports_hfss_failed_steps() -> None:
    assert resume_stage_for_failed_step("HFSS solve") == "sim_running"
    assert resume_stage_for_failed_step("HFSS export touchstone") == "results_exported"
    assert resume_stage_for_failed_step("run_hfss3dlayout_filter_verdict.py") == "planned"


def test_completed_hfss_stage_distinguishes_build_export_and_score() -> None:
    assert completed_hfss_stage(Namespace(build_only=True), {}) == "setup_ready"
    assert completed_hfss_stage(Namespace(build_only=False), {"s2p": "case.s2p"}) == "results_exported"
    assert completed_hfss_stage(Namespace(build_only=False), {"s2p": "case.s2p", "post_processed": True}) == "scored"
