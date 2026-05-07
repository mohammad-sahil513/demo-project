"""DOCX schema extractor for placeholder and fidelity anchors."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from core.exceptions import TemplateException
from modules.template.schema_models import PlaceholderDef, PlaceholderLocation, TemplateSchema

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
_TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")


def extract_docx_schema(template_path: Path) -> TemplateSchema:
    try:
        with ZipFile(template_path, "r") as archive:
            file_names = set(archive.namelist())
            document_xml = archive.read("word/document.xml")
            header_parts = sorted(name for name in file_names if name.startswith("word/header") and name.endswith(".xml"))
            footer_parts = sorted(name for name in file_names if name.startswith("word/footer") and name.endswith(".xml"))
            rel_parts = sorted(name for name in file_names if name.startswith("word/_rels/") and name.endswith(".rels"))
            media_parts = sorted(name for name in file_names if name.startswith("word/media/"))
    except KeyError as exc:
        raise TemplateException("Invalid DOCX template: missing word/document.xml") from exc

    root = ET.fromstring(document_xml)
    placeholders: list[PlaceholderDef] = []
    seen: set[str] = set()

    for idx, paragraph in enumerate(root.findall(".//w:p", _WORD_NS), start=1):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", _WORD_NS)).strip()
        if not text:
            continue
        for match in _TOKEN_RE.finditer(text):
            token = match.group(1).strip()
            if token in seen:
                continue
            seen.add(token)
            placeholders.append(
                PlaceholderDef(
                    placeholder_id=token,
                    kind="text",
                    required=True,
                    location=PlaceholderLocation(
                        part="word/document.xml",
                        xml_path=f"/w:document/w:body/w:p[{idx}]",
                        context=text[:200],
                        mask_scope="text_tokens",
                    ),
                )
            )

    # Content controls become deterministic placeholders too.
    for idx, sdt in enumerate(root.findall(".//w:sdt", _WORD_NS), start=1):
        alias_node = sdt.find(".//w:alias", _WORD_NS)
        tag_node = sdt.find(".//w:tag", _WORD_NS)
        alias = (alias_node.attrib.get(f'{{{_WORD_NS["w"]}}}val') if alias_node is not None else None) or ""
        tag = (tag_node.attrib.get(f'{{{_WORD_NS["w"]}}}val') if tag_node is not None else None) or ""
        placeholder_id = (tag or alias).strip()
        if not placeholder_id or placeholder_id in seen:
            continue
        seen.add(placeholder_id)
        placeholders.append(
            PlaceholderDef(
                placeholder_id=placeholder_id,
                kind="rich_text",
                required=True,
                location=PlaceholderLocation(
                    part="word/document.xml",
                    xml_path=f"/w:document//w:sdt[{idx}]",
                    context=alias or tag or "content-control",
                    mask_scope="content_control",
                ),
            )
        )

    # Bookmark placeholders (true OOXML range boundaries).
    for idx, bookmark in enumerate(root.findall(".//w:bookmarkStart", _WORD_NS), start=1):
        name = (bookmark.attrib.get(f'{{{_WORD_NS["w"]}}}name') or "").strip()
        if not name or name.startswith("_"):
            continue
        if name in seen:
            continue
        seen.add(name)
        placeholders.append(
            PlaceholderDef(
                placeholder_id=name,
                kind="rich_text",
                required=True,
                location=PlaceholderLocation(
                    part="word/document.xml",
                    xml_path=f"/w:document//w:bookmarkStart[{idx}]",
                    context=name,
                    mask_scope="bookmark_range",
                ),
            )
        )

    return TemplateSchema(
        source_format="docx",
        placeholders=placeholders,
        locked_fidelity_anchors={
            "header_parts": header_parts,
            "footer_parts": footer_parts,
            "relationship_parts": rel_parts,
            "media_parts": media_parts,
        },
    )

