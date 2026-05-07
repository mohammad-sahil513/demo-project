"""Post-process exported DOCX so page 1 is title-only, page 2 is TOC-only, page 3+ is body."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from core.config import settings

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _w(tag: str) -> str:
    return f"{{{_W}}}{tag}"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _p_style_val(p: ET.Element) -> str | None:
    if _local(p.tag) != "p":
        return None
    ppr = p.find(_w("pPr"))
    if ppr is None:
        return None
    ps = ppr.find(_w("pStyle"))
    if ps is None:
        return None
    val = ps.get(_w("val"))
    if val is None:
        val = ps.get("{%s}val" % _W)  # type: ignore[str-format]
    return str(val).strip() if val else None


def _is_title_style_para(p: ET.Element) -> bool:
    if _local(p.tag) != "p":
        return False
    val = (_p_style_val(p) or "").lower()
    return val in {"title", "subtitle", "cover"}


def _paragraph_text(p: ET.Element) -> str:
    parts: list[str] = []
    for t in p.iter():
        if _local(t.tag) == "t":
            if t.text:
                parts.append(t.text)
            if t.tail:
                parts.append(t.tail)
    return "".join(parts).strip()


def _is_empty_paragraph(p: ET.Element) -> bool:
    if _local(p.tag) != "p":
        return False
    if _is_page_break_only_paragraph(p) or _has_toc_field(p):
        return False
    return _paragraph_text(p) == "" and not _paragraph_has_non_empty_run_content(p)


def _paragraph_has_non_empty_run_content(p: ET.Element) -> bool:
    """True if paragraph has images, drawings, fldChar, instrText, tab, etc."""
    for child in p.iter():
        loc = _local(child.tag)
        if loc in {"drawing", "pict", "object", "fldChar", "instrText", "fldSimple", "sym", "tab"}:
            return True
        if loc == "br":
            br_type = child.get(_w("type"))
            if br_type is None:
                br_type = child.get("{%s}type" % _W)
            if br_type != "page":
                return True
    return False


def _is_page_break_only_paragraph(p: ET.Element) -> bool:
    if _local(p.tag) != "p":
        return False
    if _p_style_val(p) is not None:
        return False
    runs = [c for c in p if _local(c.tag) == "r"]
    if len(runs) != 1:
        return False
    r = runs[0]
    brs = [c for c in r if _local(c.tag) == "br"]
    if len(brs) != 1:
        return False
    b = brs[0]
    t = b.get(_w("type")) or b.get("{%s}type" % _W)
    return t == "page"


def _has_toc_field(p: ET.Element) -> bool:
    if _local(p.tag) != "p":
        return False
    for el in p.iter():
        if _local(el.tag) == "instrText":
            txt = (el.text or "").strip()
            if txt.upper().startswith("TOC"):
                return True
        if _local(el.tag) == "fldSimple":
            instr = el.get(_w("instr")) or el.get("{%s}instr" % _W) or ""
            if "TOC" in instr.upper():
                return True
    return False


def _make_title_paragraph(*, title_text: str) -> ET.Element:
    p = ET.Element(_w("p"))
    ppr = ET.SubElement(p, _w("pPr"))
    ps = ET.SubElement(ppr, _w("pStyle"))
    ps.set(_w("val"), "Title")
    jc = ET.SubElement(ppr, _w("jc"))
    jc.set(_w("val"), "center")
    r = ET.SubElement(p, _w("r"))
    t = ET.SubElement(r, _w("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = title_text
    return p


def _make_page_break_paragraph() -> ET.Element:
    p = ET.Element(_w("p"))
    r = ET.SubElement(p, _w("r"))
    br = ET.SubElement(r, _w("br"))
    br.set(_w("type"), "page")
    return p


def _make_toc_paragraph() -> ET.Element:
    """Match python-docx field structure from docx_builder._add_toc."""
    p = ET.Element(_w("p"))
    r = ET.SubElement(p, _w("r"))

    fld_begin = ET.SubElement(r, _w("fldChar"))
    fld_begin.set(_w("fldCharType"), "begin")

    instr = ET.SubElement(r, _w("instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'

    fld_separate = ET.SubElement(r, _w("fldChar"))
    fld_separate.set(_w("fldCharType"), "separate")

    fld_text = ET.SubElement(r, _w("t"))
    fld_text.text = "Table of Contents"

    fld_end = ET.SubElement(r, _w("fldChar"))
    fld_end.set(_w("fldCharType"), "end")
    return p


def _split_body_children(body: ET.Element) -> tuple[list[ET.Element], ET.Element | None]:
    children = list(body)
    sect_pr: ET.Element | None = None
    elems: list[ET.Element] = []
    for ch in children:
        if _local(ch.tag) == "sectPr":
            sect_pr = ch
        else:
            elems.append(ch)
    return elems, sect_pr


def _rebuild_body(body: ET.Element, elems: list[ET.Element], sect_pr: ET.Element | None) -> None:
    for c in list(body):
        body.remove(c)
    for el in elems:
        body.append(el)
    if sect_pr is not None:
        body.append(sect_pr)


def _serialize_document(root: ET.Element) -> bytes:
    decl = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    ET.register_namespace("w", _W)
    body = ET.tostring(root, encoding="utf-8", default_namespace=None)
    return decl + body


def _rewrite_document_xml(docx_path: Path, new_xml: bytes) -> None:
    inner = "word/document.xml"
    tmp = docx_path.with_suffix(docx_path.suffix + ".~struct")
    with ZipFile(docx_path, "r") as zin, ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = new_xml if info.filename == inner else zin.read(info.filename)
            ni = ZipInfo(filename=info.filename, date_time=info.date_time)
            ni.compress_type = ZIP_DEFLATED
            ni.external_attr = info.external_attr
            zout.writestr(ni, data)
    tmp.replace(docx_path)


def _title_end_index(elems: list[ET.Element]) -> int:
    i = 0
    while i < len(elems) and _local(elems[i].tag) == "p" and _is_title_style_para(elems[i]):
        i += 1
    return i


def _find_toc_index(elems: list[ET.Element], start: int) -> int | None:
    for j in range(start, len(elems)):
        if _local(elems[j].tag) == "p" and _has_toc_field(elems[j]):
            return j
    return None


def enforce_title_toc_pagination(
    docx_path: Path,
    *,
    doc_title: str,
    doc_type: str,
) -> list[dict[str, object]]:
    """
    Ensure document.xml has: title block (page 1) | page break | TOC (page 2) | page break | body.

    Returns workflow-style warning dicts (phase RENDER_EXPORT).
    """
    warnings: list[dict[str, object]] = []
    if not getattr(settings, "template_docx_structure_fixer_enabled", True):
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_fixer_disabled",
                "message": "DOCX structure fixer skipped (TEMPLATE_DOCX_STRUCTURE_FIXER_ENABLED=false).",
            },
        )
        return warnings

    path = Path(docx_path)
    if not path.is_file():
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_fixer_skipped",
                "message": f"DOCX not found at {path}.",
            },
        )
        return warnings

    inner = "word/document.xml"
    with ZipFile(path, "r") as zf:
        try:
            raw = zf.read(inner)
        except KeyError:
            warnings.append(
                {
                    "phase": "RENDER_EXPORT",
                    "code": "docx_structure_fixer_skipped",
                    "message": "word/document.xml missing.",
                },
            )
            return warnings

    root = ET.fromstring(raw)
    body = root.find(f".//{_w('body')}")
    if body is None:
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_fixer_skipped",
                "message": "w:body not found.",
            },
        )
        return warnings

    elems, sect_pr = _split_body_children(body)
    dirty = False

    stem = Path(doc_title).stem or doc_title or "Document"
    generated_title = f"{stem} — {doc_type}"

    # 1) Title block from start
    te = _title_end_index(elems)
    if te == 0:
        elems.insert(0, _make_title_paragraph(title_text=generated_title))
        te = 1
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_title_inserted",
                "message": "Inserted Title paragraph at start (no Title/Subtitle/Cover block found).",
            },
        )

    # Strip empty paragraphs immediately after title
    while te < len(elems) and _local(elems[te].tag) == "p" and _is_empty_paragraph(elems[te]) and not _has_toc_field(
        elems[te],
    ):
        del elems[te]
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_empty_paragraph_removed",
                "message": "Removed empty paragraph after title block.",
            },
        )

    # 2) Exactly one page break after title (index te)
    if te >= len(elems) or not _is_page_break_only_paragraph(elems[te]):
        elems.insert(te, _make_page_break_paragraph())
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_pagebreak_inserted",
                "location": "after_title",
                "message": "Inserted page break after title block.",
            },
        )
    while te + 1 < len(elems) and _is_page_break_only_paragraph(elems[te + 1]):
        del elems[te + 1]
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_extra_pagebreak_removed",
                "message": "Removed duplicate page break after title.",
            },
        )

    # 3) TOC at te + 1
    toc_idx = _find_toc_index(elems, te + 1)
    orphans: list[ET.Element] = []
    if toc_idx is None:
        elems.insert(te + 1, _make_toc_paragraph())
        toc_idx = te + 1
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_toc_inserted",
                "message": "Inserted TOC field paragraph after title page break.",
            },
        )
    elif toc_idx > te + 1:
        orphans = list(elems[te + 1 : toc_idx])
        del elems[te + 1 : toc_idx]
        toc_idx = te + 1
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_preface_orphans_relocated",
                "message": "Moved paragraphs between title page break and TOC to after TOC section.",
            },
        )

    toc_end = toc_idx + 1

    # Strip empties after TOC paragraph
    while toc_end < len(elems) and _local(elems[toc_end].tag) == "p" and _is_empty_paragraph(elems[toc_end]):
        del elems[toc_end]
        dirty = True

    # 4) Page break after TOC
    if toc_end >= len(elems) or not _is_page_break_only_paragraph(elems[toc_end]):
        elems.insert(toc_end, _make_page_break_paragraph())
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_pagebreak_inserted",
                "location": "after_toc",
                "message": "Inserted page break after TOC.",
            },
        )
    while toc_end + 1 < len(elems) and _is_page_break_only_paragraph(elems[toc_end + 1]):
        del elems[toc_end + 1]
        dirty = True
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_extra_pagebreak_removed",
                "message": "Removed duplicate page break after TOC.",
            },
        )

    content_start = toc_end + 1
    insert_at = content_start
    for orphan in orphans:
        elems.insert(insert_at, orphan)
        insert_at += 1

    if not dirty:
        warnings.append(
            {
                "phase": "RENDER_EXPORT",
                "code": "docx_structure_unmodified",
                "message": "DOCX already matched title / TOC / body pagination.",
            },
        )
        return warnings

    _rebuild_body(body, elems, sect_pr)
    new_xml = _serialize_document(root)
    _rewrite_document_xml(path, new_xml)
    return warnings
