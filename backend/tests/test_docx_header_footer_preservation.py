"""Header/footer preservation: contract validator surfaces missing anchors.

When a DOCX template ships without ``relationship_parts`` anchors, the
strict fidelity probe needs to warn so operators can fix the template
before relying on it for production exports.
"""

from modules.template.contract_validator import validate_template_schema
from modules.template.schema_models import TemplateSchema


def test_docx_schema_has_header_footer_anchor_support() -> None:
    schema = TemplateSchema(
        source_format="docx",
        placeholders=[],
        locked_fidelity_anchors={
            "header_parts": ["word/header1.xml"],
            "footer_parts": ["word/footer1.xml"],
            "relationship_parts": ["word/_rels/document.xml.rels"],
        },
    )
    errors, _warnings = validate_template_schema(schema)
    assert errors == []

