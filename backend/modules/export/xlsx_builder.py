"""Build or fill UAT XLSX outputs."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from modules.assembly.models import AssembledDocument
from modules.export.markdown_tables import parse_gfm_table, split_markdown_blocks


def _sheet_title(title: str) -> str:
    t = title.strip()[:31]
    return t or "Sheet"


def _get_or_create_worksheet(wb, section_title: str, sheet_map: dict[str, object] | None):
    """Resolve sheet using workbook names first, then template sheet_map entries."""
    st_full = section_title.strip()
    st_short = _sheet_title(st_full)

    def matches(sheet_name: str) -> bool:
        sn = sheet_name.strip()
        return sn == st_full or sn == st_short or sn.lower() == st_full.lower()

    for sn in wb.sheetnames:
        if matches(sn):
            return wb[sn]

    if sheet_map and isinstance(sheet_map.get("sheets"), list):
        for item in sheet_map["sheets"]:
            nm = (item.get("name") or "").strip()
            if not nm:
                continue
            if nm == st_full or nm.lower() == st_full.lower() or nm == st_short:
                if nm in wb.sheetnames:
                    return wb[nm]
                n2 = _sheet_title(nm)
                if n2 in wb.sheetnames:
                    return wb[n2]

    new_name = st_short
    if new_name not in wb.sheetnames:
        wb.create_sheet(title=new_name)
    return wb[new_name]


class XlsxBuilder:
    def build(
        self,
        assembled: AssembledDocument,
        output_path: Path,
        *,
        template_path: Path | None = None,
        sheet_map: dict[str, object] | None = None,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        from_template = bool(template_path and template_path.is_file())
        if from_template:
            from openpyxl import load_workbook

            wb = load_workbook(template_path)  # type: ignore[arg-type]
        else:
            wb = Workbook()
            wb.remove(wb.active)

        for section in assembled.sections:
            ws = _get_or_create_worksheet(wb, section.title, sheet_map)
            mr = ws.max_row or 0
            mc = ws.max_column or 0

            if from_template:
                header_nonempty = mr >= 1 and any(
                    ws.cell(row=1, column=c).value not in (None, "")
                    for c in range(1, mc + 1)
                )
                if mr > 1:
                    ws.delete_rows(2, mr - 1)
                elif mr == 1 and not header_nonempty:
                    ws.delete_rows(1, 1)
                start_row = 2 if header_nonempty else 1
            else:
                if mr > 0:
                    ws.delete_rows(1, mr)
                start_row = 1

            rows: list[list[str]] = []
            if section.output_type == "table":
                for kind, payload in split_markdown_blocks(section.content):
                    if kind == "table":
                        rows.extend(parse_gfm_table(payload))
            if not rows and section.content.strip():
                rows = [[section.content.strip()]]

            for r_off, row in enumerate(rows):
                r_idx = start_row + r_off
                for c_idx, val in enumerate(row, start=1):
                    ws.cell(row=r_idx, column=c_idx, value=val)
                    if r_off == 0:
                        ws.column_dimensions[get_column_letter(c_idx)].width = min(
                            max(len(str(val)) + 2, 12),
                            48,
                        )

        wb.save(str(output_path))
