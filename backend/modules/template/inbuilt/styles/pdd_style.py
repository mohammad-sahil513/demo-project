"""Inbuilt style map for PDD — dark slate table header on portrait pages."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


PDD_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=16, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=13, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=11),
    table=TableStyle(header_fill="#0f172a", header_text_color="#ffffff", border_color="#cbd5e1"),
    page_setup=PageSetup(orientation="portrait"),
)
