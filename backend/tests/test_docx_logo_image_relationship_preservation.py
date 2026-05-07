from modules.template.contract_validator import validate_template_schema
from modules.template.schema_models import TemplateSchema


def test_docx_schema_warns_when_relationship_anchors_missing() -> None:
    schema = TemplateSchema(
        source_format="docx",
        placeholders=[],
        locked_fidelity_anchors={"header_parts": [], "footer_parts": []},
    )
    _errors, warnings = validate_template_schema(schema)
    assert any(w.get("code") == "docx_relationship_anchors_missing" for w in warnings)

