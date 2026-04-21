"""Shared template models for inbuilt and custom pipelines."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ParagraphStyle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    font_name: str = "Calibri"
    font_size_pt: int = 11
    bold: bool = False
    italic: bool = False
    alignment: str = "left"


class TableStyle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    header_fill: str = "#1f2937"
    header_text_color: str = "#ffffff"
    border_color: str = "#d1d5db"
    row_striping: bool = True


class PageSetup(BaseModel):
    model_config = ConfigDict(extra="ignore")

    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_top_in: float = 1.0
    margin_right_in: float = 1.0
    margin_bottom_in: float = 1.0
    margin_left_in: float = 1.0


class StyleMap(BaseModel):
    model_config = ConfigDict(extra="ignore")

    heading_1: ParagraphStyle = Field(default_factory=lambda: ParagraphStyle(font_size_pt=16, bold=True))
    heading_2: ParagraphStyle = Field(default_factory=lambda: ParagraphStyle(font_size_pt=13, bold=True))
    body: ParagraphStyle = Field(default_factory=ParagraphStyle)
    table: TableStyle = Field(default_factory=TableStyle)
    page_setup: PageSetup = Field(default_factory=PageSetup)


class DocumentSkeleton(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    headings: list[str] = Field(default_factory=list)
    table_headers_by_heading: dict[str, list[str]] = Field(default_factory=dict)
    raw_structure: dict[str, object] = Field(default_factory=dict)


class SectionDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    section_id: str
    title: str
    description: str = ""
    execution_order: int
    output_type: Literal["text", "table", "diagram"] = "text"
    prompt_selector: str = "default"
    retrieval_query: str = ""
    generation_hints: str = ""
    expected_length: str = "medium"
    tone: str = "professional"
    level: int = 1
    parent_section_id: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    table_headers: list[str] = Field(default_factory=list)
    is_complex: bool = False
