#!/usr/bin/env python3
"""Compare saved HFSS 3D Layout launch designs from an AEDT project file.

This is a static, read-only comparison for debugging launch configuration
differences without opening AEDT.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

_TOOL_DIR = Path(__file__).resolve().parent
import sys

if str(_TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOL_DIR))

from inspect_real_board_launch_connectivity import (  # noqa: E402
    _inspect_design_from_aedt,
    _read_text,
)


def _json_default(value: Any) -> str:
    return str(value)


def _planar_blocks(text: str) -> dict[str, str]:
    blocks = {}
    pattern = re.compile(r"^[ \t]*\$begin 'PlanarEMCircuit'\s*$(?P<body>.*?)(^[ \t]*\$end 'PlanarEMCircuit'\s*$)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(text):
        body = match.group("body")
        name = re.search(r"^[ \t]*Name='([^']+)'", body, re.MULTILINE)
        if name:
            blocks[name.group(1)] = body
    return blocks


def _port_names(design: dict[str, Any]) -> list[str]:
    return [port["name"] for port in design.get("ports", [])]


def _port_brief(port: dict[str, Any]) -> dict[str, Any]:
    props = port.get("properties", {})
    fields = port.get("fields", {})
    return {
        "name": port.get("name"),
        "type": fields.get("Type") or props.get("Type"),
        "hfss_type": fields.get("HFSSPortType") or props.get("HFSS Type"),
        "layout_object": fields.get("LayoutObject"),
        "pin": fields.get("Pin"),
        "reference": props.get("Reference"),
        "reference_net": props.get("Reference Net"),
        "arms": fields.get("Arms"),
        "use_ref_from_hierarchy": fields.get("UseRefFromHierarchy"),
    }


def _nets_brief(design: dict[str, Any]) -> dict[str, Any]:
    return {
        net["name"]: {
            "interface_ports": net.get("interface_ports", []),
            "net_pins": net.get("net_pins", []),
        }
        for net in design.get("nets", [])
        if net.get("name")
    }


def _page_nets_brief(design: dict[str, Any]) -> dict[str, Any]:
    return {
        net["name"]: {
            "interface": net.get("interface"),
            "wire_segments": net.get("wire_segments"),
            "component_pins": net.get("component_pins", []),
        }
        for net in design.get("page_nets", [])
        if net.get("name")
    }


def _quantity_idmaps(block: str) -> list[str]:
    return re.findall(r"IDMap\(([^)]*S\([^)]*\)[^)]*)\)", block)


def _report_exprs_for_design(text: str, design: str) -> list[str]:
    exprs: list[str] = []
    design_pat = re.compile(rf"DesignEditor='{re.escape(design)}'(?P<body>.*?)(?=DesignEditor='|$)", re.DOTALL)
    for match in design_pat.finditer(text):
        exprs.extend(re.findall(r"Expr='([^']+)'", match.group("body")))
    return list(dict.fromkeys(exprs))


def _component_defs(text: str, names: list[str]) -> dict[str, dict[str, Any]]:
    output = {}
    for name in names:
        pattern = re.compile(rf"^[ \t]*\$begin '{re.escape(name)}'\s*$(?P<body>.*?)(^[ \t]*\$end '{re.escape(name)}'\s*$)", re.MULTILINE | re.DOTALL)
        match = pattern.search(text)
        if not match:
            output[name] = {"found": False}
            continue
        body = match.group("body")
        output[name] = {
            "found": True,
            "pin_defs": re.findall(r"Pin\('([^']+)',\s*([-+0-9.eE]+),\s*([-+0-9.eE]+),", body),
            "variables": {
                key: value
                for key, value in re.findall(r"VariableProp\(n='([^']+)',\s*v='([^']+)'", body)
            },
            "cosim_dynlink": re.findall(r"DynLink\((.*?)\)\)", body, re.DOTALL),
        }
    return output


def _compare_dict(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(left) | set(right))
    return {
        key: {"left": left.get(key), "right": right.get(key)}
        for key in keys
        if left.get(key) != right.get(key)
    }


def _compare_designs(text: str, left_name: str, right_name: str) -> dict[str, Any]:
    blocks = _planar_blocks(text)
    left = _inspect_design_from_aedt(text, left_name)
    right = _inspect_design_from_aedt(text, right_name)
    left_ports = {port["name"]: _port_brief(port) for port in left.get("ports", [])}
    right_ports = {port["name"]: _port_brief(port) for port in right.get("ports", [])}
    left_components = [item.get("component") for item in left.get("component_instances", []) if item.get("component")]
    right_components = [item.get("component") for item in right.get("component_instances", []) if item.get("component")]
    return {
        "left": left_name,
        "right": right_name,
        "left_found": left.get("found"),
        "right_found": right.get("found"),
        "left_components": left.get("component_instances", []),
        "right_components": right.get("component_instances", []),
        "left_ports": list(left_ports.values()),
        "right_ports": list(right_ports.values()),
        "port_names": {"left": _port_names(left), "right": _port_names(right)},
        "port_differences": _compare_dict(left_ports, right_ports),
        "net_differences": _compare_dict(_nets_brief(left), _nets_brief(right)),
        "page_net_differences": _compare_dict(_page_nets_brief(left), _page_nets_brief(right)),
        "quantity_idmaps": {
            "left": _quantity_idmaps(blocks.get(left_name, "")),
            "right": _quantity_idmaps(blocks.get(right_name, "")),
        },
        "report_exprs": {
            "left": _report_exprs_for_design(text, left_name),
            "right": _report_exprs_for_design(text, right_name),
        },
        "component_definitions": _component_defs(text, left_components + right_components),
        "findings": _findings(left_name, right_name, left, right, left_ports, right_ports, text),
    }


def _findings(
    left_name: str,
    right_name: str,
    left: dict[str, Any],
    right: dict[str, Any],
    left_ports: dict[str, Any],
    right_ports: dict[str, Any],
    text: str,
) -> list[str]:
    findings = []
    left_port_names = set(left_ports)
    right_port_names = set(right_ports)
    if left_port_names != right_port_names:
        findings.append(f"port set differs: {left_name}={sorted(left_port_names)}, {right_name}={sorted(right_port_names)}")
    for name in sorted(left_port_names & right_port_names):
        if left_ports[name].get("type") != right_ports[name].get("type") or left_ports[name].get("hfss_type") != right_ports[name].get("hfss_type"):
            findings.append(f"port {name} type differs")
    left_exprs = _report_exprs_for_design(text, left_name)
    right_exprs = _report_exprs_for_design(text, right_name)
    if any("S1_1_Pin_T1" in expr for expr in left_exprs) and not any("S1_1_Pin_T1" in expr for expr in right_exprs):
        findings.append(f"{left_name} reports include S1_1_Pin_T1 but {right_name} reports do not")
    if any("S1_1_Pin_T1" in expr for expr in right_exprs) and not any("S1_1_Pin_T1" in expr for expr in left_exprs):
        findings.append(f"{right_name} reports include S1_1_Pin_T1 but {left_name} reports do not")
    for design_name, design in ((left_name, left), (right_name, right)):
        invalid = [port["name"] for port in design.get("ports", []) if "Invalid" in str(port.get("properties", {}).get("HFSS Type", ""))]
        if invalid:
            findings.append(f"{design_name} has saved invalid HFSS ports: {invalid}")
    return findings


def compare(args: argparse.Namespace) -> dict[str, Any]:
    text = _read_text(args.project)
    return {
        "project": str(args.project),
        "comparisons": [_compare_designs(text, left, right) for left, right in args.pair],
        "notes": [
            "Static comparison reads saved AEDT only and does not launch AEDT.",
            "Numeric IDs, symbols, and placement coordinates are expected to differ across copied designs.",
        ],
    }


def _print_summary(payload: dict[str, Any]) -> None:
    for item in payload.get("comparisons", []):
        print(f"\n[{item['left']} vs {item['right']}]")
        print(f"ports: {item['port_names']}")
        print(f"left_components={item['left_components']}")
        print(f"right_components={item['right_components']}")
        print(f"quantity_idmaps={item['quantity_idmaps']}")
        print(f"report_exprs={item['report_exprs']}")
        for finding in item.get("findings", []):
            print(f"finding: {finding}")


def _pair(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("pair must be LEFT:RIGHT")
    left, right = value.split(":", 1)
    return left, right


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare saved HFSS 3D Layout launch designs.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--pair", type=_pair, action="append", required=True, help="Design pair as LEFT:RIGHT")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare(args)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.summary:
        _print_summary(payload)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
