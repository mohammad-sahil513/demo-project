from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from docx import Document

from modules.template.docx_template_normalize import apply_docx_template_normalize


def test_normalize_trims_extra_table_rows(tmp_path: Path) -> None:
    p = tmp_path / "n.docx"
    doc = Document()
    t = doc.add_table(rows=4, cols=2)
    for i in range(4):
        for j, cell in enumerate(t.rows[i].cells):
            cell.text = f"{i},{j}"
    doc.save(p)
    w = apply_docx_template_normalize(p)
    assert any(x.get("code") == "normalize_table_rows_trimmed" for x in w)
    raw = ZipFile(p, "r").read("word/document.xml").decode("utf-8")
    assert raw.count("<w:tr") == 2
