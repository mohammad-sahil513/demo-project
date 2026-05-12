"""XLSX schema extractor — named ranges as placeholders + sheet anchors.

For XLSX templates we treat Excel **named ranges** as the deterministic
placeholder contract. Authors create a named range pointing at the cell or
range they want filled, and the placeholder filler writes content into the
exact ``A1`` destination stored on the defined name.

We also record each worksheet's name, index, and dimensions as fidelity
anchors — the integrity checker compares the post-fill workbook against
these values to detect accidental sheet removal or oversize bleed.
"""

from __future__ import annotations

from pathlib import Path

from modules.template.schema_models import PlaceholderDef, PlaceholderLocation, TemplateSchema
from modules.template.xlsx_workbook import open_xlsx_workbook


def extract_xlsx_schema(template_path: Path) -> TemplateSchema:
    placeholders: list[PlaceholderDef] = []
    seen: set[str] = set()
    sheet_anchors: list[dict[str, object]] = []

    with open_xlsx_workbook(template_path, read_only=False, data_only=False) as wb:
        # Named ranges are the strongest enterprise placeholder contract for XLSX.
        for defined_name in wb.defined_names.values():
            name = str(defined_name.name or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            dest_text = str(defined_name.attr_text or "")
            placeholders.append(
                PlaceholderDef(
                    placeholder_id=name,
                    kind="text",
                    required=True,
                    location=PlaceholderLocation(
                        part="workbook",
                        xml_path=dest_text or f"definedName:{name}",
                        context="named-range",
                    ),
                )
            )

        for index, sheet_name in enumerate(wb.sheetnames, start=1):
            ws = wb[sheet_name]
            sheet_anchors.append(
                {
                    "name": sheet_name,
                    "index": index,
                    "max_row": int(ws.max_row or 0),
                    "max_column": int(ws.max_column or 0),
                }
            )

    return TemplateSchema(
        source_format="xlsx",
        placeholders=placeholders,
        locked_fidelity_anchors={"sheets": sheet_anchors},
    )

