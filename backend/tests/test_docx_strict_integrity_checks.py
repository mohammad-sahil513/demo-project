from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from modules.export.docx_integrity import check_docx_integrity


def _write_docx(path: Path, *, header_text: str) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p><w:r><w:t>{{placeholder}}</w:t></w:r></w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
        )
        archive.writestr(
            "word/header1.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
            <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>{header_text}</w:t></w:r></w:p></w:hdr>""",
        )
        archive.writestr(
            "word/footer1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:ftr>""",
        )
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")


def _replace_docx_part(path: Path, part_name: str, payload: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with ZipFile(path, "r") as zin, ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = payload if info.filename == part_name else zin.read(info.filename)
            ni = ZipInfo(filename=info.filename, date_time=info.date_time)
            ni.compress_type = ZIP_DEFLATED
            ni.external_attr = info.external_attr
            zout.writestr(ni, data)
    tmp.replace(path)


def test_docx_integrity_detects_header_footer_drift(tmp_path: Path) -> None:
    template = tmp_path / "template.docx"
    output = tmp_path / "output.docx"
    _write_docx(template, header_text="ACME")
    _write_docx(output, header_text="CHANGED")
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema={})
    assert any(w.get("code") == "docx_header_footer_integrity_failed" for w in warnings)


def test_docx_integrity_allows_declared_placeholder_delta(tmp_path: Path) -> None:
    template = tmp_path / "template_allowed.docx"
    output = tmp_path / "output_allowed.docx"
    _write_docx(template, header_text="ACME")
    _write_docx(output, header_text="ACME")
    # mutate only first paragraph text (declared placeholder path)
    _replace_docx_part(
        output,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p><w:r><w:t>UPDATED_VALUE</w:t></w:r></w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "placeholder",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document/w:body/w:p[1]",
                    "mask_scope": "path_node",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert not any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_blocks_forbidden_document_mutation(tmp_path: Path) -> None:
    template = tmp_path / "template_forbidden.docx"
    output = tmp_path / "output_forbidden.docx"
    _write_docx(template, header_text="ACME")
    _write_docx(output, header_text="ACME")
    # mutate second paragraph text (not declared placeholder path)
    _replace_docx_part(
        output,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p><w:r><w:t>{{placeholder}}</w:t></w:r></w:p>
                <w:p><w:r><w:t>CHANGED_STATIC</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "placeholder",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document/w:body/w:p[1]",
                    "mask_scope": "text_tokens",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_text_token_scope_blocks_non_token_changes(tmp_path: Path) -> None:
    template = tmp_path / "template_scope.docx"
    output = tmp_path / "output_scope.docx"
    _write_docx(template, header_text="ACME")
    _write_docx(output, header_text="ACME")
    # same paragraph, but mutate non-token static text (should fail with text_tokens scope)
    _replace_docx_part(
        output,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p><w:r><w:t>{{placeholder}} EXTRA</w:t></w:r></w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "placeholder",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document/w:body/w:p[1]",
                    "mask_scope": "text_tokens",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_allows_bookmark_range_changes(tmp_path: Path) -> None:
    template = tmp_path / "template_bookmark_allowed.docx"
    output = tmp_path / "output_bookmark_allowed.docx"
    _write_docx(template, header_text="ACME")
    _replace_docx_part(
        template,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p>
                  <w:bookmarkStart w:id="42" w:name="bm_summary"/>
                  <w:r><w:t>OLD_RANGE</w:t></w:r>
                  <w:bookmarkEnd w:id="42"/>
                </w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    with ZipFile(output, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/header1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:hdr>""",
        )
        archive.writestr(
            "word/footer1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:ftr>""",
        )
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p>
                  <w:bookmarkStart w:id="42" w:name="bm_summary"/>
                  <w:r><w:t>NEW_RANGE</w:t></w:r>
                  <w:bookmarkEnd w:id="42"/>
                </w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
        )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "bm_summary",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document//w:bookmarkStart[1]",
                    "mask_scope": "bookmark_range",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert not any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_blocks_changes_outside_bookmark_range(tmp_path: Path) -> None:
    template = tmp_path / "template_bookmark_block.docx"
    output = tmp_path / "output_bookmark_block.docx"
    _write_docx(template, header_text="ACME")
    _replace_docx_part(
        template,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p>
                  <w:bookmarkStart w:id="42" w:name="bm_summary"/>
                  <w:r><w:t>OLD_RANGE</w:t></w:r>
                  <w:bookmarkEnd w:id="42"/>
                </w:p>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    with ZipFile(output, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/header1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:hdr>""",
        )
        archive.writestr(
            "word/footer1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:ftr>""",
        )
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:p>
                  <w:bookmarkStart w:id="42" w:name="bm_summary"/>
                  <w:r><w:t>NEW_RANGE</w:t></w:r>
                  <w:bookmarkEnd w:id="42"/>
                </w:p>
                <w:p><w:r><w:t>CHANGED_STATIC</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
        )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "bm_summary",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document//w:bookmarkStart[1]",
                    "mask_scope": "bookmark_range",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_allows_content_control_range_changes(tmp_path: Path) -> None:
    template = tmp_path / "template_sdt_allowed.docx"
    output = tmp_path / "output_sdt_allowed.docx"
    _write_docx(template, header_text="ACME")
    _replace_docx_part(
        template,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:sdt>
                  <w:sdtPr><w:tag w:val="cc_summary"/></w:sdtPr>
                  <w:sdtContent><w:p><w:r><w:t>OLD_CC</w:t></w:r></w:p></w:sdtContent>
                </w:sdt>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    with ZipFile(output, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/header1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:hdr>""",
        )
        archive.writestr(
            "word/footer1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:ftr>""",
        )
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:sdt>
                  <w:sdtPr><w:tag w:val="cc_summary"/></w:sdtPr>
                  <w:sdtContent><w:p><w:r><w:t>NEW_CC</w:t></w:r></w:p></w:sdtContent>
                </w:sdt>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
        )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "cc_summary",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document//w:sdt[1]",
                    "mask_scope": "content_control",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert not any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)


def test_docx_integrity_blocks_changes_outside_content_control_range(tmp_path: Path) -> None:
    template = tmp_path / "template_sdt_block.docx"
    output = tmp_path / "output_sdt_block.docx"
    _write_docx(template, header_text="ACME")
    _replace_docx_part(
        template,
        "word/document.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:sdt>
                  <w:sdtPr><w:tag w:val="cc_summary"/></w:sdtPr>
                  <w:sdtContent><w:p><w:r><w:t>OLD_CC</w:t></w:r></w:p></w:sdtContent>
                </w:sdt>
                <w:p><w:r><w:t>STATIC_TEXT</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
    )
    with ZipFile(output, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/header1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:hdr>""",
        )
        archive.writestr(
            "word/footer1.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p/></w:ftr>""",
        )
        archive.writestr("word/_rels/document.xml.rels", "<Relationships/>")
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>
                <w:sdt>
                  <w:sdtPr><w:tag w:val="cc_summary"/></w:sdtPr>
                  <w:sdtContent><w:p><w:r><w:t>NEW_CC</w:t></w:r></w:p></w:sdtContent>
                </w:sdt>
                <w:p><w:r><w:t>CHANGED_STATIC</w:t></w:r></w:p>
              </w:body>
            </w:document>""",
        )
    schema = {
        "placeholders": [
            {
                "placeholder_id": "cc_summary",
                "location": {
                    "part": "word/document.xml",
                    "xml_path": "/w:document//w:sdt[1]",
                    "mask_scope": "content_control",
                },
            }
        ]
    }
    warnings = check_docx_integrity(template_path=template, output_path=output, placeholder_schema=schema)
    assert any(w.get("code") == "docx_forbidden_document_xml_mutation" for w in warnings)

