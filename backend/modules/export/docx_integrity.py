"""DOCX package integrity checks for strict template fidelity."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_zip_map(path: Path) -> dict[str, bytes]:
    with ZipFile(path, "r") as archive:
        return {name: archive.read(name) for name in archive.namelist()}


_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")


def _extract_allowed_locations_for_part(
    placeholder_schema: dict[str, object] | None,
    *,
    part: str,
) -> list[dict[str, str]]:
    if not placeholder_schema:
        return []
    raw = placeholder_schema.get("placeholders")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        location = item.get("location")
        if not isinstance(location, dict):
            continue
        if str(location.get("part") or "").strip() != part:
            continue
        xml_path = str(location.get("xml_path") or "").strip()
        mask_scope = str(location.get("mask_scope") or "path_node").strip()
        if xml_path:
            out.append({"xml_path": xml_path, "mask_scope": mask_scope})
    return out


def _parse_segment(segment: str) -> tuple[str, int | None]:
    seg = segment.strip()
    if not seg:
        return "", None
    if "[" in seg and seg.endswith("]"):
        name, idx_str = seg[:-1].split("[", 1)
        try:
            return name, int(idx_str)
        except ValueError:
            return name, None
    return seg, None


def _find_nodes_by_absolute_path(root: ET.Element, xml_path: str) -> list[ET.Element]:
    # Supports patterns like /w:document/w:body/w:p[2]
    segments = [s for s in xml_path.strip().split("/") if s]
    if not segments:
        return []
    first_name, first_idx = _parse_segment(segments[0])
    if first_name != "w:document":
        return []
    candidates = [root]
    if first_idx not in (None, 1):
        return []
    for seg in segments[1:]:
        name, idx = _parse_segment(seg)
        if not name:
            return []
        ns, local = name.split(":", 1) if ":" in name else ("", name)
        qname = f"{{{_WORD_NS.get(ns, '')}}}{local}" if ns else local
        next_candidates: list[ET.Element] = []
        for node in candidates:
            children = [child for child in list(node) if child.tag == qname]
            if idx is None:
                next_candidates.extend(children)
            else:
                if 1 <= idx <= len(children):
                    next_candidates.append(children[idx - 1])
        candidates = next_candidates
        if not candidates:
            return []
    return candidates


def _find_nodes_by_descendant_path(root: ET.Element, xml_path: str) -> list[ET.Element]:
    # Supports patterns like /w:document//w:sdt[1]
    if "//" not in xml_path:
        return []
    tail = xml_path.split("//", 1)[1].strip()
    name, idx = _parse_segment(tail)
    if not name:
        return []
    ns, local = name.split(":", 1) if ":" in name else ("", name)
    qname = f"{{{_WORD_NS.get(ns, '')}}}{local}" if ns else local
    found = root.findall(f".//{qname}")
    if idx is None:
        return found
    if 1 <= idx <= len(found):
        return [found[idx - 1]]
    return []


def _collect_nodes_for_paths(root: ET.Element, xml_paths: list[str]) -> list[ET.Element]:
    nodes: list[ET.Element] = []
    for xml_path in xml_paths:
        if "//" in xml_path:
            nodes.extend(_find_nodes_by_descendant_path(root, xml_path))
        else:
            nodes.extend(_find_nodes_by_absolute_path(root, xml_path))
    return nodes


def _mask_node_text(node: ET.Element) -> None:
    for t in node.findall(".//w:t", _WORD_NS):
        t.text = "__ALLOWED_PLACEHOLDER_DELTA__"


def _mask_text_tokens_only(node: ET.Element) -> None:
    for t in node.findall(".//w:t", _WORD_NS):
        text = t.text or ""
        if _TOKEN_RE.search(text):
            t.text = _TOKEN_RE.sub("__ALLOWED_PLACEHOLDER_DELTA__", text)


def _mask_content_control_range(node: ET.Element) -> None:
    # Prefer strict OOXML content-control payload scope.
    sdt_contents = node.findall(".//w:sdtContent", _WORD_NS)
    if sdt_contents:
        for sdt_content in sdt_contents:
            for t in sdt_content.findall(".//w:t", _WORD_NS):
                t.text = "__ALLOWED_PLACEHOLDER_DELTA__"
        return
    # Fallback for malformed/unexpected structures.
    _mask_node_text(node)


def _mask_bookmark_ranges(root: ET.Element, start_nodes: list[ET.Element]) -> None:
    bookmark_ids: set[str] = set()
    for node in start_nodes:
        bid = (node.attrib.get(f'{{{_WORD_NS["w"]}}}id') or "").strip()
        if bid:
            bookmark_ids.add(bid)
    if not bookmark_ids:
        return

    active: set[str] = set()
    for node in root.iter():
        if node.tag == f'{{{_WORD_NS["w"]}}}bookmarkStart':
            bid = (node.attrib.get(f'{{{_WORD_NS["w"]}}}id') or "").strip()
            if bid in bookmark_ids:
                active.add(bid)
            continue
        if node.tag == f'{{{_WORD_NS["w"]}}}bookmarkEnd':
            bid = (node.attrib.get(f'{{{_WORD_NS["w"]}}}id') or "").strip()
            if bid in active:
                active.remove(bid)
            continue
        if active and node.tag == f'{{{_WORD_NS["w"]}}}t':
            node.text = "__ALLOWED_PLACEHOLDER_DELTA__"


def _document_xml_equal_with_allowed_delta(
    before_xml: bytes,
    after_xml: bytes,
    allowed_locations: list[dict[str, str]],
) -> bool:
    try:
        before_root = ET.fromstring(before_xml)
        after_root = ET.fromstring(after_xml)
    except ET.ParseError:
        return False

    for loc in allowed_locations:
        xml_path = loc.get("xml_path", "")
        mask_scope = loc.get("mask_scope", "path_node")
        if not xml_path:
            continue
        before_nodes = _collect_nodes_for_paths(before_root, [xml_path])
        after_nodes = _collect_nodes_for_paths(after_root, [xml_path])
        if mask_scope == "text_tokens":
            for node in before_nodes:
                _mask_text_tokens_only(node)
            for node in after_nodes:
                _mask_text_tokens_only(node)
        elif mask_scope == "content_control":
            for node in before_nodes:
                _mask_content_control_range(node)
            for node in after_nodes:
                _mask_content_control_range(node)
        elif mask_scope == "bookmark_range":
            _mask_bookmark_ranges(before_root, before_nodes)
            _mask_bookmark_ranges(after_root, after_nodes)
        else:
            for node in before_nodes:
                _mask_node_text(node)
            for node in after_nodes:
                _mask_node_text(node)

    before_norm = ET.tostring(before_root, encoding="utf-8")
    after_norm = ET.tostring(after_root, encoding="utf-8")
    return before_norm == after_norm


def check_docx_integrity(
    *,
    template_path: Path,
    output_path: Path,
    placeholder_schema: dict[str, object] | None,
) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    before = _read_zip_map(template_path)
    after = _read_zip_map(output_path)

    anchors = (placeholder_schema or {}).get("locked_fidelity_anchors")
    anchor_map = anchors if isinstance(anchors, dict) else {}

    header_parts = [str(v) for v in anchor_map.get("header_parts", [])] if isinstance(anchor_map.get("header_parts"), list) else []
    footer_parts = [str(v) for v in anchor_map.get("footer_parts", [])] if isinstance(anchor_map.get("footer_parts"), list) else []
    relationship_parts = [str(v) for v in anchor_map.get("relationship_parts", [])] if isinstance(anchor_map.get("relationship_parts"), list) else []
    media_parts = [str(v) for v in anchor_map.get("media_parts", [])] if isinstance(anchor_map.get("media_parts"), list) else []
    allowed_document_locations = _extract_allowed_locations_for_part(placeholder_schema, part="word/document.xml")

    if not header_parts:
        header_parts = [name for name in before if name.startswith("word/header") and name.endswith(".xml")]
    if not footer_parts:
        footer_parts = [name for name in before if name.startswith("word/footer") and name.endswith(".xml")]
    if not relationship_parts:
        relationship_parts = [name for name in before if name.startswith("word/_rels/") and name.endswith(".rels")]
    if not media_parts:
        media_parts = [name for name in before if name.startswith("word/media/")]

    def compare_exact(parts: list[str], code: str, message: str) -> None:
        drift: list[str] = []
        for part in parts:
            b = before.get(part)
            a = after.get(part)
            if b is None or a is None:
                drift.append(part)
                continue
            if _sha256(b) != _sha256(a):
                drift.append(part)
        if drift:
            warnings.append(
                {
                    "code": code,
                    "severity": "error",
                    "message": message,
                    "parts": sorted(drift),
                }
            )

    compare_exact(
        header_parts + footer_parts,
        "docx_header_footer_integrity_failed",
        "Header/footer structure changed outside allowed placeholder-only mutation.",
    )
    compare_exact(
        relationship_parts,
        "docx_relationship_integrity_failed",
        "DOCX relationship parts changed; media/logo linking may have drifted.",
    )
    compare_exact(
        media_parts,
        "docx_media_integrity_failed",
        "DOCX media assets changed from the source template.",
    )

    before_document = before.get("word/document.xml")
    after_document = after.get("word/document.xml")
    if before_document is None or after_document is None:
        warnings.append(
            {
                "code": "docx_document_part_missing",
                "severity": "error",
                "message": "word/document.xml missing in template or output package.",
            }
        )
    else:
        if not _document_xml_equal_with_allowed_delta(before_document, after_document, allowed_document_locations):
            warnings.append(
                {
                    "code": "docx_forbidden_document_xml_mutation",
                    "severity": "error",
                    "message": "Detected non-placeholder mutation in word/document.xml.",
                }
            )

    return warnings


def summarize_docx_integrity_issues(issues: list[dict[str, object]]) -> dict[str, str]:
    """Map raw integrity issue codes to a small API-friendly summary."""

    codes = {str(i.get("code") or "") for i in issues}

    def bucket(*keys: str) -> str:
        return "fail" if any(k in codes for k in keys if k) else "pass"

    doc_xml_fail_codes = {"docx_forbidden_document_xml_mutation", "docx_document_part_missing"}
    return {
        "overall": "fail" if issues else "pass",
        "header_footer_integrity": bucket("docx_header_footer_integrity_failed"),
        "relationship_integrity": bucket("docx_relationship_integrity_failed"),
        "media_integrity": bucket("docx_media_integrity_failed"),
        "document_xml_integrity": bucket(*doc_xml_fail_codes),
    }

