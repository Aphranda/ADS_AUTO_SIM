import csv
import json
from pathlib import Path

from simads.workflows.backend_summary import build_backend_summary, write_backend_summary


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_backend_summary_combines_ads_and_hfss_run_manifests(tmp_path: Path) -> None:
    ads_run = tmp_path / "runs" / "ads_run"
    hfss_run = tmp_path / "runs" / "hfss_run"
    write_json(
        ads_run / "run_manifest.json",
        {
            "run_id": "ads_run",
            "project_id": "project_a",
            "round_id": "round1",
            "candidate_id": "candidate_a",
            "profile_id": "home_ads",
            "pipeline_id": "pipeline_a",
            "simulator": "ads_rfpro",
            "status": "completed",
            "stage": "scored",
            "elapsed_s": 12.3,
            "outputs": {"score_csv": "ads_score.csv", "trace_csv": "ads_trace.csv"},
        },
    )
    write_json(ads_run / "state.json", {"status": "completed", "stage": "scored"})
    write_json(
        hfss_run / "run_manifest.json",
        {
            "run_id": "hfss_run",
            "project_id": "project_a",
            "round_id": "round1",
            "candidate_id": "candidate_a",
            "profile_id": "home",
            "pipeline_id": "pipeline_a",
            "simulator": "hfss3dlayout",
            "status": "completed",
            "stage": "scored",
            "outputs": {"score_csv": "hfss_score.csv", "trace_csv": "hfss_trace.csv", "s2p": "hfss.s2p"},
        },
    )

    rows = build_backend_summary([tmp_path / "runs"])
    out = write_backend_summary(tmp_path / "backend_summary.csv", rows)

    assert [(row["backend"], row["score_path"]) for row in rows] == [
        ("ads_rfpro", "ads_score.csv"),
        ("hfss3dlayout", "hfss_score.csv"),
    ]
    assert rows[0]["pipeline_id"] == "pipeline_a"
    with out.open(newline="", encoding="utf-8") as fp:
        written = list(csv.DictReader(fp))
    assert written[1]["trace_path"] == "hfss_trace.csv"
    assert written[1]["s2p_path"] == "hfss.s2p"
