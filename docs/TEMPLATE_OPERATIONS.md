# Template Operations

This document consolidates template authoring, runbook steps, fidelity rules, normalization policy, environment flags, validation troubleshooting, and UAT observability.

## Purpose
- Provide one canonical reference for all template-related operations and policies.

## Inputs
- Custom DOCX/XLSX template files.
- Runtime template feature flags.
- Validation and observability outputs.

## Outputs
- Production-safe template authoring and rollout process.
- Clear strict-mode/fidelity contract.
- Fast troubleshooting for compile/export issues.

## Failure Modes
- Invalid placeholders or bindings can block compile/export.
- Misconfigured flags can allow unsafe fallback behavior.
- Missing observability can hide UAT schema/evidence regressions.

## 1) Authoring Guidelines

### DOCX
- Prefer content controls (`w:sdt`) with stable IDs/tags.
- Optional token style supported: `{{placeholder_id}}`.
- Keep branding assets in headers/footers.
- Avoid required placeholders inside dynamic/unsupported fields.

### XLSX
- Use named ranges for placeholders.
- Keep formulas/styles in non-placeholder cells.
- Reserve dedicated named ranges for table-like outputs.

### Placeholder Naming
- Use lowercase snake_case or dot notation.
- Examples: `project.name`, `scope_summary`, `uat.test_case_table`.

## 2) Authoring Runbook (Custom DOCX/XLSX)

### Placeholder-Native DOCX (Recommended)
1. Use placeholders as one of:
   - `{{placeholder_id}}` text tokens
   - content controls (`w:sdt`) where tag/alias = `placeholder_id`
   - Word bookmarks with name = `placeholder_id`
2. Section binding (hybrid):
   - Automatic when `placeholder_id == section_id`
   - Explicit via `PATCH /api/templates/{template_id}/bindings`
3. After binding updates, re-run compile to persist `resolved_section_bindings`.
4. TOC/fields:
   - Use real Word heading styles for TOC fields.
   - Outputs set update-fields-on-open; validate in Word, not only browser preview.
5. Integrity:
   - Enable strict blocking in production.
   - Resolve `docx_*` integrity errors before release.

### UAT (XLSX)
- Placeholders are named ranges.
- Binding discipline mirrors DOCX (exact match or explicit map).
- Keep strict mode enabled for production custom UAT templates.

## 3) Fidelity Contract

### Core Rule
Only declared placeholder values may change in final output.

### Must Preserve
- Header/footer structure and content.
- Embedded media/logo relationships.
- Page setup, section breaks, numbering, watermark/background.
- Styles/layout outside placeholder ranges.

### Allowed Changes
- Text, rich text, list, table, and image content at declared placeholders.

### Strict Blocking Conditions
Block export when:
- required placeholders are unresolved,
- header/footer integrity fails,
- media relationship integrity fails,
- schema/contract validation fails.

## 4) Upload Normalization Policy

Normalization flag: `TEMPLATE_UPLOAD_NORMALIZE_ENABLED`.

Current behavior:
- trims each `w:tbl` in `word/document.xml` to at most two rows,
- does not remove narrative prose between headings.

Production stance:
- default off,
- enable only for certified template families after QA,
- monitor warnings like `normalize_table_rows_trimmed`.

## 5) Environment Matrix (Template Flags)

| Variable | Dev (local) | Staging | Prod |
|---|---|---|---|
| `TEMPLATE_DOCX_PLACEHOLDER_NATIVE_ENABLED` | optional `true` | `true` | `true` |
| `TEMPLATE_SECTION_BINDING_STRICT` | `false` | `true` | `true` |
| `TEMPLATE_FIDELITY_STRICT_ENABLED` | optional | `true` | `true` |
| `TEMPLATE_SCHEMA_VALIDATION_BLOCKING` | optional | `true` | `true` |
| `TEMPLATE_FIDELITY_MEDIA_INTEGRITY_BLOCKING` | `false` | `true` | `true` |
| `TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED` | `true` | `false` | `false` |
| `TEMPLATE_DOCX_REQUIRE_NATIVE_FOR_CUSTOM` | `false` | `true` | `true` |
| `TEMPLATE_UPLOAD_NORMALIZE_ENABLED` | `false` | `false` | `false` (unless certified family) |

Classifier controls:
- `TEMPLATE_CLASSIFIER_TIMEOUT_SECONDS` (default `120`)
- `TEMPLATE_CLASSIFIER_MAX_RETRIES` (default `2`)

## 6) Validation Errors and Remediation

### Common Error Codes
- `placeholder_id_empty`
- `placeholder_id_duplicate`
- `xlsx_sheets_missing`
- `template_compile_failed`

### Common Warning Codes
- `placeholders_not_found`
- `docx_relationship_anchors_missing`

### Remediation
- Use unique, stable placeholder IDs.
- Add missing named ranges/placeholders.
- Re-upload and re-run compile/validation.

## 7) UAT Observability Contract

Required keys:
- `uat_schema_compliance_rate`
- `uat_low_evidence_sections`
- `uat_sheet_row_counts`
- `uat_schema_warning_counts`
- `uat_schema_warning_codes`
- `uat_schema_blocking_codes`

Retrieval baseline keys:
- `retrieval_zero_hit_sections`
- `retrieval_total_chunks`
- `retrieval_phase_duration_ms`

Alerting suggestions:
- warn when `uat_schema_compliance_rate < 0.8`,
- critical when blocking code appears,
- warn when `uat_low_evidence_sections > 0`.

## Related Code

- `backend/modules/template/schema_extractor_docx.py`
- `backend/modules/template/section_bindings.py`
- `backend/modules/export/docx_placeholder_writer.py`
- `backend/modules/export/renderer.py`
