"""Placeholder value coercion for XLSX deterministic fill.

Excel accepts mixed value types but our placeholder contract is text-only;
forcing strings keeps the cell formatting predictable and avoids accidental
date or number coercion when the underlying value looks numeric.
"""

from __future__ import annotations


def coerce_cell_value(value: object) -> str:
    if value is None:
        return ""
    return str(value)

