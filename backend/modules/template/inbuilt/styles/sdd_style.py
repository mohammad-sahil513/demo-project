"""Inbuilt style map for SDD."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


SDD_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=16, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=13, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=11),
    table=TableStyle(header_fill="#1d4ed8", header_text_color="#ffffff", border_color="#93c5fd"),
    page_setup=PageSetup(orientation="portrait"),
)
