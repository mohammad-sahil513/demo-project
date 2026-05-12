"""Merge extracted template metadata into compiled section plans.

XLSX templates carry their schema as worksheet header rows. After the
template is extracted and classified, this helper copies each sheet's
detected header row onto the matching :class:`SectionDefinition` as
``table_headers`` (and ``required_fields`` when not already set). The match
is by normalized title — whitespace-collapsed and trimmed.
"""

from __future__ import annotations

from typing import Any

from modules.template.models import SectionDefinition


def _normalize_title(text: str) -> str:
    return " ".join((text or "").split()).strip()


def apply_xlsx_sheet_schema_to_plan(
    plan: list[SectionDefinition],
    sheet_map: dict[str, Any],
) -> list[SectionDefinition]:
    """
    For XLSX templates, sheet_map[\"schema\"] lists per-sheet headers.
    Match section titles to sheet_name and populate table_headers / required_fields.
    """
    if not plan or not isinstance(sheet_map, dict):
        return plan

    raw_schema = sheet_map.get("schema")
    if not isinstance(raw_schema, list) or not raw_schema:
        return plan

    by_sheet: dict[str, list[str]] = {}
    for item in raw_schema:
        if not isinstance(item, dict):
            continue
        name = item.get("sheet_name")
        headers_raw = item.get("headers")
        if name is None or not isinstance(headers_raw, list):
            continue
        key = _normalize_title(str(name))
        if not key:
            continue
        headers = [_normalize_title(str(h)) for h in headers_raw if str(h).strip()]
        if headers:
            by_sheet[key] = headers

    if not by_sheet:
        return plan

    out: list[SectionDefinition] = []
    for sec in plan:
        key = _normalize_title(sec.title)
        headers = by_sheet.get(key)
        if not headers:
            out.append(sec)
            continue
        update: dict[str, Any] = {"table_headers": list(headers)}
        if not sec.required_fields:
            update["required_fields"] = list(headers)
        out.append(sec.model_copy(update=update))
    return out
