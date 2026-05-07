# UAT Observability Contract

This document defines canonical observability keys for UAT workflow runs.

## Required Keys

- `uat_schema_compliance_rate` (0.0 - 1.0)
- `uat_low_evidence_sections` (integer)
- `uat_sheet_row_counts` (object keyed by section/sheet title)
- `uat_schema_warning_counts` (object keyed by warning code)
- `uat_schema_warning_codes` (array of configured warning-level codes)
- `uat_schema_blocking_codes` (array of configured blocking codes)

## Retrieval Baseline Keys

- `retrieval_zero_hit_sections`
- `retrieval_total_chunks`
- `retrieval_phase_duration_ms`

## Interpretation

- Low `uat_schema_compliance_rate` indicates structural risk in exported XLSX.
- High `uat_low_evidence_sections` indicates content confidence risk.
- `uat_schema_warning_counts` enables code-specific alerting and RCA.

## Alerting Suggestions

- Warn when `uat_schema_compliance_rate < 0.8`
- Critical when any blocking code appears in `uat_schema_warning_counts`
- Warn when `uat_low_evidence_sections > 0`
