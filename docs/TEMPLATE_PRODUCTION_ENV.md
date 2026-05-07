# Template feature flags — environment matrix

Set these via environment variables (Pydantic `TEMPLATE_*` / `template_*` field names as in [backend/core/config.py](../backend/core/config.py)).

## Profiles

| Variable | Dev (local) | Staging | Prod (custom DOCX fidelity) |
|----------|-------------|---------|-----------------------------|
| `TEMPLATE_DOCX_PLACEHOLDER_NATIVE_ENABLED` | optional `true` | `true` | `true` |
| `TEMPLATE_SECTION_BINDING_STRICT` | `false` | `true` | `true` |
| `TEMPLATE_FIDELITY_STRICT_ENABLED` | optional | `true` | `true` |
| `TEMPLATE_SCHEMA_VALIDATION_BLOCKING` | optional | `true` | `true` |
| `TEMPLATE_FIDELITY_MEDIA_INTEGRITY_BLOCKING` | `false` | `true` | `true` |
| `TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED` | `true` | `false` | `false` |
| `TEMPLATE_DOCX_REQUIRE_NATIVE_FOR_CUSTOM` | `false` | `true` | `true` |
| `TEMPLATE_UPLOAD_NORMALIZE_ENABLED` | `false` | `false` | `false` unless certified per template family |

## Notes

- **Native DOCX** requires compile to persist `resolved_section_bindings` (exact `section_id` ↔ placeholder match or `PATCH /templates/{id}/bindings`).
- **`TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED=false`** blocks pure heading-based `DocxFiller` when strict mode is off; pair with strict or native in staging/prod.
- **`TEMPLATE_DOCX_REQUIRE_NATIVE_FOR_CUSTOM=true`** blocks export when native preconditions are not met (flag off, empty map, or missing schema).
- **UAT / XLSX**: keep `TEMPLATE_FIDELITY_STRICT_ENABLED` aligned with named-range templates; same validation discipline as DOCX.

## Classifier timeouts

| Variable | Default | Purpose |
|----------|---------|---------|
| `TEMPLATE_CLASSIFIER_TIMEOUT_SECONDS` | `120` | `asyncio.wait_for` around LLM classification |
| `TEMPLATE_CLASSIFIER_MAX_RETRIES` | `2` | Extra attempts after timeout (compile fails if all exhausted) |
