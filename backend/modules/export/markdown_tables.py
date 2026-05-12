"""Compatibility layer for the older table-centric markdown parser.

Older code paths only cared whether a chunk of generated content was
"text" or "table". We now have a richer :mod:`content_blocks` parser, but
the builder/filler/xlsx writers still want the two-kind view. This module
adapts the rich block list back into the simpler shape, normalizing GFM
tables into a canonical pipe representation along the way.
"""
from __future__ import annotations

from typing import Literal

from modules.export.content_blocks import (
    ContentBlock,
    parse_content_blocks,
    parse_gfm_table,
    parse_html_table,
)

BlockKind = Literal["text", "table"]

def _rows_to_pipe_table(rows: list[list[str]]) -> str:
    """
    Convert parsed rows into a clean GitHub-flavored markdown pipe table string.
    """
    if not rows:
        return ""

    header = rows[0]
    header_line = "| " + " | ".join(str(cell) for cell in header) + " |"
    separator_line = "| " + " | ".join("---" for _ in header) + " |"

    lines = [header_line, separator_line]

    for row in rows[1:]:
        normalized_row = [str(cell) for cell in row]
        lines.append("| " + " | ".join(normalized_row) + " |")

    return "\n".join(lines)


def split_markdown_blocks(content: str) -> list[tuple[BlockKind, str]]:
    """
    Backward-compatible API used by current builder/filler/xlsx code.

    Notes:
    - headings, images, captions, lists, and HTML tables are detected by the
      richer semantic parser, but for backward compatibility this function maps:
        * gfm/html tables -> ("table", normalized table text)
        * everything else -> ("text", plain text payload)
    """
    blocks = parse_content_blocks(content)
    out: list[tuple[BlockKind, str]] = []

    for block in blocks:
        if block.kind in {"table_gfm", "table_html"}:
            normalized = block.text or _rows_to_pipe_table(block.rows)
            if block.rows:
                normalized = _rows_to_pipe_table(block.rows)
            out.append(("table", normalized))
            continue

        if block.kind == "heading":
            hashes = "#" * max(block.level, 1)
            out.append(("text", f"{hashes} {block.text}".strip()))
            continue

        if block.kind == "bullet_list":
            out.append(("text", "\n".join(f"- {item}" for item in block.items)))
            continue

        if block.kind == "numbered_list":
            out.append(("text", "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(block.items))))
            continue

        if block.kind == "image":
            payload = block.text or (block.image_target or "")
            out.append(("text", payload))
            continue

        if block.kind == "caption":
            out.append(("text", block.text))
            continue

        # paragraph and any fallback kinds
        out.append(("text", block.text))

    return out


__all__ = [
    "ContentBlock",
    "BlockKind",
    "parse_content_blocks",
    "parse_gfm_table",
    "parse_html_table",
    "split_markdown_blocks",
]
