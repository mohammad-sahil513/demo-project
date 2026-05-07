"""In-memory assembled document structures (post-generation, pre-export)."""

from __future__ import annotations

from typing import Any

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

    # Forward-compatible container for future semantic blocks
    content_blocks: list[dict[str, Any]] = Field(default_factory=list)

    # Per-section export mode (kept for compatibility; document-level mode is primary)
    export_mode: str = "final"


class AssembledDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    doc_type: str
    sections: list[AssembledSection] = Field(default_factory=list)

    # NEW: document-wide export mode
    export_mode: str = "final"
