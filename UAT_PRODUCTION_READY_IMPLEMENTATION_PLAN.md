# UAT Production-Ready Implementation Plan

## Objective
Deliver a robust UAT pipeline where custom UAT XLSX templates are reliably interpreted and enforced, generated outputs match expected sheet/column structure, retrieval and prompting are tuned for UAT quality, and users can preview/download with confidence.

## Current Gaps to Close
- XLSX template extraction currently captures sheet names, not full column schema.
- Export writes generated rows but does not strictly validate/enforce template column contracts.
- XLSX preview is sheet-list oriented, not schema/value aware.
- UAT uses mostly generic generation prompts/retrieval behavior.
- Section planning phase contains a stub and lacks UAT-specific planning rules.

## Target Outcomes (Definition of Done)
- UAT template compile extracts per-sheet headers and key field metadata.
- Workflow stores and uses UAT schema contract during generation/export.
- Export enforces header mapping and emits actionable warnings/errors on mismatches.
- UAT prompts and retrieval strategy are domain-specific and repeatable.
- Preview experience supports UAT template schema visibility before workflow runs.
- End-to-end tests validate UAT upload -> compile -> workflow -> preview -> download.

---

## Phase 1: Template Schema Extraction and Persistence

### Scope
Enhance XLSX template extraction so compile captures not only sheet names but also header row schema for each sheet.

### Implementation Tasks
1. Extend XLSX extractor in `backend/modules/template/extractor.py`:
   - Read workbook sheets and detect header row (row 1 baseline; allow heuristics later).
   - Capture per-sheet:
     - `sheet_name`
     - `headers[]`
     - `column_count`
     - optional `required_columns[]` (initially same as headers unless configured).
2. Extend template metadata model (`sheet_map`) to include schema payload.
3. Persist schema in template record at compile time in `backend/services/template_service.py`.
4. Update compile diagnostics payload to expose schema metadata for API consumers.

### Acceptance Criteria
- Uploading UAT `.xlsx` template stores sheet headers in template JSON.
- `GET /templates/{id}` returns sheet metadata sufficient for downstream validation.
- Compile fails with clear error if XLSX has no usable sheet/header structure.

---

## Phase 2: Schema-Aware UAT Export

### Scope
Enforce template schema in XLSX export and avoid silently writing malformed output.

### Implementation Tasks
1. Update `backend/modules/export/xlsx_builder.py`:
   - Resolve target worksheet by schema mapping first.
   - Validate generated table headers against template schema.
   - Map generated columns to template headers (exact + normalized matching).
   - Fill missing required columns as `TBD`.
   - Preserve template header row and formatting where possible.
2. Emit structured warnings/errors:
   - `schema_mismatch`
   - `missing_required_columns`
   - `unmapped_generated_columns`
3. Bubble export warnings to workflow warnings and output metadata.

### Acceptance Criteria
- UAT output workbook always conforms to template sheet/header contract.
- Mismatch scenarios are visible via diagnostics and do not fail silently.
- Downloaded XLSX contains expected sheets and aligned columns.

---

## Phase 3: UAT-Specific Prompting and Retrieval Strategy

### Scope
Improve quality/relevance of generated UAT content using dedicated prompts and retrieval patterns.

### Implementation Tasks
1. Add UAT-focused prompts under `backend/prompts/generation/`:
   - test case generation
   - defect log generation
   - sign-off summary
   - traceability mapping
2. Introduce UAT prompt selector mapping in section definitions (`backend/modules/template/inbuilt/uat_sections.py`).
3. Add UAT-specific retrieval query scaffolds:
   - feature-based test scenario extraction
   - acceptance criteria evidence extraction
   - risk/edge-case retrieval
4. Add normalization rules for table output to enforce required UAT fields.

### Acceptance Criteria
- UAT sections use dedicated prompts instead of only generic defaults.
- Retrieval results for UAT sections show improved relevance/citations.
- Generated test case and defect tables consistently include required fields.

---

## Phase 4: Workflow Planning and Validation Hardening

### Scope
Replace stub planning and add strong pre-export validation gates for UAT workflows.

### Implementation Tasks
1. Replace section planning stub in `backend/services/workflow_executor.py` with:
   - UAT section dependency checks
   - schema readiness checks
   - required retrieval/generation preconditions
2. Add validation gate before export:
   - block export when critical schema violations exist.
3. Improve observability metrics for UAT:
   - per-sheet row counts
   - schema compliance rate
   - low-evidence section counts

### Acceptance Criteria
- UAT workflow cannot complete as "success" with critical structural mismatches.
- Observability endpoints expose UAT-relevant quality metrics.

---

## Phase 5: Preview and API Experience

### Scope
Improve UAT preview to be useful for QA before generation.

### Implementation Tasks
1. Extend preview payload/API to include schema summary:
   - sheets, headers, required columns.
2. Improve frontend template preview rendering for UAT:
   - show per-sheet headers and counts (not only sheet names).
3. Add explicit user-facing validation hints on template upload.

### Acceptance Criteria
- Users can confirm template sheet/column readiness before running workflow.
- Preview surface reflects the same schema contract used by export.

---

## Phase 6: Testing, Quality Gates, and Release Readiness

### Scope
Guarantee reliability with automated tests and UAT checklist signoff.

### Test Plan
1. Unit tests:
   - extractor schema parsing
   - xlsx_builder schema mapping and mismatch paths
   - prompt selector routing for UAT sections
2. Integration tests:
   - upload UAT template -> compile -> workflow run -> export -> download
   - failure cases (missing headers, mismatched columns, empty evidence)
3. Regression tests:
   - ensure PDD/SDD DOCX flows remain unchanged.

### Release Gates
- All backend tests passing.
- No new linter/type errors.
- Manual QA signoff for:
  - UAT `.xlsx` upload
  - UAT schema preview
  - UAT generation correctness
  - UAT download integrity

---

## Risks and Mitigations
- **Risk:** Diverse real-world XLSX formats break header detection.
  - **Mitigation:** Start with strict row-1 rule + configurable heuristics.
- **Risk:** Over-strict schema validation blocks valid outputs.
  - **Mitigation:** Severity levels (`warning` vs `blocking_error`) and clear diagnostics.
- **Risk:** Prompt changes regress non-UAT quality.
  - **Mitigation:** Keep UAT prompt routing isolated by doc type.

## Suggested Execution Order
1. Phase 1 (schema extraction)
2. Phase 2 (schema-aware export)
3. Phase 6 partial tests for Phases 1-2
4. Phase 3 (prompt/retrieval tuning)
5. Phase 4 (planning/validation hardening)
6. Phase 5 (preview UX)
7. Phase 6 final full regression + release gate

## Delivery Milestones
- **M1:** Schema extraction + persistence complete.
- **M2:** Schema-enforced UAT export complete.
- **M3:** UAT prompt/retrieval quality uplift complete.
- **M4:** Full E2E validation + release-ready signoff.

