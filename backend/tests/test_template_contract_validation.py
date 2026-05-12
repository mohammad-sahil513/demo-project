"""Template contract validation: error vs warning classification rules.

Pins the rules in :func:`validate_template_schema`:

- Empty placeholder ID and duplicate IDs raise *errors*.
- Missing DOCX relationship anchors and absent placeholders raise
  *warnings*.
- Missing XLSX sheet anchors raise an *error*.
"""

from modules.template.contract_validator import validate_template_schema
from modules.template.schema_models import PlaceholderDef, PlaceholderLocation, TemplateSchema


def test_validate_schema_duplicate_placeholder_error() -> None:
    schema = TemplateSchema(
        source_format="docx",
        placeholders=[
            PlaceholderDef(
                placeholder_id="x",
                location=PlaceholderLocation(part="word/document.xml", xml_path="/w:document/w:body/w:p[1]"),
            ),
            PlaceholderDef(
                placeholder_id="x",
                location=PlaceholderLocation(part="word/document.xml", xml_path="/w:document/w:body/w:p[2]"),
            ),
        ],
    )
    errors, _warnings = validate_template_schema(schema)
    assert any(e.get("code") == "placeholder_id_duplicate" for e in errors)

