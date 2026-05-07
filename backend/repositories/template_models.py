"""Template persistence model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TemplateSource, TemplateStatus


class TemplateRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    template_id: str
    filename: str
    template_type: str
    template_source: str = Field(default=TemplateSource.CUSTOM)
    version: str | None = None
    status: str = Field(default=TemplateStatus.PENDING)
    file_path: str | None = None
    preview_path: str | None = None
    preview_html: str | None = None
    compile_error: str | None = None
    compiled_at: str | None = None
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    schema_version: str | None = None
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
