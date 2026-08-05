"""Build repeatable report manifests from HTML and local assets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

from simads.runtime.manifest import now_iso, sha256_file, write_json


LOCAL_REF_ATTRS = {"src", "href", "poster"}
SKIPPED_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


class ReportManifestError(ValueError):
    """Raised when a report manifest fails strict validation."""


@dataclass(frozen=True)
class HtmlAssetReference:
    source_html: str
    attribute: str
    uri: str
    local_path: str | None
    exists: bool
    inside_report_dir: bool
    skipped: bool
    skip_reason: str | None = None


class _HtmlReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            attr = name.lower()
            if attr in LOCAL_REF_ATTRS:
                self.references.append((attr, value.strip()))
            elif attr == "style":
                self.references.extend(("style-url", item) for item in _css_urls(value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if "url(" in data.lower():
            self.references.extend(("style-url", item) for item in _css_urls(data))


def _css_urls(text: str) -> list[str]:
    return [match.group(2).strip() for match in CSS_URL_RE.finditer(text) if match.group(2).strip()]


def _is_relative_windows_drive(uri_path: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[/\\]", uri_path))


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _normalize_reference(
    *,
    source_html: Path,
    report_dir: Path,
    attr: str,
    uri: str,
) -> HtmlAssetReference:
    if not uri or uri.startswith("#"):
        return HtmlAssetReference(
            source_html=_rel_posix(source_html, report_dir),
            attribute=attr,
            uri=uri,
            local_path=None,
            exists=False,
            inside_report_dir=False,
            skipped=True,
            skip_reason="document_fragment",
        )

    parsed = urlsplit(uri)
    if parsed.scheme.lower() in SKIPPED_SCHEMES:
        return HtmlAssetReference(
            source_html=_rel_posix(source_html, report_dir),
            attribute=attr,
            uri=uri,
            local_path=None,
            exists=False,
            inside_report_dir=False,
            skipped=True,
            skip_reason=f"scheme:{parsed.scheme.lower()}",
        )
    if parsed.netloc:
        return HtmlAssetReference(
            source_html=_rel_posix(source_html, report_dir),
            attribute=attr,
            uri=uri,
            local_path=None,
            exists=False,
            inside_report_dir=False,
            skipped=True,
            skip_reason="network_path",
        )

    uri_path = unquote(parsed.path)
    if Path(uri_path).is_absolute() or _is_relative_windows_drive(uri_path):
        local = Path(uri_path)
    else:
        local = source_html.parent / uri_path
    resolved = local.resolve()
    inside = _is_inside(resolved, report_dir)
    rel = _rel_posix(resolved, report_dir) if inside else str(resolved)
    return HtmlAssetReference(
        source_html=_rel_posix(source_html, report_dir),
        attribute=attr,
        uri=uri,
        local_path=rel,
        exists=resolved.is_file(),
        inside_report_dir=inside,
        skipped=False,
        skip_reason=None,
    )


def collect_html_asset_references(html_path: Path, *, report_dir: Path | None = None) -> list[HtmlAssetReference]:
    """Collect local HTML asset references and normalize them against a report directory."""

    html_path = html_path.resolve()
    report_dir = (report_dir or html_path.parent).resolve()
    if not _is_inside(html_path, report_dir):
        raise ReportManifestError(f"HTML file is outside report_dir: {html_path}")
    parser = _HtmlReferenceParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    return [
        _normalize_reference(source_html=html_path, report_dir=report_dir, attr=attr, uri=uri)
        for attr, uri in parser.references
    ]


def _file_entry(path: Path, *, report_dir: Path) -> dict[str, Any]:
    rel = path.resolve().relative_to(report_dir.resolve())
    return {
        "path": rel.as_posix(),
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else None,
        "sha256": sha256_file(path),
    }


def _iter_report_files(report_dir: Path, output_path: Path | None) -> Iterable[Path]:
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        if output_path is not None and path.resolve() == output_path.resolve():
            continue
        yield path


def build_report_manifest(
    report_dir: Path,
    *,
    html_files: Iterable[Path] | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable manifest for an HTML report directory."""

    report_dir = report_dir.resolve()
    if not report_dir.is_dir():
        raise ReportManifestError(f"report_dir does not exist or is not a directory: {report_dir}")

    selected_html = list(html_files) if html_files is not None else sorted(report_dir.glob("*.html"))
    if not selected_html:
        raise ReportManifestError(f"no HTML report files found in: {report_dir}")
    selected_html = [path.resolve() if path.is_absolute() else (report_dir / path).resolve() for path in selected_html]
    for html_path in selected_html:
        if not html_path.is_file():
            raise ReportManifestError(f"HTML report file does not exist: {html_path}")
        if not _is_inside(html_path, report_dir):
            raise ReportManifestError(f"HTML report file is outside report_dir: {html_path}")

    refs: list[HtmlAssetReference] = []
    for html_path in selected_html:
        refs.extend(collect_html_asset_references(html_path, report_dir=report_dir))

    referenced_paths = sorted(
        {ref.local_path for ref in refs if not ref.skipped and ref.local_path is not None and ref.inside_report_dir}
    )
    missing = [asdict(ref) for ref in refs if not ref.skipped and ref.inside_report_dir and not ref.exists]
    outside = [asdict(ref) for ref in refs if not ref.skipped and not ref.inside_report_dir]
    skipped = [asdict(ref) for ref in refs if ref.skipped]
    output_resolved = output_path.resolve() if output_path is not None else None

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "report_dir": str(report_dir),
        "html_files": [_rel_posix(path, report_dir) for path in selected_html],
        "files": [_file_entry(path, report_dir=report_dir) for path in _iter_report_files(report_dir, output_resolved)],
        "asset_references": [asdict(ref) for ref in refs],
        "referenced_assets": referenced_paths,
        "missing_references": missing,
        "outside_report_dir_references": outside,
        "skipped_references": skipped,
        "status": "ok" if not missing and not outside else "failed",
        "updated_at": now_iso(),
    }
    return payload


def validate_report_manifest(payload: dict[str, Any]) -> None:
    errors: list[str] = []
    missing = payload.get("missing_references") or []
    outside = payload.get("outside_report_dir_references") or []
    if missing:
        errors.append(f"{len(missing)} missing local reference(s)")
    if outside:
        errors.append(f"{len(outside)} outside report_dir reference(s)")
    if errors:
        raise ReportManifestError("; ".join(errors))


def write_report_manifest(report_dir: Path, *, output_path: Path | None = None, strict: bool = True) -> dict[str, Any]:
    output_path = output_path or (report_dir / "report_manifest.json")
    payload = build_report_manifest(report_dir, output_path=output_path)
    if strict:
        validate_report_manifest(payload)
    write_json(output_path, payload)
    return payload
