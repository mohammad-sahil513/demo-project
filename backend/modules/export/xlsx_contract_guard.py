"""Contract checks for XLSX strict rendering.

Cheap gate that surfaces a single warning when an XLSX template is being
rendered without a compiled placeholder schema. The warning is the signal
that strict mode is degraded to legacy fill; the renderer still produces
output but the integrity layer cannot enforce a tighter contract.
"""

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

