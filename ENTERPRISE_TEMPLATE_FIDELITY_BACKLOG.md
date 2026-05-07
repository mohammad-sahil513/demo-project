# Enterprise Template Fidelity Implementation Backlog

## Objective

Build an enterprise-grade custom template engine where:

- Input: user uploads a DOCX/XLSX custom template.
- Output: generated file preserves template structure and formatting exactly.
- Allowed differences: placeholder values/content only.
- Disallowed differences: layout, style, section/page setup, numbering behavior, table geometry, header/footer structure, and other non-placeholder document artifacts.
- Mandatory preservation scope:
  - company logos and embedded images
  - header and footer content/formatting
  - cover page and detail sections
  - watermark/background artifacts
  - page numbering and section metadata

This backlog maps implementation directly to the current project structure in `backend` and `frontend`.

---

## Current Gap Summary (from code review)

- Current DOCX custom fill is heading-based and clears content between headings.
- Placeholder-level deterministic replacement is not implemented.
- Preview DOCX is synthetic, not true render from fill engine.
- Matching logic can skip sections when heading matching fails.
- This is not sufficient for strict enterprise exact-fidelity guarantees.
- Header/footer/logo/image preservation is not contract-verified yet.
- LLM is not separated into "content generation only" vs "deterministic document fill".

---

## Phase 0 - Contract and Governance Definition

### Goal
Define and lock the fidelity contract before technical implementation.

### Deliverables
- Exact-fidelity contract document.
- Supported placeholder standards and authoring rules.
- Template validation policy and error taxonomy.

### Files to add/update
- Add `docs/TEMPLATE_FIDELITY_CONTRACT.md`
- Add `docs/TEMPLATE_AUTHORING_GUIDE.md`
- Add `docs/TEMPLATE_VALIDATION_ERRORS.md`

### Task checklist
- Define allowed vs forbidden XML-level changes.
- Define placeholder types:
  - `text`
  - `rich_text`
  - `bullet_list`
  - `numbered_list`
  - `table`
  - `image`
- Define mandatory placeholder ID conventions.
- Define versioned schema contract (`schema_version`).
- Define mandatory preservation rules for:
  - headers/footers
  - logos and media relationships
  - page-level details and section-level metadata
- Define LLM usage policy:
  - LLM allowed for generating business content text/table drafts.
  - LLM not allowed to decide document structure mutations in strict mode.
  - Final fill/replacement path must remain deterministic and non-LLM.

### Exit criteria
- Contract approved by product + engineering.
- At least 3 sample compliant templates (DOCX and XLSX).

---

## Phase 1 - Template Schema Extraction and Validation

### Goal
Create deterministic schema extraction and strict validation at upload/compile time.

### Backend modules to add
- `backend/modules/template/schema_models.py`
- `backend/modules/template/schema_extractor_docx.py`
- `backend/modules/template/schema_extractor_xlsx.py`
- `backend/modules/template/contract_validator.py`

### Backend modules to update
- `backend/modules/template/extractor.py` (delegate to schema extractors or coexist with migration mode)
- `backend/services/template_service.py` (store schema + validation report)
- `backend/repositories/template_models.py` (add schema fields)
- `backend/api/routes/templates.py` (validation status in responses)

### Data model additions (`TemplateRecord`)
- `schema_version: str | None`
- `placeholder_schema: dict[str, object]`
- `validation_status: str` (`valid`/`invalid`/`warning`)
- `validation_errors: list[dict[str, object]]`
- `validation_warnings: list[dict[str, object]]`

### Task checklist
- Extract all placeholders with deterministic IDs and document-path references.
- Validate duplicates, missing required placeholders, unsupported placeholder shapes.
- Fail compile for invalid contract (configurable strict mode).
- Persist schema alongside existing template compile metadata.
- Extract and persist document "locked fidelity anchors":
  - header/footer part references
  - image relationship map (logo/media ids)
  - section/page setup anchors
- Add validator checks for broken/missing mandatory anchors.

### APIs (additions)
- `GET /templates/{template_id}/schema`
- `POST /templates/{template_id}/validate`

### Exit criteria
- Invalid templates rejected with actionable errors.
- Valid templates persist stable schema JSON.

---

## Phase 2 - DOCX Exact-Fidelity Fill Engine

### Goal
Replace heading-region rewrite with placeholder-only XML replacement.

### Backend modules to add
- `backend/modules/export/docx_placeholder_filler.py`
- `backend/modules/export/docx_placeholder_handlers.py`
- `backend/modules/export/docx_xml_locator.py`

### Backend modules to update
- `backend/modules/export/renderer.py` (route custom DOCX to placeholder filler)
- `backend/modules/export/docx_filler.py` (deprecate or keep compatibility mode behind flag)
- `backend/services/workflow_executor.py` (block on unresolved placeholders)

### Task checklist
- Locate target placeholders via schema path references.
- Replace only placeholder node content.
- Preserve run/paragraph/table style attributes.
- Preserve section boundaries, headers/footers, field codes.
- Preserve all existing media references and logo placements.
- Ensure no mutation of non-placeholder nodes under `word/header*.xml` and `word/footer*.xml`.
- Emit compile report:
  - placeholders resolved
  - placeholders missing
  - placeholders overflow/truncated (if applicable)
  - media/logo/header/footer integrity status

### Quality gates
- Fail export when required placeholders unresolved.
- Add warning/error codes for all failure classes.
- Fail export when media or header/footer integrity checks fail.

### Exit criteria
- No heading-based region deletion for strict mode.
- Placeholder-only mutation verified on golden docs.

---

## Phase 3 - XLSX Exact-Fidelity Fill Engine

### Goal
Implement deterministic placeholder fill for spreadsheets with structure preservation.

### Backend modules to add
- `backend/modules/export/xlsx_placeholder_filler.py`
- `backend/modules/export/xlsx_placeholder_handlers.py`
- `backend/modules/export/xlsx_contract_guard.py`

### Backend modules to update
- `backend/modules/export/xlsx_builder.py` (strict schema-driven filling)
- `backend/modules/export/renderer.py` (strict mode routing)

### Task checklist
- Map placeholders to named ranges/cell anchors/table anchors.
- Fill values while preserving formulas, formats, validation, merges.
- Controlled dynamic table row insertion with style cloning.
- Validate required columns/sheets with strict blocking policy.

### Exit criteria
- Output workbook preserves formatting and formulas outside placeholder scope.

---

## Phase 4 - True Preview Pipeline (WYSIWYG)

### Goal
Ensure preview uses same fill pipeline and fidelity rules as final render.

### Backend modules to update
- `backend/modules/template/preview_generator.py` (replace synthetic DOCX generation)
- `backend/services/template_service.py` (preview generated from schema + sample payload)
- `backend/api/routes/templates.py` (preview diagnostics)

### Frontend modules to update
- `frontend/src/components/templates/TemplatePreviewModal.tsx`
- `frontend/src/api/templateApi.ts`
- `frontend/src/api/types.ts`

### Task checklist
- Generate preview from actual placeholder fill engine using deterministic sample payload.
- Return diagnostics payload:
  - placeholders filled
  - placeholders unresolved
  - warnings
- Include fidelity diagnostics in preview:
  - header/footer integrity
  - logo/image integrity
  - structural diff summary (allowed-only changes)

### Exit criteria
- Preview reflects real final-render behavior for same template.

---

## Phase 5 - Observability, Policy, and Runtime Safety

### Goal
Add enterprise runtime controls and deep diagnostics.

### Backend modules to add
- `backend/modules/template/fidelity_metrics.py`
- `backend/modules/template/fidelity_policies.py`

### Backend modules to update
- `backend/services/workflow_executor.py` (policy enforcement + summary reporting)
- `backend/core/constants.py` (new warning/error code enums)
- `backend/api/routes/workflows.py` (fidelity diagnostics endpoint extension)

### Task checklist
- Track fidelity KPIs per workflow/template version.
- Track touched placeholder count and unresolved placeholder count.
- Block exports under strict policy if contract fails.
- Emit structured diagnostics for UI and ops.
- Track and alert on logo/header/footer drift incidents.
- Track media rel mismatch and missing image incidents by template version.

### Exit criteria
- All strict-policy blockers enforced consistently.
- Diagnostics visible in observability endpoints.

---

## Phase 6 - Enterprise Test Harness and Certification

### Goal
Create robust regression framework to guarantee fidelity.

### Backend tests to add
- `backend/tests/test_template_schema_extraction_docx.py`
- `backend/tests/test_template_schema_extraction_xlsx.py`
- `backend/tests/test_template_contract_validation.py`
- `backend/tests/test_docx_placeholder_filler_fidelity.py`
- `backend/tests/test_xlsx_placeholder_filler_fidelity.py`
- `backend/tests/test_template_preview_fidelity.py`
- `backend/tests/test_template_strict_policy_blocking.py`
- `backend/tests/test_docx_header_footer_preservation.py`
- `backend/tests/test_docx_logo_image_relationship_preservation.py`

### Test fixtures to add
- `backend/tests/fixtures/templates/enterprise_docx/*.docx`
- `backend/tests/fixtures/templates/enterprise_xlsx/*.xlsx`
- `backend/tests/fixtures/template_schemas/*.json`
- `backend/tests/fixtures/fidelity_expected_diffs/*.json`

### Task checklist
- Golden-file tests for exact placeholder-only mutation.
- XML-level diff checks for DOCX internals.
- Workbook structure checks for XLSX.
- High-volume test matrix (large templates, multi-language, long content).
- Explicit golden checks for:
  - `word/header*.xml` unchanged (except allowed placeholder regions if defined)
  - `word/footer*.xml` unchanged (except allowed placeholder regions if defined)
  - `word/_rels/*.rels` media relationships preserved

### Exit criteria
- Target pass rate achieved on golden suite.
- No silent fidelity regressions on CI.

---

## Phase 7 - Frontend UX for Enterprise Diagnostics

### Goal
Expose compile/schema/fidelity health clearly to users.

### Frontend modules to add
- `frontend/src/components/templates/TemplateSchemaPanel.tsx`
- `frontend/src/components/templates/TemplateValidationPanel.tsx`
- `frontend/src/components/templates/TemplateFidelityBadge.tsx`

### Frontend modules to update
- `frontend/src/components/templates/TemplateCard.tsx`
- `frontend/src/components/templates/TemplatePreviewModal.tsx`
- `frontend/src/pages/TemplatesPage.tsx`
- `frontend/src/api/types.ts`
- `frontend/src/api/templateApi.ts`

### Task checklist
- Show validation status and unresolved placeholders.
- Show schema version and placeholder counts.
- Show strict-policy block reason when compile/export fails.
- Show "fidelity integrity" badges:
  - Header/Footer preserved
  - Logo/Image preserved
  - Structure preserved

### Exit criteria
- Users can self-diagnose template compliance issues without logs.

---

## Phase 8 - Migration and Rollout

### Goal
Safely transition from current heuristic fill to strict fidelity engine.

### Backend modules to update
- `backend/core/config.py` (feature flags)
- `backend/services/template_service.py` (dual mode compile flags)
- `backend/modules/export/renderer.py` (compatibility mode switch)

### Feature flags
- `template_fidelity_strict_enabled`
- `template_fidelity_preview_v2_enabled`
- `template_schema_validation_blocking`
- `template_fidelity_media_integrity_blocking`

### Task checklist
- Dual-run mode for selected templates (compare old/new outputs).
- Tenant/template-level rollout controls.
- Rollback strategy and kill-switch.

### Exit criteria
- Pilot templates stable in production.
- Controlled progressive rollout completed.

---

## API Contract Backlog

### Template endpoints
- Extend `GET /templates` and `GET /templates/{id}` payloads:
  - `schema_version`
  - `validation_status`
  - `validation_errors`
  - `validation_warnings`
  - `placeholder_summary`

### New endpoints
- `GET /templates/{id}/schema`
- `POST /templates/{id}/validate`
- `GET /templates/{id}/fidelity-report`

### Workflow diagnostics
- Extend workflow diagnostics payload with:
  - `fidelity_status`
  - `touched_placeholders`
  - `unresolved_placeholders`
  - `blocked_by_policy`
  - `header_footer_integrity`
  - `media_integrity`

---

## Suggested Work Breakdown (Epic -> Story)

1. **Epic A: Schema + Validation**
   - Story A1: DOCX schema extractor
   - Story A2: XLSX schema extractor
   - Story A3: Validator + API

2. **Epic B: Strict Fill Engines**
   - Story B1: DOCX placeholder replacer
   - Story B2: XLSX placeholder replacer
   - Story B3: renderer integration + strict policy

3. **Epic C: Preview + UX**
   - Story C1: preview v2 backend
   - Story C2: frontend diagnostics panels

4. **Epic D: Testing + Rollout**
   - Story D1: golden fidelity suite
   - Story D2: dual-run rollout controls

---

## Non-Functional Requirements (NFRs)

- Determinism: same input/template/schema => same output.
- Observability: structured diagnostics on every compile/export.
- Performance targets:
  - DOCX strict fill p95 < 8s
  - XLSX strict fill p95 < 6s
- Reliability:
  - compile/export success >= 99% for compliant templates.
- Security:
  - sanitize external paths/assets
  - strict storage boundaries for template artifacts.
- Fidelity hard requirements:
  - logos/images preserved in place
  - header/footer preserved exactly
  - non-placeholder XML remains unchanged in strict mode

---

## LLM Support Policy (Required)

### Where LLM is required
- Content generation for placeholder payloads:
  - narrative section text
  - bullets and structured summaries
  - table row drafts (subject to schema constraints)

### Where LLM is optional
- Placeholder suggestion at template onboarding time.
- Quality rewriting (tone/length normalization) before deterministic fill.

### Where LLM is prohibited in strict mode
- Deciding where content should be inserted in DOCX/XLSX.
- Modifying template structure, styles, headers, footers, logos, or media relations.
- Performing any non-deterministic output mutation at render time.

### Implementation note
- Keep a strict boundary:
  - LLM output -> normalized content payload
  - deterministic filler -> exact placement into declared placeholders only

---

## Acceptance Definition (Enterprise Ready)

System is enterprise-ready when all are true:

- Strict placeholder-only mutation enforced for DOCX/XLSX.
- Contract validator blocks non-compliant templates in strict mode.
- Preview matches final render pipeline behavior.
- Golden fidelity suite passes on every CI run.
- Production telemetry confirms SLA, fidelity, and failure-policy compliance.
- Logos/images, headers, and footers are preserved exactly for compliant templates.

---

## Immediate Next 10 Engineering Tasks

1. Add `docs/TEMPLATE_FIDELITY_CONTRACT.md`.
2. Add `schema_version` + `placeholder_schema` to `TemplateRecord`.
3. Implement `schema_models.py`.
4. Implement `schema_extractor_docx.py`.
5. Implement `schema_extractor_xlsx.py`.
6. Implement `contract_validator.py`.
7. Add `GET /templates/{id}/schema`.
8. Introduce `docx_placeholder_filler.py` in compatibility mode.
9. Add golden test fixture pack for 3 DOCX + 3 XLSX templates.
10. Add strict policy flags in `core/config.py` (including media/header-footer integrity) and wire in renderer.

---

## Sample Enterprise Acceptance Test Cases (Given/When/Then)

### AT-01: DOCX exact fidelity with placeholder replacement only
- **Given** a compliant enterprise DOCX template with content controls for section placeholders
- **When** a workflow runs and fills all placeholders
- **Then** only placeholder content nodes are changed
- **And** all non-placeholder XML nodes remain unchanged
- **And** output passes XML diff allowlist checks

### AT-02: Header and footer preservation
- **Given** a DOCX template with branded header and legal footer
- **When** placeholder content is filled
- **Then** `word/header*.xml` and `word/footer*.xml` remain unchanged (except explicitly allowed placeholder zones)
- **And** header/footer integrity status is reported as `pass`

### AT-03: Logo and media relationship preservation
- **Given** a DOCX template containing company logo and additional embedded images
- **When** output is generated in strict mode
- **Then** media relationship entries in `word/_rels/*.rels` are preserved
- **And** original logo placement remains unchanged
- **And** media integrity status is reported as `pass`

### AT-04: Strict blocking on unresolved required placeholders
- **Given** a template where one required placeholder cannot be resolved from generated payload
- **When** export is attempted with strict policy enabled
- **Then** export is blocked with a deterministic error code
- **And** workflow diagnostics include unresolved placeholder details

### AT-05: Preview parity with final render
- **Given** a valid template and a deterministic sample payload
- **When** preview is generated and final export is generated from the same payload
- **Then** preview and final output are structurally equivalent under the same fidelity policy
- **And** the same integrity checks (header/footer/media) pass in both

### AT-06: XLSX structure preservation
- **Given** an XLSX template with formulas, validations, styles, and named ranges
- **When** placeholders are filled
- **Then** formulas and validations outside placeholder ranges remain unchanged
- **And** formatting and workbook structure remain unchanged outside allowed zones

### AT-07: LLM boundary enforcement in strict mode
- **Given** strict fidelity mode is enabled
- **When** LLM-generated content is produced for placeholders
- **Then** LLM output is accepted only as payload text/table/image metadata
- **And** no LLM-driven structural mutation is applied to DOCX/XLSX
- **And** deterministic filler performs all final placement

### AT-08: Template validation failure before compile
- **Given** an uploaded template with duplicate placeholder IDs
- **When** template validation runs
- **Then** template status is marked invalid
- **And** compile/export is blocked until template is corrected
- **And** API returns actionable validation errors

### AT-09: Enterprise legal/document details preservation
- **Given** a template containing watermark, page numbering, section breaks, and legal disclaimers
- **When** output is generated
- **Then** all these artifacts remain unchanged unless explicitly mapped as placeholders
- **And** fidelity report marks structure preservation as `pass`

### AT-10: Regression safety in CI
- **Given** a golden enterprise template fixture suite
- **When** CI executes fidelity regression tests
- **Then** build fails if any non-allowed XML/structure delta is detected
- **And** failure output includes precise artifact diff locations for debugging

