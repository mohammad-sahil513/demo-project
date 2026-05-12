"""Pydantic model for the template JSON record.

A template represents either:

- an **inbuilt** template (PDD / SDD / UAT) — bundled in
  ``modules/template/inbuilt`` and persisted on first read.
- a **custom** template — uploaded by a user as a ``.docx`` or ``.xlsx``.

The record holds everything the workflow needs to produce a faithful export
without re-running compilation: the section plan, style map, sheet map (XLSX),
placeholder schema, and validation outcomes. See
``docs/PIPELINE.md`` for the lifecycle.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TemplateSource, TemplateStatus


class TemplateRecord(BaseModel):
    """One template's metadata and compile-time artifacts."""

    # ``extra="ignore"`` lets older records load even after we add new fields.
    model_config = ConfigDict(extra="ignore")

    template_id: str
    filename: str
    template_type: str  # ``PDD`` | ``SDD`` | ``UAT``
    template_source: str = Field(default=TemplateSource.CUSTOM)
    version: str | None = None
    # ``TemplateStatus`` — must be ``READY`` before any workflow may use it.
    status: str = Field(default=TemplateStatus.PENDING)
    # ``file_path`` is the source ``.docx``/``.xlsx`` we render against.
    file_path: str | None = None
    preview_path: str | None = None
    preview_html: str | None = None
    compile_error: str | None = None
    compiled_at: str | None = None

    # Compile artifacts -----------------------------------------------------
    # Ordered list of sections discovered/declared in the template; each dict
    # has the shape produced by ``modules.template.planner``.
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    # DOCX style map (heading→style id) used by the placeholder filler.
    style_map: dict[str, object] = Field(default_factory=dict)
    # XLSX sheet map (sheet name→column layout) for tabular templates.
    sheet_map: dict[str, object] = Field(default_factory=dict)
    schema_version: str | None = None
    # Canonical placeholder schema (id → location, kind, validation rules).
    placeholder_schema: dict[str, object] = Field(default_factory=dict)
    validation_status: str = "unknown"
    validation_errors: list[dict[str, object]] = Field(default_factory=list)
    validation_warnings: list[dict[str, object]] = Field(default_factory=list)
    # Last DOCX sample-fill + integrity probe (export-parity preview); empty for XLSX or if not run yet.
    fidelity_integrity_issues: list[dict[str, object]] = Field(default_factory=list)
    fidelity_integrity_summary: dict[str, str] = Field(default_factory=dict)
    fidelity_integrity_checked_at: str | None = None
    # User-supplied explicit section→placeholder map (merged into schema at compile); optional.
    section_placeholder_bindings: dict[str, object] = Field(default_factory=dict)
    # Computed at compile: section_id -> [placeholder_id, ...]
    resolved_section_bindings: dict[str, object] = Field(default_factory=dict)
    created_at: str
    updated_at: str
