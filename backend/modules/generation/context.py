"""Shared prompt context builders for generation.

Every section generator (text/table/diagram) uses :func:`build_prompt_mapping`
to assemble the variable substitutions that fill the prompt YAML templates.
Keeping all formatting logic in one place means a new section field is added
exactly once and immediately visible in every prompt.
"""
from __future__ import annotations

from collections.abc import Iterable

from modules.template.models import SectionDefinition

# Stand-in inserted into prompts when retrieval returned no chunks. We
# explicitly tell the model to lean on the section title/description instead
# of hallucinating sources.
_NO_EVIDENCE_TEXT = (
    "No retrieved evidence is available for this section. "
    "Rely on the section title and description only."
)


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _truncate_text(text: str, *, max_chars: int | None = None) -> str:
    if max_chars is None or max_chars <= 0:
        return text
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rstrip()
    return f"{truncated}\n\n[truncated for prompt budget]"


def evidence_text_from_retrieval(
    payload: dict[str, object] | None,
    *,
    max_chars: int | None = None,
) -> str:
    """Extract the joined source text from a retrieval payload, with optional truncation."""
    if not payload:
        return _NO_EVIDENCE_TEXT

    raw = payload.get("context_text")
    text = _normalize_text(raw)
    if not text:
        return _NO_EVIDENCE_TEXT

    return _truncate_text(text, max_chars=max_chars)


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


def format_child_titles(child_titles: Iterable[str] | None) -> str:
    values = [str(title).strip() for title in (child_titles or []) if str(title).strip()]
    if not values:
        return "None"
    return ", ".join(values)


def infer_section_role(*, parent_title: str | None, child_titles: Iterable[str] | None) -> str:
    has_parent = bool((parent_title or "").strip())
    has_children = any(str(title).strip() for title in (child_titles or []))

    if has_children:
        return "parent_with_children"
    if has_parent:
        return "child_or_leaf"
    return "standalone_or_top_level"


def build_prompt_mapping(
    section: SectionDefinition,
    doc_type: str,
    evidence_context: str,
    *,
    render_error: str = "",
    failed_diagram_source: str = "",
    parent_section_title: str = "",
    child_section_titles: Iterable[str] | None = None,
) -> dict[str, str]:
    """Return the ``{placeholder: value}`` mapping consumed by the prompt YAML templates.

    The mapping keys must match the ``{placeholder}`` tokens in the YAML.
    Add a new mapping key here and the existing template renderer
    (:meth:`GenerationPromptLoader.render_template`) will pick it up
    automatically.
    """
    child_titles_text = format_child_titles(child_section_titles)
    section_role = infer_section_role(
        parent_title=parent_section_title,
        child_titles=child_section_titles,
    )

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
        "parent_section_title": (parent_section_title or "").strip() or "None",
        "child_section_titles": child_titles_text,
        "section_role": section_role,
    }
