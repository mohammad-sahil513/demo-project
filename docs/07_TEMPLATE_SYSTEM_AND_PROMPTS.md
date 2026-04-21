# 07 — Template System, Section Definitions & Prompt Files

---

## Template System Overview

The template system produces one thing: `list[SectionDefinition]` — the section plan.

Every downstream phase (retrieval, generation, assembly, export) only knows about `SectionDefinition` objects. Whether the template was an inbuilt PDD template or a custom DOCX uploaded by the user, the section plan looks identical.

```
TWO INPUT PATHS → ONE OUTPUT SCHEMA
─────────────────────────────────────
Inbuilt template  →  registry.py  →  hardcoded List[SectionDefinition]
                                               │
Custom DOCX/XLSX  →  extractor                 │
                  →  classifier                │
                  →  planner       →  computed List[SectionDefinition]
                                               │
                                               ▼
                        WorkflowRecord.section_plan (stored as dicts)
                        Used by: retrieval, generation, assembly, export
```

---

## Template Compilation Pipeline (Custom Templates)

This runs as a background task immediately when a custom template is uploaded.

### Step 1 — `TemplateExtractor`

**For DOCX templates:**
- Opens the DOCX file with `python-docx`
- **StyleMap extraction:** walks standard heading styles (Heading 1–6), extracts font name, size, bold, italic, color, spacing. Extracts body text style. Extracts first table's border/fill styles. Reads page setup (margins, orientation).
- **DocumentSkeleton extraction:** scans the document body element by element:
  - Paragraphs with style `"Heading 1"` through `"Heading 6"` → `SkeletonElement(element_type="heading", level=1-6, text=...)`
  - Paragraphs where ALL runs are bold (faux-headings) → `SkeletonElement(level=None)` — flagged ambiguous
  - Table elements → reads first row only → `SkeletonElement(element_type="table_shell", table_headers=[...])`
  - Body paragraphs → **completely ignored** (stripped out)

**For XLSX templates:**
- Opens workbook with `openpyxl`
- For each sheet: reads sheet name, first row as column headers, column widths, header cell fill color
- Returns `sheet_map` and `sheet_structures` list

---

### Step 2 — `TemplateClassifier` (DOCX only)

**One LLM call classifies ALL sections in the template at once.**

- Takes the list of all heading elements from DocumentSkeleton
- Sends them all to GPT-5-mini in a single `invoke_json()` call
- Prompt (`prompts/template/classifier.yaml`) instructs the LLM to classify each heading:
  - `output_type`: text / table / diagram
  - `description`: what content belongs here
  - `generation_hints`: 4-6 specific topics
  - `retrieval_query`: optimised search query for Azure AI Search
  - `expected_length`: short / medium / long
  - `tone`: formal / technical / structured
  - `required_fields`: column names if table
  - `prompt_selector`: which generation prompt file to use
  - `is_complex`: true if needs GPT-5
  - `dependencies`: which other sections this depends on

- Returns JSON list matching the input heading order
- Graceful degradation: if LLM call fails → empty list → planner assigns defaults

**XLSX path:** No LLM needed. Each sheet = one section. Headers = `table_headers`. Classification is deterministic.

---

### Step 3 — `SectionPlanner`

Merges DocumentSkeleton elements with LLM classifications into final `list[SectionDefinition]`.

**Algorithm:**
1. Build a `title.lower() → classification_dict` lookup map
2. Walk skeleton elements in document order
3. For each heading element:
   - Generate new `section_id`
   - Track heading level to determine parent (level 1 has no parent; level 2 parent is the most recent level 1)
   - Look up classification by title → get output_type, description, hints, etc.
   - `execution_order` = 0-indexed counter (order they appear in document)
   - Resolve dependency titles → dependency section_ids using title→id lookup of already-processed sections
   - Create `SectionDefinition` with all fields

**Parent tracking example:**
```
Heading 1 "System Overview" → level=1, parent=None, id=sec-001
  Heading 2 "Architecture" → level=2, parent=sec-001, id=sec-002
  Heading 2 "Components"   → level=2, parent=sec-001, id=sec-003
Heading 1 "API Design"    → level=1, parent=None, id=sec-004
  Heading 2 "Endpoints"   → level=2, parent=sec-004, id=sec-005
```

---

### Step 4 — `PreviewGenerator`

Creates the user-visible preview shown before generation begins.

**DOCX preview:** Builds a skeleton `.docx` file using the extracted `StyleMap`:
- Each section becomes a heading with the correct style
- Followed by a placeholder paragraph: `"[Content will be generated here by AI based on your BRD document]"` in italic
- Heading styles applied from StyleMap

**XLSX preview (HTML table):** Converts Sheet1 of the uploaded workbook to an HTML table string:
- First row as `<th>` elements (header row)
- Subsequent rows as `<td>` elements
- Maximum 20 rows shown
- Simple border styling
- Saved as `.html` file for serving via `/preview-html` endpoint

---

## Inbuilt Template Definitions

### PDD Sections

All defined in `modules/template/inbuilt/pdd_sections.py` as hardcoded `SectionDefinition` objects.

| Title | Output Type | Prompt Selector | is_complex |
|-------|-------------|----------------|------------|
| Executive Summary | text | overview | false |
| Project Scope | text | scope | false |
| Stakeholder Matrix | table | stakeholders | false |
| Business Requirements | text | requirements | false |
| High-Level Architecture | diagram | architecture | **true** |
| Risk Register | table | risk_register | false |
| Assumptions and Constraints | text | assumptions | false |
| Success Criteria | text | default | false |

**PDD StyleMap:** Formal corporate blue theme. Heading 1: large, blue (#4472C4), bold. Heading 2: smaller, dark navy. Body: Calibri 11pt. Page margins: 1" all sides.

---

### SDD Sections

Defined in `modules/template/inbuilt/sdd_sections.py`.

| Title | Output Type | Prompt Selector | is_complex |
|-------|-------------|----------------|------------|
| System Overview | text | overview | false |
| Architecture Diagram | diagram | architecture | **true** |
| API Specification | table | api_specification | false |
| Data Models | text | requirements | false |
| Component Diagram | diagram | architecture | **true** |
| Sequence Diagrams | diagram | sequence | **true** |
| Security Design | text | architecture | false |
| Deployment Architecture | diagram | architecture | **true** |
| Testing Strategy | text | default | false |

**SDD StyleMap:** Technical grey/charcoal theme. More compact spacing for dense technical content.

---

### UAT Sections

Defined in `modules/template/inbuilt/uat_sections.py`. Each section = one Excel sheet.

| Title (= Sheet Name) | Output Type | Table Headers |
|----------------------|-------------|---------------|
| Summary | table | Field, Value |
| Test Cases | table | Test ID, Module, Test Scenario, Test Steps, Expected Result, Actual Result, Status, Tester |
| Defect Log | table | Defect ID, Severity, Module, Description, Steps to Reproduce, Status, Assigned To |
| Sign-Off | table | Stakeholder, Role, Decision, Sign-Off Date, Comments |

**UAT StyleMap:** Excel-compatible. Header fill: blue (#4472C4), white bold font. Alternating row fill: light blue (#D9E1F2).

---

## Prompt File Specifications

All prompt files are YAML with a `prompt_template` key containing the prompt string.
Variables injected with Python `.format()`. All variables wrapped in `{curly_braces}`.

---

### `prompts/template/classifier.yaml`

**Purpose:** Classify all custom template headings in one call.
**Model:** GPT-5-mini, low reasoning, 800 tokens
**Input variables:** `{doc_type}`, `{headings_json}`

**What the LLM must return:** JSON object with `"sections"` array, one entry per heading, each containing: `title`, `output_type`, `description`, `generation_hints`, `retrieval_query`, `expected_length`, `tone`, `required_fields`, `prompt_selector`, `is_complex`, `dependencies`.

**Response format:** Pure JSON, no markdown fences, no preamble. Parser strips fences if present.

---

### `prompts/generation/text/default.yaml`

**Purpose:** Generic text section generation. Fallback if specific selector file not found.
**Model:** GPT-5-mini (or GPT-5 if is_complex)
**Variables:** `{section_title}`, `{section_description}`, `{generation_hints}`, `{expected_length}`, `{tone}`, `{doc_type}`, `{doc_filename}`, `{context}`

**What LLM should produce:** Markdown prose with `##` and `###` sub-headings where appropriate. No filler text. Specific details drawn from `{context}`. Match `{tone}` and `{expected_length}`.

---

### `prompts/generation/text/overview.yaml`
**For:** Executive Summary, Project Overview sections
**Additional guidance:** Structured paragraphs — business value, key objectives, expected outcomes, stakeholder highlights.

### `prompts/generation/text/requirements.yaml`
**For:** Business/Functional Requirements sections
**Additional guidance:** Numbered or bulleted requirements. Each requirement specific and testable. Grouped by functional area.

### `prompts/generation/text/architecture.yaml`
**For:** Architecture description sections (NOT the diagram — the text description accompanying it)
**Additional guidance:** Component-by-component explanation. Mention integrations, data flows, technology choices.

### `prompts/generation/text/scope.yaml`
**For:** Project Scope sections
**Additional guidance:** Clear "In Scope" and "Out of Scope" subsections. Bullet lists of deliverables.

### `prompts/generation/text/assumptions.yaml`
**For:** Assumptions, Constraints, Dependencies sections
**Additional guidance:** Numbered list of assumptions. Separate list of constraints. Mark which could change.

### `prompts/generation/text/risks.yaml`
**For:** Risk description sections (narrative risk analysis, not the risk register table)
**Additional guidance:** Group by risk category. Include likelihood and impact narrative.

---

### `prompts/generation/table/default.yaml`

**Purpose:** Generic table generation. Fallback.
**Variables:** All standard + `{headers_instruction}` (injected by TableGenerator if table_headers are set)

**What LLM should produce:** Valid GFM markdown table. First row is header. At least 3 data rows. Data specific to the section topic. Columns matching the headers instruction exactly.

---

### `prompts/generation/table/stakeholders.yaml`
**For:** Stakeholder Matrix tables
**Guidance:** Each row = one stakeholder. Columns: Stakeholder, Role, Responsibility, Interest (High/Med/Low), Influence (High/Med/Low), Contact info. Draw from source content.

### `prompts/generation/table/traceability_matrix.yaml`
**For:** Requirements traceability matrix
**Guidance:** Links requirements to design elements to test cases. Multiple ID columns. Cross-reference format.

### `prompts/generation/table/risk_register.yaml`
**For:** Risk register tables
**Guidance:** Each row = one risk. Severity computed from Likelihood × Impact matrix. Include mitigation and owner.

### `prompts/generation/table/api_specification.yaml`
**For:** API endpoint specification tables
**Guidance:** Endpoint, Method, Description, Request params, Response format columns. Technical precision.

---

### `prompts/generation/diagram/default.yaml`

**Purpose:** PlantUML generation. Primary diagram prompt.
**Variables:** `{section_title}`, `{section_description}`, `{generation_hints}`, `{doc_type}`, `{context}`, `{diagram_format}` (="PlantUML"), `{correction_block}` (empty on first attempt, contains error info on retries)

**What LLM should produce:** Raw PlantUML code only. No explanation. No markdown fences. Must start with `@startuml` and end with `@enduml`. Max 15 nodes/components for clarity.

**Self-correction block format when retrying:**
```
PREVIOUS ATTEMPT FAILED.
Failed PlantUML code:
{the code that failed}

Error from renderer: HTTP 400: {kroki error message}

Fix the code to resolve this error. Do not repeat the same mistake.
```

---

### `prompts/generation/diagram/mermaid_default.yaml`

**Purpose:** Mermaid fallback when PlantUML fails 3 times.
**Variables:** Same as default.yaml but `{diagram_format}` = "Mermaid"

**What LLM should produce:** Raw Mermaid syntax only. No markdown fences. Start with diagram type keyword (`flowchart TD`, `sequenceDiagram`, `classDiagram`, `erDiagram`). Max 12 nodes. All labels with spaces must be quoted.

---

### `prompts/generation/diagram/architecture.yaml`
**For:** System architecture diagrams
**Guidance:** Show major system components as boxes/nodes. Show integrations as arrows. Label data flows. Include external systems.

### `prompts/generation/diagram/sequence.yaml`
**For:** Sequence diagrams
**Guidance:** Actor → system → sub-system → database sequence. Show request and response. Include error paths where relevant.

### `prompts/generation/diagram/flowchart.yaml`
**For:** Process flowcharts
**Guidance:** Start/end nodes. Decision diamonds. Process rectangles. Clear flow direction (TD or LR).

---

## Section Execution Order & Dependencies

**Execution order** determines:
1. The order sections appear in the output document
2. Which sections can run in parallel (those with no pending dependencies)

**Dependency rules:**
- Most sections have no dependencies (`dependencies = []`) — run in parallel
- Sections that logically reference other sections have dependencies
- Example: "Defect Log" depends on "Test Cases" (can't log defects before test cases are defined)
- Dependency resolution: planner converts dependency title strings → section_id references

**Parallel wave example for a typical PDD:**
```
Wave 1 (all independent, run together):
  - Executive Summary
  - Project Scope
  - Stakeholder Matrix
  - Business Requirements
  - Risk Register
  - Assumptions and Constraints

Wave 2 (depends on wave 1 sections):
  - High-Level Architecture  ← depends on Business Requirements
  - Success Criteria         ← depends on Project Scope
```
