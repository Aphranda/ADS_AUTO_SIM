import json
from pathlib import Path

from simads.domain import SimulationResultSpec, StackupSpec, SweepSpec
from simads.runtime import (
    SimulationManifestPayload,
    SimulationRunContext,
    build_simulation_artifacts,
    write_simulation_manifests,
)


def test_write_simulation_manifests(tmp_path: Path) -> None:
    layout = tmp_path / "candidate_layout.json"
    layout.write_text('{"layout_id": "candidate"}\n', encoding="utf-8")
    s2p = tmp_path / "filter.s2p"
    s2p.write_text("! touchstone placeholder\n", encoding="utf-8")
    run_dir = tmp_path / "runs" / "run1"
    payload = SimulationManifestPayload(
        context=SimulationRunContext(
            project_id="project_a",
            round_id="round1",
            candidate_id="candidate",
            profile_id="hfss3dlayout",
            simulator="hfss3dlayout",
            run_id="run1",
        ),
        sweep=SweepSpec(start_ghz=4.0, stop_ghz=10.0, points=40),
        stackup=StackupSpec(
            stackup_id="FR4_210UM",
            dielectric_material="FR4",
            er=4.6,
            loss_tangent=0.02,
            dielectric_height_mm=0.21,
            copper_thickness_mm=0.035,
        ),
        inputs={"layout_json": str(layout)},
        outputs={"s2p": str(s2p)},
        result=SimulationResultSpec(simulator="hfss3dlayout", s2p=s2p),
    )
    artifacts = build_simulation_artifacts(layout_json=layout, s2p=s2p, state=run_dir / "state.json")

    paths = write_simulation_manifests(
        run_dir=run_dir,
        run_id="run1",
        payload=payload,
        artifacts=artifacts,
        status="completed",
        stage="completed",
        elapsed_s=1.2345,
    )

    assert paths["run_manifest"].exists()
    run_manifest = json.loads(paths["run_manifest"].read_text(encoding="utf-8"))
    artifact_manifest = json.loads(paths["artifact_manifest"].read_text(encoding="utf-8"))
    state = json.loads(paths["state"].read_text(encoding="utf-8"))

    assert run_manifest["simulator"] == "hfss3dlayout"
    assert run_manifest["sweep"]["spacing_mhz"] == (10.0 - 4.0) / 39 * 1000.0
    assert run_manifest["outputs"]["state"].endswith("state.json")
    assert state["status"] == "completed"
    assert any(item["type"] == "s2p" and item["exists"] for item in artifact_manifest["artifacts"])
