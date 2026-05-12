"""Drop document title / front-matter headings before section planning (generic heuristics).

Many uploaded templates begin with cover-page text and a "Document
Information" / "Revision History" block before the real Section 1. Those
front-matter headings should not be part of the workflow's generation plan;
they're metadata, not content the LLM needs to write.

The filter walks the heading list forward until it finds either a heading
called ``Introduction`` or one with explicit numbering — that index becomes
the main-body start. Everything before it is dropped.
"""

from __future__ import annotations

import re

from modules.template.models import DocumentSkeleton, ExtractedHeading

_INTRO_RE = re.compile(r"(?i)^introduction\b")
_NUMBERED_HEADING_RE = re.compile(r"^\d+(?:\.\d+)*\s+\S")


def _main_body_start_index(items: list[ExtractedHeading]) -> int:
    """
    Index of the first heading that begins the main body.

    Prefer:
    1. A heading titled Introduction (word boundary).
    2. A heading with extracted list numbering (e.g. 1, 2.1) or leading numbered text (1 word...).
    """
    for i, item in enumerate(items):
        raw = item.text.strip()
        if _INTRO_RE.match(raw):
            return i
        if item.numbering is not None:
            return i
        if _NUMBERED_HEADING_RE.match(raw):
            return i

    return 0


def all_heading_items_from_skeleton(skeleton: DocumentSkeleton) -> list[ExtractedHeading]:
    """All extracted headings in document order (no front-matter trimming)."""
    if skeleton.heading_items:
        return list(skeleton.heading_items)
    return [
        ExtractedHeading(
            text=heading,
            level=1,
            order=index + 1,
            style_name=None,
            numbering=None,
        )
        for index, heading in enumerate(skeleton.headings)
    ]


def filter_heading_items_for_section_plan(items: list[ExtractedHeading]) -> list[ExtractedHeading]:
    """Return headings that participate in workflow section planning (stable ExtractedHeading.order)."""
    if not items:
        return items
    start = _main_body_start_index(items)
    filtered = items[start:]
    return filtered if filtered else items
