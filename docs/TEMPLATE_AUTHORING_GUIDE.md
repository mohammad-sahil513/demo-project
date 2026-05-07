# Template Authoring Guide

## DOCX
- Prefer content controls (`w:sdt`) with stable IDs/tags.
- Optional token style supported: `{{placeholder_id}}`.
- Keep business branding assets in headers/footers.
- Do not place required placeholders inside dynamic/unsupported fields.

## XLSX
- Use named ranges for placeholders.
- Keep formulas/styles in non-placeholder cells.
- For table-like outputs, reserve dedicated named ranges.

## Placeholder Naming
- Use lowercase snake_case or dot notation.
- Examples: `project.name`, `scope_summary`, `uat.test_case_table`.

## Validation
- Upload and validate template before production use.
- Fix duplicate IDs and missing required placeholders before compile.
