# Template Validation Errors

## Error Codes

- `placeholder_id_empty`
  - Placeholder id is blank.
- `placeholder_id_duplicate`
  - Duplicate placeholder id found.
- `xlsx_sheets_missing`
  - Workbook sheet anchors were not detected.
- `template_compile_failed`
  - Template compile operation failed.

## Warning Codes

- `placeholders_not_found`
  - No deterministic placeholders discovered.
- `docx_relationship_anchors_missing`
  - DOCX relationship anchors are missing; media integrity checks may be weaker.

## Remediation
- Add/rename placeholders to unique stable IDs.
- Add named ranges in XLSX templates.
- Re-upload corrected template and re-run validation.
