"""In-memory assembled document structures (post-generation, pre-export)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssembledSection(BaseModel):
    """One section ready for export (no citation payloads — UI-only elsewhere)."""

    model_config = ConfigDict(extra="ignore")

    section_id: str
    title: str
    level: int = 1
    output_type: str = "text"
    content: str = ""
    diagram_path: str | None = None


class AssembledDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    doc_type: str
    sections: list[AssembledSection] = Field(default_factory=list)
