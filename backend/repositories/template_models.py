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
    compile_error: str | None = None
    compiled_at: str | None = None
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    created_at: str
    updated_at: str
