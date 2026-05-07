"""Placeholder handlers for DOCX deterministic fill."""

from __future__ import annotations


def coerce_placeholder_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)

