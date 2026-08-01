#!/usr/bin/env python3
"""Probe AEL words inside an ADS Python context."""

from __future__ import annotations


def probe_words() -> list[tuple[str | None, str, str]]:
    import keysight.ads.ael as ael

    words = [
        "dxf_create_importer",
        "dxf_import_design",
        "gds_create_importer",
        "gds_import_design",
        "gbr_import_design",
        "de_import_design",
    ]
    vocabs = [None, "CmdOp", "AEL", "Design", "Translators", "DXF", "GDS", "Gerber", "dxf", "gds", "gbr"]
    rows: list[tuple[str | None, str, str]] = []
    for vocab in vocabs:
        bridge = ael.call(vocab=vocab) if vocab is not None else ael.call
        for word in words:
            try:
                getattr(bridge, word)
            except Exception as exc:
                rows.append((vocab, word, f"NO: {str(exc).splitlines()[0]}"))
            else:
                rows.append((vocab, word, "OK"))
    return rows


def main() -> None:
    import keysight.edatoolbox.multi_python as multi_python

    with multi_python.ads_context() as ads_ctx:
        rows = ads_ctx.call(probe_words)
    for vocab, word, status in rows:
        print(f"{vocab!r},{word},{status}")


if __name__ == "__main__":
    main()
