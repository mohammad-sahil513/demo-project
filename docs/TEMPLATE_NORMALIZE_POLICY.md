# Template upload normalization (`template_upload_normalize_enabled`)

When `TEMPLATE_UPLOAD_NORMALIZE_ENABLED=true`, compile runs [docx_template_normalize.py](../backend/modules/template/docx_template_normalize.py) **before** extraction.

## Current behavior

- Trims each `w:tbl` in `word/document.xml` to **at most two rows** (intended pattern: header row + one body row).
- Does **not** remove “description/example” prose between headings (that would require a separate, riskier pass).

## Production policy

- **Default: off** in production.
- Enable only for a **certified template family** after manual QA on representative files (merged cells, nested tables, and unusual OOXML can break or look wrong).
- Warnings such as `normalize_table_rows_trimmed` appear in compile validation warnings—monitor them.

## Per-tenant / per-family (future)

If you introduce template families or tenants, gate normalization per catalog entry rather than a global flag.
