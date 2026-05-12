"""Inbuilt style map for UAT — landscape with emerald table headers for wide test grids."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


UAT_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=15, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=12, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=10),
    table=TableStyle(header_fill="#065f46", header_text_color="#ffffff", border_color="#6ee7b7"),
    page_setup=PageSetup(orientation="landscape"),
)
