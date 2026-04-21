"""Shared prompt context builders for generation."""

from __future__ import annotations

from modules.template.models import SectionDefinition


def evidence_text_from_retrieval(payload: dict[str, object] | None) -> str:
    if not payload:
        return "No retrieved evidence is available for this section. Rely on the section title and description only."
    raw = payload.get("context_text")
    text = str(raw or "").strip()
    return text or "No retrieved evidence is available for this section."


def citations_from_retrieval(payload: dict[str, object] | None) -> list[dict[str, object]]:
    if not payload:
        return []
    raw = payload.get("citations")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, object]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def format_table_headers(section: SectionDefinition) -> str:
    if section.table_headers:
        return " | ".join(section.table_headers)
    if section.required_fields:
        return " | ".join(section.required_fields)
    return "Item | Details | Evidence"


def format_required_fields(section: SectionDefinition) -> str:
    if section.required_fields:
        return ", ".join(section.required_fields)
    return "N/A"


def build_prompt_mapping(
    section: SectionDefinition,
    doc_type: str,
    evidence_context: str,
    *,
    render_error: str = "",
    failed_diagram_source: str = "",
) -> dict[str, str]:
    return {
        "doc_type": doc_type,
        "section_title": section.title,
        "section_description": section.description,
        "generation_hints": section.generation_hints or "N/A",
        "expected_length": section.expected_length,
        "tone": section.tone,
        "evidence_context": evidence_context,
        "table_headers": format_table_headers(section),
        "required_fields": format_required_fields(section),
        "render_error": render_error,
        "failed_diagram_source": failed_diagram_source,
    }
