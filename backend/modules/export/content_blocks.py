"""Semantic parsing helpers for generated markdown-ish / HTML-ish content."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from typing import Literal

BlockKind = Literal[
    "heading",
    "paragraph",
    "bullet_list",
    "numbered_list",
    "table_gfm",
    "table_html",
    "image",
    "caption",
]


@dataclass(frozen=True, slots=True)
class ContentBlock:
    kind: BlockKind
    text: str = ""
    level: int = 0
    items: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    image_target: str | None = None
    image_alt: str | None = None


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(\\)?(#{1,6})\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*•]\s+(.+?)\s*$")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+?)\s*$")

_MD_IMAGE_INLINE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_MD_IMAGE_REF_RE = re.compile(r"!\[\]\[([^\]]+)\]")
_REF_STYLE_IMAGE_ID_RE = re.compile(r"image_[A-Za-z0-9+/=_\-]+")

_HTML_TABLE_START_RE = re.compile(r"<table\b", flags=re.IGNORECASE)
_HTML_TABLE_END_RE = re.compile(r"</table>", flags=re.IGNORECASE)
_HTML_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", flags=re.IGNORECASE | re.DOTALL)
_HTML_CELL_RE = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", flags=re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")

_IMAGE_PATH_RE = re.compile(
    r"^[^\s]+\.(png|jpg|jpeg|gif|bmp|svg|webp)$",
    flags=re.IGNORECASE,
)

_SEPARATOR_CELL_RE = re.compile(r"^\s*:?-{3,}:?\s*$")

_INTERNAL_CAPTION_PREFIXES = (
    "figure ",
    "diagram ",
    "workflow diagram",
    "architecture diagram",
)


def _strip_html_tags(value: str) -> str:
    cleaned = _HTML_TAG_RE.sub("", value or "")
    cleaned = unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _unwrap_decorative_line(line: str) -> str:
    """
    Remove wrappers such as **_| a | b |_** or **text** when they surround a full line.
    """
    stripped = line.strip()
    wrappers = [
        ("**_", "_**"),
        ("**", "**"),
        ("__", "__"),
        ("_", "_"),
    ]
    for prefix, suffix in wrappers:
        if stripped.startswith(prefix) and stripped.endswith(suffix) and len(stripped) > len(prefix) + len(suffix):
            return stripped[len(prefix):-len(suffix)].strip()
    return stripped


def _is_table_line(line: str) -> bool:
    s = _unwrap_decorative_line(line).strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _split_pipe_row(line: str) -> list[str]:
    s = _unwrap_decorative_line(line).strip().strip("|")
    return [cell.strip() for cell in s.split("|")]


def _is_separator_row(line: str) -> bool:
    parts = _split_pipe_row(line)
    if not parts:
        return False
    return all(_SEPARATOR_CELL_RE.match(part) is not None for part in parts)


# ---------------------------------------------------------------------------
# Public helpers reused by existing code
# ---------------------------------------------------------------------------
def parse_gfm_table(block: str) -> list[list[str]]:
    """
    Parse a GitHub-flavored markdown pipe table into rows/cells.
    """
    raw_lines = [_unwrap_decorative_line(ln.rstrip()) for ln in block.strip().splitlines() if ln.strip()]
    table_lines = [ln for ln in raw_lines if _is_table_line(ln)]
    if not table_lines:
        return []

    rows: list[list[str]] = []
    for idx, line in enumerate(table_lines):
        if idx == 1 and _is_separator_row(line):
            continue
        rows.append(_split_pipe_row(line))
    return rows


def parse_html_table(block: str) -> list[list[str]]:
    """
    Parse a simple HTML table into rows/cells.
    Supports <table><tr><td>/<th> structures commonly leaked by generators.
    """
    rows: list[list[str]] = []
    for row_match in _HTML_ROW_RE.finditer(block):
        row_html = row_match.group(1)
        cells = [_strip_html_tags(cell_html) for cell_html in _HTML_CELL_RE.findall(row_html)]
        if cells:
            rows.append(cells)
    return rows


# ---------------------------------------------------------------------------
# Semantic block parser
# ---------------------------------------------------------------------------
def parse_content_blocks(content: str) -> list[ContentBlock]:
    """
    Parse mixed markdown-ish / HTML-ish generated content into semantic blocks.

    Supports:
    - ATX headings: ## Heading
    - escaped headings: \\## Heading
    - bullet lists
    - numbered lists
    - GFM tables
    - HTML tables
    - markdown images
    - reference-style image tokens like ![][image_xxx]
    - normal paragraphs
    """
    if not content or not content.strip():
        return []

    lines = content.splitlines()
    blocks: list[ContentBlock] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = _unwrap_decorative_line(line).strip()

        if not stripped:
            i += 1
            continue

        # ------------------------------------------------------------------
        # HTML table block
        # ------------------------------------------------------------------
        if _HTML_TABLE_START_RE.search(stripped):
            start = i
            i += 1
            while i < len(lines) and not _HTML_TABLE_END_RE.search(lines[i]):
                i += 1
            if i < len(lines):
                i += 1  # include closing </table>
            block = "\n".join(lines[start:i])
            rows = parse_html_table(block)
            if rows:
                blocks.append(ContentBlock(kind="table_html", rows=rows, text=block))
            continue

        # ------------------------------------------------------------------
        # GFM table block
        # ------------------------------------------------------------------
        if _is_table_line(stripped):
            start = i
            while i < len(lines) and _is_table_line(lines[i]):
                i += 1
            block = "\n".join(lines[start:i])
            rows = parse_gfm_table(block)
            if rows:
                blocks.append(ContentBlock(kind="table_gfm", rows=rows, text=block))
            continue

        # ------------------------------------------------------------------
        # Heading block
        # ------------------------------------------------------------------
        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            hashes = heading_match.group(2)
            text = heading_match.group(3).strip()
            blocks.append(
                ContentBlock(
                    kind="heading",
                    text=text,
                    level=len(hashes),
                )
            )
            i += 1
            continue

        # ------------------------------------------------------------------
        # Markdown image block
        # ------------------------------------------------------------------
        inline_img = _MD_IMAGE_INLINE_RE.search(stripped)
        if inline_img:
            alt = inline_img.group(1).strip()
            target = inline_img.group(2).strip()
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=target,
                    image_alt=alt or None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        ref_img = _MD_IMAGE_REF_RE.search(stripped)
        if ref_img or _REF_STYLE_IMAGE_ID_RE.search(stripped):
            image_id = ref_img.group(1).strip() if ref_img else stripped
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=image_id,
                    image_alt=None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        # ------------------------------------------------------------------
        # Bare image path block
        # ------------------------------------------------------------------
        if _IMAGE_PATH_RE.match(stripped):
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=stripped,
                    image_alt=None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        # ------------------------------------------------------------------
        # Bullet list block
        # ------------------------------------------------------------------
        bullet_match = _BULLET_RE.match(stripped)
        if bullet_match:
            items: list[str] = []
            while i < len(lines):
                candidate = _unwrap_decorative_line(lines[i]).strip()
                m = _BULLET_RE.match(candidate)
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ContentBlock(kind="bullet_list", items=items))
            continue

        # ------------------------------------------------------------------
        # Numbered list block
        # ------------------------------------------------------------------
        numbered_match = _NUMBERED_RE.match(stripped)
        if numbered_match:
            items: list[str] = []
            while i < len(lines):
                candidate = _unwrap_decorative_line(lines[i]).strip()
                m = _NUMBERED_RE.match(candidate)
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ContentBlock(kind="numbered_list", items=items))
            continue

        # ------------------------------------------------------------------
        # Paragraph block
        # ------------------------------------------------------------------
        start = i
        i += 1
        while i < len(lines):
            nxt = _unwrap_decorative_line(lines[i]).strip()
            if not nxt:
                break
            if _HEADING_RE.match(nxt):
                break
            if _is_table_line(nxt):
                break
            if _HTML_TABLE_START_RE.search(nxt):
                break
            if _BULLET_RE.match(nxt):
                break
            if _NUMBERED_RE.match(nxt):
                break
            if _MD_IMAGE_INLINE_RE.search(nxt) or _MD_IMAGE_REF_RE.search(nxt) or _REF_STYLE_IMAGE_ID_RE.search(nxt):
                break
            i += 1

        para_lines = [_unwrap_decorative_line(ln).rstrip() for ln in lines[start:i]]
        para = "\n".join(para_lines).strip()
        if para:
            blocks.append(ContentBlock(kind="paragraph", text=para))

    return blocks
