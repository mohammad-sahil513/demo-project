"""Placeholder handlers for XLSX deterministic fill."""

from __future__ import annotations


def coerce_cell_value(value: object) -> str:
    if value is None:
        return ""
    return str(value)

