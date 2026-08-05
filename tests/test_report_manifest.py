from pathlib import Path

import pytest

from simads.reports import ReportManifestError, build_report_manifest, write_report_manifest


def test_build_report_manifest_collects_html_assets(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    assets = report_dir / "assets"
    assets.mkdir(parents=True)
    (assets / "plot.svg").write_text("<svg />", encoding="utf-8")
    (assets / "bg.png").write_bytes(b"png")
    (report_dir / "index.html").write_text(
        """
        <html>
          <head><style>.hero { background: url("assets/bg.png"); }</style></head>
          <body>
            <img src="assets/plot.svg">
            <a href="#local">local</a>
            <a href="https://example.test/report">external</a>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    payload = build_report_manifest(report_dir)

    assert payload["status"] == "ok"
    assert payload["referenced_assets"] == ["assets/bg.png", "assets/plot.svg"]
    assert payload["missing_references"] == []
    assert len(payload["skipped_references"]) == 2


def test_report_manifest_rejects_missing_asset(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    (report_dir / "index.html").write_text('<img src="assets/missing.svg">', encoding="utf-8")

    payload = build_report_manifest(report_dir)

    assert payload["status"] == "failed"
    assert payload["missing_references"][0]["local_path"] == "assets/missing.svg"
    with pytest.raises(ReportManifestError, match="missing local reference"):
        write_report_manifest(report_dir)


def test_report_manifest_rejects_outside_asset(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    (tmp_path / "outside.svg").write_text("<svg />", encoding="utf-8")
    (report_dir / "index.html").write_text('<img src="../outside.svg">', encoding="utf-8")

    payload = build_report_manifest(report_dir)

    assert payload["status"] == "failed"
    assert payload["outside_report_dir_references"][0]["uri"] == "../outside.svg"
    with pytest.raises(ReportManifestError, match="outside report_dir"):
        write_report_manifest(report_dir)
