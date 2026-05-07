from pathlib import Path
from zipfile import ZipFile

from modules.template.schema_extractor_docx import extract_docx_schema


def test_extract_docx_schema_reads_token_placeholder(tmp_path: Path) -> None:
    docx_path = tmp_path / "sample.docx"
    with ZipFile(docx_path, "w") as archive:
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body><w:p><w:r><w:t>{{project_name}}</w:t></w:r></w:p></w:body>
            </w:document>""",
        )
    schema = extract_docx_schema(docx_path)
    assert schema.source_format == "docx"
    assert any(p.placeholder_id == "project_name" for p in schema.placeholders)

