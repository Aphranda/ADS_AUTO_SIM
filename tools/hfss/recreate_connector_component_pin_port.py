#!/usr/bin/env python3
"""Recreate a connector component-pin port and its schematic connection through AEDT APIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from try_official_port_create_elements import _json_default, run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Delete a bad connector schematic IPort, try recreating the layout connector port with "
            "CreatePortsOnComponents, move the generated schematic IPort to a safe blank location, "
            "and explicitly wire it to the connector component pin. A port is accepted only when AEDT "
            "reports real ConnectionPoints; component-pin-only ports with ConnectionPoints=NONE are rejected."
        )
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--design", required=True)
    parser.add_argument("--component", required=True, help="Layout/schematic connector component name, for reporting.")
    parser.add_argument("--component-def", required=True, help="Connector component definition name, for reporting.")
    parser.add_argument("--component-id", required=True, help="AEDT component instance id, also used as CreatePortsOnComponents element.")
    parser.add_argument("--raw-component", required=True, help="Raw schematic selection, for example CompInst@SMA_...;80;8.")
    parser.add_argument("--pin", default="Pin_T1")
    parser.add_argument("--port", required=True, help="Expected generated AEDT port name, for example S2_1_Pin_T1.")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--schematic-safe-x-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-y-mil", type=float, default=None)
    parser.add_argument("--schematic-safe-min-clearance-mil", type=float, default=250.0)
    parser.add_argument("--schematic-safe-grid-start-x-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-start-y-mil", type=float, default=-4000.0)
    parser.add_argument("--schematic-safe-grid-step-mil", type=float, default=1000.0)
    parser.add_argument("--schematic-safe-grid-count", type=int, default=9)
    parser.add_argument("--keep-old-schematic-wires", action="store_false", dest="delete_old_schematic_wires")
    parser.set_defaults(delete_old_schematic_wires=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--non-graphical", action="store_true", default=True)
    parser.add_argument("--graphical", action="store_false", dest="non_graphical")
    parser.add_argument("--new-desktop", action="store_true", default=True)
    parser.add_argument("--attach-existing", action="store_false", dest="new_desktop")
    parser.add_argument("--remove-lock", action="store_true")
    parser.add_argument("--keep-attached", action="store_true")
    parser.add_argument("--close-projects", action="store_true")
    parser.add_argument("--close-desktop", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def to_official_args(args: argparse.Namespace) -> argparse.Namespace:
    if (args.schematic_safe_x_mil is None) ^ (args.schematic_safe_y_mil is None):
        raise SystemExit("--schematic-safe-x-mil and --schematic-safe-y-mil must be provided together")
    args.schematic_component_id = ""
    args.schematic_symbol_id = ""
    args.page_net_id = ""
    args.element = [args.component_id]
    args.method = ["CreatePortsOnComponents"]
    args.delete_iport = True
    args.connect_schematic = True
    args.move_schematic_iport = True
    return args


def main() -> int:
    args = to_official_args(parse_args())
    payload = run(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("status") in {"dry_run", "created_good_candidate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
