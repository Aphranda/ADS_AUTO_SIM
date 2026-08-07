#!/usr/bin/env python3
"""Inspect saved HFSS 3D Layout launch connectivity without opening AEDT.

This tool is intentionally file-backed. It reads the saved AEDT project text and
optionally scans the mixed text/binary AEDB edb.def for corroborating saved-state
hints. It does not start AEDT, does not use PyAEDT, and does not save projects.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
from statistics import mean
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def _line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _unique(values: list[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        if value and value not in output:
            output.append(value)
    return output


def _clean_snippet(text: str, *, limit: int = 500) -> str:
    cleaned = []
    for char in text:
        code = ord(char)
        if char in "\t " or 32 <= code < 127:
            cleaned.append(char)
        elif char in "\r\n":
            cleaned.append(" ")
        else:
            cleaned.append(" ")
    return re.sub(r"\s+", " ", "".join(cleaned)).strip()[:limit]


def _begin_end_blocks(text: str, name: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        rf"(?P<begin>^[ \t]*\$begin '{re.escape(name)}'\s*$)(?P<body>.*?)(^[ \t]*\$end '{re.escape(name)}'\s*$)",
        re.MULTILINE | re.DOTALL,
    )
    return [(match.start(), match.end(), match.group("body")) for match in pattern.finditer(text)]


def _planar_blocks(text: str) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    pattern = re.compile(r"^[ \t]*\$begin 'PlanarEMCircuit'\s*$(?P<body>.*?)(^[ \t]*\$end 'PlanarEMCircuit'\s*$)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(text):
        body = match.group("body")
        name_match = re.search(r"^[ \t]*Name='([^']+)'", body, re.MULTILINE)
        if name_match:
            output[name_match.group(1)] = {
                "start_line": _line_no(text, match.start()),
                "end_line": _line_no(text, match.end()),
                "body": body,
            }
    return output


def _parse_props(block: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for quoted_key, bare_key, value in re.findall(
        r"^[ \t]*(?:'([^']+)'|([A-Za-z][A-Za-z0-9_ ]*))='([^']*)'",
        block,
        re.MULTILINE,
    ):
        props[quoted_key or bare_key] = value
    return props


def _parse_component_instances(block: str) -> list[dict[str, Any]]:
    instances = []
    for match in re.finditer(r"\$begin 'Compinst'(?P<body>.*?)\$end 'Compinst'", block, re.DOTALL):
        body = match.group("body")
        comp_id = re.search(r"^[ \t]*ID='([^']+)'", body, re.MULTILINE)
        comp_name = re.search(r"^[ \t]*CompName='([^']+)'", body, re.MULTILINE)
        inst_name = re.search(r"TextProp\('InstanceName',\s*'[^']*',\s*'[^']*',\s*'([^']+)'\)", body)
        instances.append(
            {
                "id": comp_id.group(1) if comp_id else None,
                "component": comp_name.group(1) if comp_name else None,
                "instance_name": inst_name.group(1) if inst_name else None,
            }
        )

    schematic = {}
    schematic_pattern = re.compile(
        r"SchCompInst\('(?P<component>[^']+)',\s*'(?P<page>[^']+)',\s*'(?P<symbol_id>[^']+)',\s*(?P<orientation>\d+),\s*'(?P<id>[^']+)',\s*'(?P<mode>[^']+)',\s*(?P<x>[-+0-9.eE]+),\s*(?P<y>[-+0-9.eE]+),\s*(?P<angle>[-+0-9.eE]+),"
    )
    for match in schematic_pattern.finditer(block):
        schematic[match.group("id")] = {
            "component": match.group("component"),
            "page": match.group("page"),
            "symbol_id": match.group("symbol_id"),
            "orientation_code": int(match.group("orientation")),
            "mode": match.group("mode"),
            "x_m": float(match.group("x")),
            "y_m": float(match.group("y")),
            "angle_deg": float(match.group("angle")),
        }
    for instance in instances:
        if instance.get("id") in schematic:
            instance["schematic"] = schematic[instance["id"]]
    return instances


def _parse_nets(block: str) -> list[dict[str, Any]]:
    nets = []
    for match in re.finditer(r"\$begin 'Net'(?P<body>.*?)\$end 'Net'", block, re.DOTALL):
        body = match.group("body")
        name = re.search(r"^[ \t]*NetName='([^']+)'", body, re.MULTILINE)
        nets.append(
            {
                "name": name.group(1) if name else None,
                "interface_ports": re.findall(r"NetInterfacePorts='([^']+)'", body),
                "net_pins": [
                    {"component_id": comp_id, "pin_index": int(pin_index)}
                    for comp_id, pin_index in re.findall(r"NetPin\('([^']+)',\s*(\d+)\)", body)
                ],
            }
        )
    return nets


def _parse_page_nets(block: str) -> list[dict[str, Any]]:
    page_nets = []
    for match in re.finditer(r"\$begin 'PageNet'(?P<body>.*?)\$end 'PageNet'", block, re.DOTALL):
        body = match.group("body")
        name = re.search(r"^[ \t]*NetName='([^']+)'", body, re.MULTILINE)
        interface = re.search(r"Interface\('([^']+)',\s*(\d+)\)", body)
        page_nets.append(
            {
                "name": name.group(1) if name else None,
                "id": int(re.search(r"^[ \t]*ID=(\d+)", body, re.MULTILINE).group(1))
                if re.search(r"^[ \t]*ID=(\d+)", body, re.MULTILINE)
                else None,
                "interface": {"port": interface.group(1), "wire_id": int(interface.group(2))} if interface else None,
                "wire_segments": len(re.findall(r"WireSeg\(", body)),
                "component_pins": [
                    {"symbol_id": symbol_id, "pin": pin}
                    for symbol_id, pin in re.findall(r"PC\('([^']+)',\s*'([^']+)'\)", body)
                ],
            }
        )
    return page_nets


def _parse_ports(block: str) -> list[dict[str, Any]]:
    port_section = re.search(r"\$begin 'Port'\s*\$begin 'Data'(?P<body>.*?)\$end 'Data'", block, re.DOTALL)
    if not port_section:
        return []
    ports = []
    for match in re.finditer(r"\$begin '([^']+)'(?P<body>.*?)\$end '\1'", port_section.group("body"), re.DOTALL):
        name = match.group(1)
        body = match.group("body")
        props_block = re.search(r"\$begin 'Properties'(?P<body>.*?)\$end 'Properties'", body, re.DOTALL)
        props = _parse_props(props_block.group("body")) if props_block else {}
        fields = {}
        for key in ("Type", "UseRefFromHierarchy", "HFSSPortType", "Arms", "IsGapSource", "LayoutObject", "Pin", "CircuitPort", "AutoPort", "ValidateReference"):
            value = re.search(rf"^[ \t]*{re.escape(key)}=([^\r\n]+)", body, re.MULTILINE)
            if value:
                fields[key] = value.group(1).strip().strip("'")
        zrefs = re.findall(r"ZReferences\((.*?)\)", body)
        ports.append({"name": name, "properties": props, "fields": fields, "z_references": zrefs})
    return ports


def _port_flags(port: dict[str, Any]) -> list[str]:
    flags = []
    props = port.get("properties", {})
    fields = port.get("fields", {})
    hfss_type = str(props.get("HFSS Type") or fields.get("HFSSPortType") or "")
    port_type = str(props.get("Type") or fields.get("Type") or "")
    if "Invalid" in hfss_type or "Invalid" in port_type:
        flags.append("invalid_hfss_port")
    if not fields.get("LayoutObject") and fields.get("Type") == "Invalid":
        flags.append("no_layout_object")
    if fields.get("Type") == "EdgePort" and not props.get("Reference"):
        flags.append("edge_port_without_reference")
    if fields.get("Type") == "EdgePort" and "GND" not in str(props.get("Reference Net", "")):
        flags.append("edge_port_reference_net_not_gnd")
    return flags


def _inspect_design_from_aedt(text: str, design: str) -> dict[str, Any]:
    blocks = _planar_blocks(text)
    item: dict[str, Any] = {"design": design, "found": design in blocks}
    if design not in blocks:
        item["occurrences"] = len(re.findall(re.escape(design), text))
        return item
    block = blocks[design]["body"]
    ports = _parse_ports(block)
    nets = _parse_nets(block)
    page_nets = _parse_page_nets(block)
    item.update(
        {
            "start_line": blocks[design]["start_line"],
            "end_line": blocks[design]["end_line"],
            "component_instances": _parse_component_instances(block),
            "nets": nets,
            "page_nets": page_nets,
            "ports": ports,
            "port_flags": {port["name"]: _port_flags(port) for port in ports},
            "net_names": _unique([str(net["name"]) for net in nets if net.get("name")]),
        }
    )
    net_by_name = {net["name"]: net for net in nets}
    page_by_name = {net["name"]: net for net in page_nets}
    item["port_net_summary"] = []
    for port in ports:
        name = port["name"]
        net = net_by_name.get(name, {})
        page = page_by_name.get(name, {})
        item["port_net_summary"].append(
            {
                "port": name,
                "net_interface_ports": net.get("interface_ports", []),
                "net_pins": net.get("net_pins", []),
                "schematic_wire_segments": page.get("wire_segments"),
                "schematic_component_pins": page.get("component_pins", []),
                "port_type": port.get("fields", {}).get("Type"),
                "hfss_type": port.get("properties", {}).get("HFSS Type"),
                "layout_object": port.get("fields", {}).get("LayoutObject"),
                "reference": port.get("properties", {}).get("Reference"),
                "reference_net": port.get("properties", {}).get("Reference Net"),
            }
        )
    return item


def _read_csv_summary(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    if not rows:
        return {"path": str(path), "rows": 0}
    freq_col = next((col for col in rows[0] if "freq" in col.lower()), list(rows[0])[0])
    traces: dict[str, Any] = {}
    for col in rows[0]:
        if col == freq_col:
            continue
        values = []
        for row in rows:
            try:
                values.append((float(row[freq_col]), float(row[col])))
            except (KeyError, TypeError, ValueError):
                pass
        if not values:
            continue
        min_pair = min(values, key=lambda item: item[1])
        max_pair = max(values, key=lambda item: item[1])
        traces[col] = {
            "min_db": min_pair[1],
            "min_freq_ghz": min_pair[0],
            "max_db": max_pair[1],
            "max_freq_ghz": max_pair[0],
            "avg_db": mean(value for _, value in values),
        }
    through_cols = [col for col in traces if "S(Port2,Port1)" in col or "S(Port1,Port2)" in col]
    return_cols = [col for col in traces if "S(Port1,Port1)" in col or "S(Port2,Port2)" in col]
    through_max = max((traces[col]["max_db"] for col in through_cols), default=None)
    return_max = max((traces[col]["max_db"] for col in return_cols), default=None)
    return {
        "path": str(path),
        "rows": len(rows),
        "freq_col": freq_col,
        "traces": traces,
        "through_max_db": through_max,
        "return_max_db": return_max,
        "disconnected_signature": bool(through_max is not None and through_max < -20 and return_max is not None and return_max > -3),
    }


def _load_optional_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _scan_aedb_text(aedb: Path, designs: list[str], needles: list[str], *, window: int, max_matches: int) -> dict[str, Any]:
    edb_def = aedb / "edb.def" if aedb.is_dir() else aedb
    if not edb_def.exists():
        return {"path": str(edb_def), "exists": False}
    text = edb_def.read_bytes().decode("utf-8", errors="replace")
    lines = text.splitlines()
    scan_needles = _unique(designs + needles)
    matches = []
    for line_no, line in enumerate(lines, start=1):
        if any(needle in line for needle in scan_needles):
            start = max(1, line_no - window)
            end = min(len(lines), line_no + window)
            matches.append(
                {
                    "line": line_no,
                    "matched": [needle for needle in scan_needles if needle in line],
                    "text": _clean_snippet(line),
                    "context": [
                        {"line": idx, "text": _clean_snippet(lines[idx - 1])}
                        for idx in range(start, end + 1)
                        if lines[idx - 1].strip()
                    ],
                }
            )
            if 0 <= max_matches <= len(matches):
                break
    return {
        "path": str(edb_def),
        "exists": True,
        "size_bytes": edb_def.stat().st_size,
        "matches": matches,
        "matches_truncated": max_matches >= 0 and len(matches) >= max_matches,
    }


def _diagnose(design: dict[str, Any], csv_summary: dict[str, Any] | None, validate: dict[str, Any] | None) -> list[str]:
    findings = []
    for port, flags in design.get("port_flags", {}).items():
        if flags:
            findings.append(f"{port}: {', '.join(flags)}")
    if validate:
        port_list = validate.get("port_list", {}).get("value")
        excitations = validate.get("excitations", {}).get("value")
        if port_list == []:
            findings.append("PyAEDT live check reported empty app.port_list")
        if excitations == []:
            findings.append("PyAEDT live check reported empty app.excitations")
        for key in ("validate_design", "validate_simple", "validate_full_design"):
            if validate.get(key, {}).get("ok") is False:
                findings.append(f"{key} failed: {validate[key].get('error')}")
    if csv_summary and csv_summary.get("disconnected_signature"):
        findings.append(
            "S-parameter signature indicates an open/disconnected through path "
            f"(through max {csv_summary.get('through_max_db'):.2f} dB, return max {csv_summary.get('return_max_db'):.2f} dB)"
        )
    return findings


def _comparative_findings(designs: list[dict[str, Any]]) -> list[str]:
    findings = []
    disconnected = [
        design.get("design")
        for design in designs
        if (design.get("sparameter_csv_summary") or {}).get("disconnected_signature")
    ]
    passing = [
        design.get("design")
        for design in designs
        if (design.get("sparameter_csv_summary") or {}).get("disconnected_signature") is False
    ]
    if disconnected and passing:
        findings.append(
            "At least one design passes the through-path S-parameter check while another is disconnected; common saved "
            "port metadata such as connector-side Port1 invalid state is unlikely to be the sole root cause."
        )
    if len(designs) >= 2:
        port_flags = {design.get("design"): design.get("port_flags", {}) for design in designs}
        flag_values = list(port_flags.values())
        if flag_values and all(flags == flag_values[0] for flags in flag_values[1:]) and disconnected:
            findings.append(
                "The inspected designs have matching port flag patterns, so the failing case should be checked at the "
                "layout RF net/edge-port geometry level rather than only the schematic IPort names."
            )
    return findings


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    text = _read_text(args.project)
    csv_by_design = {}
    for item in args.csv:
        if "=" in item:
            design, path = item.split("=", 1)
        else:
            design, path = "", item
        csv_by_design[design] = _read_csv_summary(Path(path))
    validate_by_design = {}
    for item in args.validate_json:
        if "=" in item:
            design, path = item.split("=", 1)
        else:
            design, path = "", item
        validate_by_design[design] = _load_optional_json(Path(path))

    designs = []
    for design_name in args.design:
        design = _inspect_design_from_aedt(text, design_name)
        csv_summary = csv_by_design.get(design_name) or csv_by_design.get("")
        validate = validate_by_design.get(design_name) or validate_by_design.get("")
        design["sparameter_csv_summary"] = csv_summary
        design["validate_json_summary"] = validate
        design["diagnosis"] = _diagnose(design, csv_summary, validate)
        designs.append(design)

    needles = _unique(args.needle + args.net + args.port)
    for design in designs:
        for port in design.get("ports", []):
            needles.extend([port["name"], port.get("properties", {}).get("Reference", ""), port.get("fields", {}).get("LayoutObject", "")])
        needles.extend(design.get("net_names", []))
    needles = _unique([needle for needle in needles if needle])

    payload = {
        "project": str(args.project),
        "aedb": str(args.aedb) if args.aedb else None,
        "backend": "saved_file",
        "designs": designs,
        "comparative_findings": _comparative_findings(designs),
        "aedb_text_scan": _scan_aedb_text(args.aedb, args.design, needles, window=args.aedb_window, max_matches=args.max_aedb_matches)
        if args.aedb
        else None,
        "notes": [
            "This script is read-only and does not launch AEDT.",
            "AEDB edb.def is mixed binary/text; aedb_text_scan is corroborating context, not a full geometry parser.",
        ],
    }
    return payload


def _print_summary(payload: dict[str, Any]) -> None:
    print(f"project={payload['project']}")
    for finding in payload.get("comparative_findings", []):
        print(f"comparison: {finding}")
    for design in payload.get("designs", []):
        print(f"\n[{design.get('design')}] found={design.get('found')}")
        for item in design.get("port_net_summary", []):
            print(
                "  {port}: type={port_type} hfss={hfss_type} layout={layout_object} "
                "ref={reference} ref_net={reference_net} pins={schematic_component_pins} wires={schematic_wire_segments}".format(
                    **item
                )
            )
        csv_summary = design.get("sparameter_csv_summary") or {}
        if csv_summary:
            print(
                "  sparam: through_max={:.2f}dB return_max={:.2f}dB disconnected_signature={}".format(
                    csv_summary.get("through_max_db", float("nan")),
                    csv_summary.get("return_max_db", float("nan")),
                    csv_summary.get("disconnected_signature"),
                )
            )
        for finding in design.get("diagnosis", []):
            print(f"  diagnosis: {finding}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect saved real-board HFSS launch connectivity.")
    parser.add_argument("--project", type=Path, required=True, help="Saved AEDT project path.")
    parser.add_argument("--aedb", type=Path, default=None, help="Optional AEDB folder or edb.def path for saved-state text scan.")
    parser.add_argument("--design", action="append", required=True, help="Design to inspect. Repeat for multiple designs.")
    parser.add_argument("--net", action="append", default=[], help="Important net to include in AEDB text scan.")
    parser.add_argument("--port", action="append", default=[], help="Important port to include in AEDB text scan.")
    parser.add_argument("--needle", action="append", default=[], help="Extra saved-text token to scan in AEDB.")
    parser.add_argument("--csv", action="append", default=[], help="Optional design=csv_path S-parameter report CSV.")
    parser.add_argument("--validate-json", action="append", default=[], help="Optional design=json_path live validation artifact.")
    parser.add_argument("--aedb-window", type=int, default=2, help="Context lines around AEDB text matches.")
    parser.add_argument("--max-aedb-matches", type=int, default=80, help="Maximum AEDB text matches. Use -1 for no limit.")
    parser.add_argument("--summary", action="store_true", help="Print compact human-readable summary.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inspect(args)
    if args.summary:
        _print_summary(payload)
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
    if not args.summary:
        print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
