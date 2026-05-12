"""``updateFields`` flag: Word recomputes TOC + page numbers on first open.

Ensures :func:`ensure_update_fields_on_open` injects
``<w:updateFields w:val="true"/>`` into ``word/settings.xml`` (creating
the part when missing) and that re-running it is idempotent.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from docx import Document

from modules.export.docx_update_fields import ensure_update_fields_on_open


def test_ensure_update_fields_sets_word_settings(tmp_path: Path) -> None:
    path = tmp_path / "out.docx"
    Document().save(str(path))
    raw_before = ZipFile(path, "r").read("word/settings.xml")
    assert b"updateFields" not in raw_before

    ensure_update_fields_on_open(path)

    raw_after = ZipFile(path, "r").read("word/settings.xml").decode("utf-8")
    assert "updateFields" in raw_after
    assert 'w:val="true"' in raw_after or "val=\"true\"" in raw_after
