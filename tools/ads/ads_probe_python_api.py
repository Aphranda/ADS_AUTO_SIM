#!/usr/bin/env python3
r"""Probe ADS Python APIs by keyword and dump signatures/docs.

Run with ADS Python when possible, for example:

    D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe tools\ads\ads_probe_python_api.py --out out.md
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Iterable


DEFAULT_MODULES = (
    "keysight.ads.de",
    "keysight.ads.de.db_uu",
    "keysight.ads.de.tech",
    "keysight.ads.ael",
    "keysight.ads.emtools",
    "keysight.edatoolbox.ads",
    "keysight.edatoolbox.xxpro",
)

DEFAULT_KEYWORDS = (
    "port",
    "gnd",
    "ground",
    "reference",
    "term",
    "terminal",
    "pin",
    "em",
    "setup",
    "layer",
)


@dataclass(frozen=True)
class ApiHit:
    module: str
    qualname: str
    kind: str
    signature: str
    doc: str


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _short_doc(obj: object, max_chars: int = 220) -> str:
    doc = inspect.getdoc(obj) or ""
    line = " ".join(doc.split())
    if len(line) > max_chars:
        return line[: max_chars - 3] + "..."
    return line


def _signature(obj: object) -> str:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return ""


def _kind(obj: object) -> str:
    if inspect.ismodule(obj):
        return "module"
    if inspect.isclass(obj):
        return "class"
    if inspect.ismethod(obj):
        return "method"
    if inspect.isfunction(obj):
        return "function"
    if inspect.isbuiltin(obj):
        return "builtin"
    return type(obj).__name__


def _safe_getattr(obj: object, name: str) -> object | None:
    try:
        return getattr(obj, name)
    except Exception:
        return None


def _iter_public_members(obj: object) -> Iterable[tuple[str, object]]:
    for name in dir(obj):
        if name.startswith("_"):
            continue
        member = _safe_getattr(obj, name)
        if member is not None:
            yield name, member


def _record_if_match(
    hits: list[ApiHit],
    module_name: str,
    qualname: str,
    obj: object,
    keywords: tuple[str, ...],
) -> None:
    doc = _short_doc(obj)
    haystack = f"{qualname} {doc}"
    if not _contains_keyword(haystack, keywords):
        return
    hits.append(
        ApiHit(
            module=module_name,
            qualname=qualname,
            kind=_kind(obj),
            signature=_signature(obj),
            doc=doc,
        )
    )


def probe_module(module_name: str, keywords: tuple[str, ...], *, recurse_classes: bool = True) -> tuple[list[ApiHit], str | None]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return ([], f"{type(exc).__name__}: {exc}")

    hits: list[ApiHit] = []
    for name, member in _iter_public_members(module):
        qualname = f"{module_name}.{name}"
        _record_if_match(hits, module_name, qualname, member, keywords)
        if recurse_classes and inspect.isclass(member):
            for child_name, child in _iter_public_members(member):
                child_qualname = f"{qualname}.{child_name}"
                _record_if_match(hits, module_name, child_qualname, child, keywords)
    return (hits, None)


def discover_child_modules(module_name: str, keywords: tuple[str, ...], limit: int) -> list[str]:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return []
    paths = getattr(module, "__path__", None)
    if paths is None:
        return []

    found: list[str] = []
    for info in pkgutil.walk_packages(paths, prefix=f"{module_name}."):
        if _contains_keyword(info.name, keywords):
            found.append(info.name)
        if len(found) >= limit:
            break
    return found


def render_report(
    hits_by_module: dict[str, list[ApiHit]],
    import_errors: dict[str, str],
    *,
    keywords: tuple[str, ...],
    child_modules: dict[str, list[str]],
) -> str:
    lines = [
        "# ADS Python API Probe",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Python: `{sys.executable}`",
        f"Keywords: `{', '.join(keywords)}`",
        "",
    ]

    if import_errors:
        lines.append("## Import Errors")
        lines.append("")
        for module, error in sorted(import_errors.items()):
            lines.append(f"- `{module}`: {error}")
        lines.append("")

    if child_modules:
        lines.append("## Keyword Child Modules")
        lines.append("")
        for module, children in sorted(child_modules.items()):
            if not children:
                continue
            lines.append(f"### `{module}`")
            lines.extend(f"- `{child}`" for child in children)
            lines.append("")

    lines.append("## API Hits")
    lines.append("")
    for module, hits in sorted(hits_by_module.items()):
        lines.append(f"### `{module}`")
        lines.append("")
        if not hits:
            lines.append("_No keyword hits._")
            lines.append("")
            continue
        lines.append("| Object | Kind | Signature | Doc |")
        lines.append("|---|---|---|---|")
        for hit in sorted(hits, key=lambda item: item.qualname.lower()):
            signature = hit.signature.replace("|", "\\|")
            doc = hit.doc.replace("|", "\\|")
            lines.append(f"| `{hit.qualname}` | {hit.kind} | `{signature}` | {doc} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe ADS Python APIs for objects matching keywords.")
    parser.add_argument("--module", action="append", dest="modules", help="Module to inspect. May be repeated.")
    parser.add_argument("--keyword", action="append", dest="keywords", help="Keyword to search. May be repeated.")
    parser.add_argument("--discover", action="store_true", help="Also discover child module names matching keywords.")
    parser.add_argument("--discover-limit", type=int, default=80)
    parser.add_argument("--out", type=Path, default=None, help="Markdown report path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modules = tuple(args.modules or DEFAULT_MODULES)
    keywords = tuple(args.keywords or DEFAULT_KEYWORDS)

    hits_by_module: dict[str, list[ApiHit]] = {}
    import_errors: dict[str, str] = {}
    child_modules: dict[str, list[str]] = {}

    for module in modules:
        hits, error = probe_module(module, keywords)
        hits_by_module[module] = hits
        if error:
            import_errors[module] = error
        if args.discover:
            child_modules[module] = discover_child_modules(module, keywords, args.discover_limit)

    report = render_report(
        hits_by_module,
        import_errors,
        keywords=keywords,
        child_modules=child_modules,
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
