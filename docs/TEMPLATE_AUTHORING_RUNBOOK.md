# Template authoring runbook (custom DOCX / XLSX)

## Placeholder-native DOCX (recommended for production)

1. **Placeholders** must be one of:
   - `{{placeholder_id}}` text tokens
   - Content controls (`w:sdt`) with tag/alias = `placeholder_id`
   - Word bookmarks (non-internal names) = `placeholder_id`

2. **Section binding (hybrid)**  
   - **Automatic:** if `placeholder_id` equals the planner `section_id` (e.g. `sec-custom-1-overview`), no extra map is needed.  
   - **Explicit:** `PATCH /api/templates/{template_id}/bindings` with JSON body `{ "sec-custom-1-overview": "my_body_cc" }` or `["id1", "id2"]` for multiple placeholders per section.

3. **After PATCH bindings** re-run compile (or use **Recompile** if exposed) so `resolved_section_bindings` is persisted.

4. **TOC / fields**  
   - Use real Word heading styles / outline levels for TOC fields.  
   - Outputs set **update fields on open**; users should open once in Word for full TOC refresh.  
   - Do not treat **browser preview** (`docx-preview`) as layout or field fidelity—use Word for acceptance.

5. **Strict / integrity**  
   - Enable media/header/footer integrity blocking in production if bad exports must be rejected.  
   - Fix template or placeholders when validation reports `docx_*` integrity errors.

## UAT (XLSX)

- Placeholders are **named ranges**; section binding rules mirror DOCX (exact name or explicit map).  
- Keep `TEMPLATE_FIDELITY_STRICT_ENABLED` on for production UAT builds using custom templates.

## Related code

- Schema extract: [backend/modules/template/schema_extractor_docx.py](../backend/modules/template/schema_extractor_docx.py)  
- Native writer: [backend/modules/export/docx_placeholder_writer.py](../backend/modules/export/docx_placeholder_writer.py)  
- Bindings: [backend/modules/template/section_bindings.py](../backend/modules/template/section_bindings.py)
