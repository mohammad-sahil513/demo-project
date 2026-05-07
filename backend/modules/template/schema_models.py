"""Schema models for deterministic template placeholders."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlaceholderKind = Literal["text", "rich_text", "bullet_list", "numbered_list", "table", "image"]


class PlaceholderLocation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    part: str
    xml_path: str
    context: str | None = None
    mask_scope: Literal["text_tokens", "content_control", "path_node", "bookmark_range"] = "path_node"


class PlaceholderDef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    placeholder_id: str
    kind: PlaceholderKind = "text"
    required: bool = True
    location: PlaceholderLocation


class TemplateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str = "1.0"
    source_format: Literal["docx", "xlsx"]
    placeholders: list[PlaceholderDef] = Field(default_factory=list)
    locked_fidelity_anchors: dict[str, object] = Field(default_factory=dict)
    # Optional explicit map: section_id (from planner) -> placeholder_id or list of ids
    section_placeholder_bindings: dict[str, str | list[str]] = Field(default_factory=dict)


class SchemaValidationIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: str
    message: str
    placeholder_id: str | None = None
    level: Literal["error", "warning"] = "error"

