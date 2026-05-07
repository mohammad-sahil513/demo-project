"""Infer which DOCX export branch applies for a template (observability / UI)."""

from __future__ import annotations

from pathlib import Path

from core.config import settings
from core.constants import TemplateSource
from modules.template.inbuilt.registry import is_inbuilt_template_id
from repositories.template_models import TemplateRecord


def compute_export_path_hint(record: TemplateRecord) -> str:
    """
    Server-side label for the effective custom-DOCX export branch given current flags and compile artifacts.

    Inbuilt templates use the document builder path, not custom-template fill.
    """
    suffix = Path(record.filename or "").suffix.lower()
    if suffix != ".docx":
        return "xlsx_or_other"

    if record.template_source == TemplateSource.INBUILT.value or is_inbuilt_template_id(record.template_id):
        return "inbuilt_docx_builder"

    has_schema = record.placeholder_schema is not None
    raw = record.resolved_section_bindings or {}
    has_bindings = isinstance(raw, dict) and len(raw) > 0
    native_on = settings.template_docx_placeholder_native_enabled
    use_native = bool(native_on and has_bindings and has_schema)
    strict = settings.template_fidelity_strict_enabled
    legacy_ok = settings.template_docx_legacy_export_allowed
    require_native = settings.template_docx_require_native_for_custom

    if require_native and not use_native:
        return "blocked_require_native"
    if not use_native and not strict and not legacy_ok:
        return "blocked_legacy_disallowed"
    if use_native:
        return "native_placeholders"
    if strict:
        return "strict_placeholder_filler"
    return "legacy_heading_fill"
