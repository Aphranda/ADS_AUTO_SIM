from argparse import Namespace

from simads.hfss.plans import RELIABLE_HFSS_ROUTE, apply_hfss_route_defaults


def test_apply_hfss_route_defaults_keeps_custom_args() -> None:
    args = Namespace(
        route="custom",
        port_type="wave",
        gnd_boundary_mode="em-boundary",
        configure_extents=False,
        reference_ground_ports=True,
        patch_edb_port_properties=False,
    )

    route = apply_hfss_route_defaults(args)

    assert route == "custom"
    assert args.port_type == "wave"
    assert args.gnd_boundary_mode == "em-boundary"
    assert args.configure_extents is False
    assert args.reference_ground_ports is True
    assert args.patch_edb_port_properties is False


def test_apply_hfss_route_defaults_expands_reliable_route() -> None:
    args = Namespace(
        route="reliable",
        port_type="wave",
        gnd_boundary_mode="em-boundary",
        configure_extents=False,
        reference_ground_ports=True,
        patch_edb_port_properties=False,
    )

    route = apply_hfss_route_defaults(args)

    assert route == RELIABLE_HFSS_ROUTE
    assert args.route == RELIABLE_HFSS_ROUTE
    assert args.port_type == "aedt-edge"
    assert args.gnd_boundary_mode == "port-edges"
    assert args.configure_extents is True
    assert args.reference_ground_ports is False
    assert args.patch_edb_port_properties is True


def test_apply_hfss_route_defaults_accepts_full_reliable_route_name() -> None:
    args = Namespace(route=RELIABLE_HFSS_ROUTE)

    route = apply_hfss_route_defaults(args)

    assert route == RELIABLE_HFSS_ROUTE
    assert args.port_type == "aedt-edge"
