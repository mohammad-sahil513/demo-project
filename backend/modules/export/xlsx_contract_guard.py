"""Contract checks for XLSX strict rendering."""

from __future__ import annotations


def check_xlsx_schema(schema: dict[str, object] | None) -> list[dict[str, object]]:
    if not schema:
        return [
            {
                "code": "placeholder_schema_missing",
                "severity": "warning",
                "message": "XLSX strict renderer running without placeholder schema.",
            }
        ]
    return []

