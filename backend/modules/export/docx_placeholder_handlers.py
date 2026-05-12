"""Placeholder value coercion helpers for DOCX deterministic fill.

The writer only emits ``<w:t>`` text content, so every value must be
coerced to a plain string before being injected. ``None`` becomes an empty
string rather than ``"None"`` to keep absent values invisible in the
output.
"""

from __future__ import annotations


def coerce_placeholder_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)

