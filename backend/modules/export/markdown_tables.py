"""Split markdown prose into text blocks and GFM pipe tables."""

from __future__ import annotations

import re
from typing import Literal

BlockKind = Literal["text", "table"]


def _is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 2


def _is_separator_row(line: str) -> bool:
    s = line.strip().strip("|").replace(" ", "")
    if not s:
        return False
    parts = [p for p in s.split("|") if p]
    return bool(parts) and all(re.fullmatch(r":?-{3,}:?", p) is not None for p in parts)


def parse_gfm_table(block: str) -> list[list[str]]:
    raw_lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip()]
    table_lines = [ln for ln in raw_lines if _is_table_line(ln)]
    if len(table_lines) >= 2 and _is_separator_row(table_lines[1]):
        table_lines.pop(1)
    rows: list[list[str]] = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def split_markdown_blocks(content: str) -> list[tuple[BlockKind, str]]:
    """Return ordered (kind, payload) where payload is prose or raw table lines."""
    lines = content.splitlines()
    blocks: list[tuple[BlockKind, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _is_table_line(line):
            start = i
            while i < len(lines) and _is_table_line(lines[i]):
                i += 1
            blocks.append(("table", "\n".join(lines[start:i])))
            continue
        if not line.strip():
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_table_line(lines[i]):
            i += 1
        blocks.append(("text", "\n".join(lines[start:i]).strip()))
    return blocks
