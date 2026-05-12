"""In-place DOCX OOXML placeholder fill — preserves tables, images, non-target regions.

The placeholder-native fill path: unzip the template, parse the parts
that contain placeholder anchors (``word/document.xml``, headers,
footers), and rewrite **only** the targeted nodes. Everything else is
copied byte-for-byte back into the output zip, which is what gives this
path its strict fidelity guarantee.

Two location strategies are supported via the schema:

- **Absolute XPath** (``/w:document/w:body/w:p[N]``) for paragraph-level
  token replacement (``{{ token }}``).
- **Descendant XPath** for content controls and bookmark ranges where
  the anchor is identified by node type rather than exact position.

The token regex is built per-placeholder so the writer can replace a
single token without affecting any other token sharing a paragraph. XML
text values are escaped via :func:`_escape_xml_text` to keep the output
spec-compliant.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from modules.assembly.models import AssembledDocument
from modules.export.docx_integrity import _find_nodes_by_absolute_path, _find_nodes_by_descendant_path

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_W_MAIN = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_TOKEN_RE_TEMPLATE = r"\{\{\s*%s\s*\}\}"


def _build_parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    m: dict[ET.Element, ET.Element] = {}
    for parent in root.iter():
        for child in list(parent):
            m[child] = parent
    return m


def _escape_xml_text(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _new_paragraph_with_text(plain: str) -> ET.Element:
    p = ET.Element(f"{{{_W_MAIN}}}p")
    r = ET.SubElement(p, f"{{{_W_MAIN}}}r")
    t = ET.SubElement(r, f"{{{_W_MAIN}}}t")
    t.text = plain
    return p


def _clear_sdt_content_and_set_text(sdt: ET.Element, plain: str) -> None:
    sdtc = sdt.find(f"{{{_W_MAIN}}}sdtContent")
    if sdtc is None:
        return
    for child in list(sdtc):
        sdtc.remove(child)
    sdtc.append(_new_paragraph_with_text(plain))


def _replace_path_node_text(node: ET.Element, plain: str) -> None:
    texts = node.findall(".//w:t", _WORD_NS)
    if not texts:
        return
    texts[0].text = plain
    for extra in texts[1:]:
        extra.text = ""


def _fill_bookmark_range(
    parent: ET.Element,
    bookmark_start: ET.Element,
    plain: str,
) -> None:
    bid = (bookmark_start.attrib.get(f"{{{_W_MAIN}}}id") or "").strip()
    if not bid:
        return
    while True:
        kids = list(parent)
        try:
            si = kids.index(bookmark_start)
        except ValueError:
            return
        if si + 1 >= len(kids):
            break
        el = kids[si + 1]
        if el.tag == f"{{{_W_MAIN}}}bookmarkEnd":
            eid = (el.attrib.get(f"{{{_W_MAIN}}}id") or "").strip()
            if eid == bid:
                break
        parent.remove(el)
    kids = list(parent)
    si = kids.index(bookmark_start)
    new_p = _new_paragraph_with_text(plain)
    parent.insert(si + 1, new_p)


def _find_ancestor_tbl(pmap: dict[ET.Element, ET.Element], node: ET.Element) -> ET.Element | None:
    cur: ET.Element | None = node
    while cur is not None:
        if cur.tag == f"{{{_W_MAIN}}}tbl":
            return cur
        cur = pmap.get(cur)
    return None


def _fill_table_first_data_row(table: ET.Element, rows: list[list[str]]) -> None:
    trs = table.findall("w:tr", _WORD_NS)
    if len(trs) < 2:
        return
    data_row = trs[1]
    cells = data_row.findall("w:tc", _WORD_NS)
    if not rows or not rows[0]:
        return
    src = rows[0]
    for idx, tc in enumerate(cells):
        val = src[idx] if idx < len(src) else ""
        for t in tc.findall(".//w:t", _WORD_NS):
            t.text = ""
        ts = tc.findall(".//w:t", _WORD_NS)
        if ts:
            ts[0].text = val


def _parse_simple_markdown_table(content: str) -> list[list[str]]:
    lines = [ln.strip() for ln in (content or "").splitlines() if ln.strip()]
    rows: list[list[str]] = []
    for ln in lines:
        if "|" not in ln:
            continue
        if re.match(r"^\|?[\s\-:|]+\|", ln):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(cells)
    return rows


def _apply_placeholder_to_tree(
    root: ET.Element,
    ph: dict[str, object],
    text: str,
    *,
    output_type: str,
    pmap: dict[ET.Element, ET.Element],
) -> None:
    loc = ph.get("location") if isinstance(ph.get("location"), dict) else {}
    xml_path = str(loc.get("xml_path") or "").strip()
    mask_scope = str(loc.get("mask_scope") or "path_node").strip()
    pid = str(ph.get("placeholder_id") or "").strip()
    kind = str(ph.get("kind") or "text").strip()

    if not xml_path or not pid:
        return

    if mask_scope == "text_tokens":
        pat = re.compile(_TOKEN_RE_TEMPLATE % re.escape(pid))
        for t in root.findall(".//w:t", _WORD_NS):
            if t.text:
                t.text = pat.sub(_escape_xml_text(text), t.text)
        return

    if "//" in xml_path:
        nodes = _find_nodes_by_descendant_path(root, xml_path)
    else:
        nodes = _find_nodes_by_absolute_path(root, xml_path)

    if not nodes:
        return
    node = nodes[0]

    if mask_scope == "content_control" and node.tag == f"{{{_W_MAIN}}}sdt":
        _clear_sdt_content_and_set_text(node, text)
        return

    if mask_scope == "bookmark_range" and node.tag == f"{{{_W_MAIN}}}bookmarkStart":
        parent = pmap.get(node)
        if parent is not None:
            _fill_bookmark_range(parent, node, text)
        return

    if kind == "table" or output_type == "table":
        tbl = node if node.tag == f"{{{_W_MAIN}}}tbl" else _find_ancestor_tbl(pmap, node)
        if tbl is not None:
            rows = _parse_simple_markdown_table(text)
            _fill_table_first_data_row(tbl, rows)
            return

    _replace_path_node_text(node, text)


def fill_docx_placeholders_native(
    *,
    template_path: Path,
    output_path: Path,
    assembled: AssembledDocument,
    placeholder_schema: dict[str, object],
    section_placeholder_map: dict[str, list[str]],
) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    raw_ph = placeholder_schema.get("placeholders")
    if not isinstance(raw_ph, list):
        warnings.append(
            {
                "code": "native_fill_no_placeholders",
                "severity": "warning",
                "message": "placeholder_schema.placeholders missing or invalid.",
            }
        )
        return warnings

    by_id: dict[str, dict[str, object]] = {}
    for item in raw_ph:
        if isinstance(item, dict):
            pid = str(item.get("placeholder_id") or "").strip()
            if pid:
                by_id[pid] = item

    parts_to_edit: set[str] = set()
    for ph in by_id.values():
        loc = ph.get("location") if isinstance(ph.get("location"), dict) else {}
        part = str(loc.get("part") or "word/document.xml").strip()
        parts_to_edit.add(part)

    with ZipFile(template_path, "r") as zin:
        names = zin.namelist()
        part_bytes: dict[str, bytes] = {n: zin.read(n) for n in names}

    trees: dict[str, ET.Element] = {}
    parent_maps: dict[str, dict[ET.Element, ET.Element]] = {}
    for part in parts_to_edit:
        if part not in part_bytes:
            warnings.append({"code": "native_fill_part_missing", "severity": "error", "message": part})
            continue
        root = ET.fromstring(part_bytes[part])
        trees[part] = root
        parent_maps[part] = _build_parent_map(root)

    for section in assembled.sections:
        pids = section_placeholder_map.get(section.section_id, [])
        if not pids:
            warnings.append(
                {
                    "code": "native_fill_section_unmapped",
                    "severity": "warning",
                    "section_id": section.section_id,
                    "message": f"No placeholder binding for section {section.section_id!r}; skipped.",
                }
            )
            continue
        body_text = section.content or ""
        for pid in pids:
            ph = by_id.get(pid)
            if not ph:
                continue
            loc = ph.get("location") if isinstance(ph.get("location"), dict) else {}
            part = str(loc.get("part") or "word/document.xml").strip()
            if part not in trees:
                continue
            root = trees[part]
            pmap = parent_maps[part]
            _apply_placeholder_to_tree(
                root,
                ph,
                body_text,
                output_type=section.output_type,
                pmap=pmap,
            )

    out = output_path
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".~nw")
    try:
        with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
            for name in names:
                data = part_bytes[name]
                if name in trees:
                    root = trees[name]
                    decl = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    data = decl + ET.tostring(root, encoding="utf-8")
                info = ZipInfo(filename=name)
                info.compress_type = ZIP_DEFLATED
                zout.writestr(info, data)
        tmp.replace(out)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return warnings
