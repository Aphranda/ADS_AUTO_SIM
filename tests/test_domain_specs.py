from simads.domain import SimulationResultSpec, StackupSpec, SweepSpec


def test_sweep_spec_reports_frequency_spacing() -> None:
    sweep = SweepSpec(start_ghz=4.0, stop_ghz=10.0, points=40)

    assert sweep.spacing_ghz == (10.0 - 4.0) / 39
    assert round(sweep.spacing_mhz, 6) == round(6000.0 / 39, 6)
    assert sweep.to_dict()["points"] == 40


def test_sweep_spec_rejects_invalid_ranges() -> None:
    try:
        SweepSpec(start_ghz=10.0, stop_ghz=4.0, points=40)
    except ValueError as exc:
        assert "stop_ghz" in str(exc)
    else:
        raise AssertionError("invalid sweep range should fail")


def test_stackup_and_result_specs_are_serializable() -> None:
    stackup = StackupSpec(
        stackup_id="FR4_210UM",
        dielectric_material="SIMADS_FR4_ER4P6_TD02",
        er=4.6,
        loss_tangent=0.02,
        dielectric_height_mm=0.21,
        copper_thickness_mm=0.035,
    )
    result = SimulationResultSpec(
        simulator="hfss3dlayout",
        project="D:/Work/ADS/SIMADS_EM_PAR/HFSS_VERDICT/example.aedt",
        s2p="results/example/filter.s2p",
    )

    assert stackup.to_dict()["bottom_layer"] == "GND"
    assert result.to_dict()["simulator"] == "hfss3dlayout"
    assert result.to_dict()["s2p"] == "results/example/filter.s2p"
