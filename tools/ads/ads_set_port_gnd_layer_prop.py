#!/usr/bin/env python3
r"""Set ADS layout Term portGndLayer properties for EM port reference tests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_TOOLS_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
for _path in (_TOOLS_ROOT, _SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import profile_names, resolve_library, resolve_workspace


def ensure_hpeesof_dir() -> None:
    if os.environ.get("HPEESOF_DIR"):
        return
    executable = Path(sys.executable).resolve()
    try:
        ads_root = executable.parents[2]
    except IndexError:
        return
    if (ads_root / "tools").exists():
        os.environ["HPEESOF_DIR"] = str(ads_root)


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{stamp}] {message}", flush=True)


def _prop_value(prop: Any) -> object:
    try:
        return prop.value
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def set_term_string_prop(db_uu: Any, term: Any, name: str, value: str) -> dict[str, object]:
    existing = term.find_prop(name)
    if existing is None:
        created = db_uu.StringProp.create(term, name, value)
        return {"name": name, "action": "created", "before": None, "after": _prop_value(created)}

    before = _prop_value(existing)
    try:
        existing.value = value
        action = "updated"
        after = _prop_value(existing)
    except Exception:
        existing.delete_prop()
        created = db_uu.StringProp.create(term, name, value)
        action = "recreated"
        after = _prop_value(created)
    return {"name": name, "action": action, "before": before, "after": after}


def set_port_gnd_layer_props(
    workspace_path: Path,
    library_name: str,
    cell_name: str,
    view_name: str,
    port_names: tuple[str, ...],
    gnd_layer: str,
) -> dict[str, object]:
    ensure_hpeesof_dir()
    import keysight.ads.de as de
    from keysight.ads.de import db_uu

    log(f"Opening ADS workspace: {workspace_path}")
    workspace = de.open_workspace(str(workspace_path))
    try:
        design = db_uu.open_design((library_name, cell_name, view_name), "Append")
        try:
            rows: list[dict[str, object]] = []
            for port_name in port_names:
                term = design.find_term(port_name)
                if term is None:
                    raise RuntimeError(f"Term not found: {port_name}")
                prop_result = set_term_string_prop(db_uu, term, "portGndLayer", gnd_layer)
                rows.append({"port": port_name, **prop_result})
            log(f"Saving layout with portGndLayer props: {library_name}:{cell_name}:{view_name}")
            design.save_design()
        finally:
            close_design = getattr(design, "close_design", None)
            if callable(close_design):
                close_design()
    finally:
        workspace.close()

    return {
        "workspace": str(workspace_path),
        "library": library_name,
        "cell": cell_name,
        "view": view_name,
        "gnd_layer": gnd_layer,
        "rows": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set portGndLayer StringProp on ADS layout P1/P2 terms.")
    parser.add_argument("--profile", default="home_simads_em_parallel", choices=profile_names())
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--library", default=None)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--view", default="layout")
    parser.add_argument("--port", action="append", dest="ports", default=None)
    parser.add_argument("--gnd-layer", default="ETCH_INNER1")
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def _resolve_output_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return _REPO_ROOT / path


def main() -> None:
    args = parse_args()
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    result = set_port_gnd_layer_props(
        workspace,
        library,
        args.cell,
        args.view,
        tuple(args.ports or ("P1", "P2")),
        args.gnd_layer,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        out_path = _resolve_output_path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote portGndLayer prop result: {out_path}", flush=True)
    print(text, flush=True)


if __name__ == "__main__":
    main()
