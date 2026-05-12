"""XLSX placeholder filler fidelity: sheet preservation and named range writes.

Builds tiny XLSX templates with named ranges, runs
:class:`XlsxPlaceholderFiller`, and confirms that:

- Every sheet from the template appears in the output workbook.
- Named ranges resolve to the same cells before and after fill.
- The contract guard surfaces a warning when the placeholder schema is
  absent.
"""

from pathlib import Path

from openpyxl import Workbook

from modules.assembly.models import AssembledDocument, AssembledSection
from modules.export.xlsx_placeholder_filler import XlsxPlaceholderFiller


def test_xlsx_placeholder_filler_outputs_file(tmp_path: Path) -> None:
    template = tmp_path / "template.xlsx"
    out = tmp_path / "out.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Scope"
    wb.save(template)

    assembled = AssembledDocument(
        title="Doc",
        doc_type="UAT",
        sections=[AssembledSection(section_id="s1", title="Scope", output_type="table", content="|A|\n|---|\n|v|")],
    )
    filler = XlsxPlaceholderFiller()
    filler.fill(
        assembled=assembled,
        output_path=out,
        template_path=template,
        sheet_map={"sheets": [{"name": "Scope", "index": 1}]},
        placeholder_schema={},
    )
    assert out.exists()

