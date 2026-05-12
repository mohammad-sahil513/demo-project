"""Validation for the compiled template placeholder schema.

Runs at the end of the template compile step. The output is two lists of
issue dicts (errors and warnings); both are persisted on the
:class:`TemplateRecord` and surfaced in the UI. Errors block compilation;
warnings are advisory and do not.

Checks performed:
- Placeholder IDs are non-empty and unique.
- DOCX templates carry relationship anchors (so media integrity is
  enforceable downstream).
- XLSX templates carry at least one sheet anchor.
- An empty placeholder list yields a single ``placeholders_not_found``
  warning rather than an error — some inbuilt templates intentionally use
  the heading-driven path with no placeholders.
"""

from __future__ import annotations

from modules.template.schema_models import SchemaValidationIssue, TemplateSchema


def validate_template_schema(schema: TemplateSchema) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    errors: list[SchemaValidationIssue] = []
    warnings: list[SchemaValidationIssue] = []

    if not schema.placeholders:
        warnings.append(
            SchemaValidationIssue(
                code="placeholders_not_found",
                message="No deterministic placeholders were extracted from template.",
                level="warning",
            )
        )

    seen: set[str] = set()
    for placeholder in schema.placeholders:
        pid = placeholder.placeholder_id.strip()
        if not pid:
            errors.append(
                SchemaValidationIssue(
                    code="placeholder_id_empty",
                    message="Placeholder id cannot be empty.",
                )
            )
            continue
        if pid in seen:
            errors.append(
                SchemaValidationIssue(
                    code="placeholder_id_duplicate",
                    message=f"Duplicate placeholder id detected: {pid}",
                    placeholder_id=pid,
                )
            )
            continue
        seen.add(pid)

    anchors = schema.locked_fidelity_anchors or {}
    if schema.source_format == "docx":
        if not anchors.get("relationship_parts"):
            warnings.append(
                SchemaValidationIssue(
                    code="docx_relationship_anchors_missing",
                    message="DOCX relationship anchors are missing; media integrity checks may be weaker.",
                    level="warning",
                )
            )
    if schema.source_format == "xlsx":
        if not anchors.get("sheets"):
            errors.append(
                SchemaValidationIssue(
                    code="xlsx_sheets_missing",
                    message="XLSX workbook has no sheet anchors.",
                )
            )

    return [e.model_dump() for e in errors], [w.model_dump() for w in warnings]

