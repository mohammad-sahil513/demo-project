# Project Context Export

Generated on: `2026-04-30 10:26:59`

## Included Roots

- `C:\Office Stuff\PROJECT\demo-project\frontend`

## Folder Structure

### Root: `frontend`

```text
frontend
├── public
│   └── brand
│       └── ey-logo.svg
├── src
│   ├── api
│   │   ├── client.ts
│   │   ├── documentApi.ts
│   │   ├── errors.ts
│   │   ├── outputApi.ts
│   │   ├── templateApi.ts
│   │   ├── types.ts
│   │   ├── workflowApi.test.ts
│   │   └── workflowApi.ts
│   ├── components
│   │   ├── layout
│   │   │   └── Navbar.tsx
│   │   ├── output
│   │   │   ├── CitationPanel.tsx
│   │   │   ├── DocumentTabs.tsx
│   │   │   ├── DocxViewer.tsx
│   │   │   ├── DownloadPanel.tsx
│   │   │   └── SectionSidebar.tsx
│   │   ├── progress
│   │   │   └── ProgressBar.tsx
│   │   ├── templates
│   │   │   ├── AddTemplatePanel.tsx
│   │   │   ├── TemplateCard.tsx
│   │   │   └── TemplatePreviewModal.tsx
│   │   └── upload
│   │       ├── DocumentSelector.tsx
│   │       ├── FileUploader.tsx
│   │       └── TemplateSelector.tsx
│   ├── pages
│   │   ├── OutputPage.tsx
│   │   ├── ProgressPage.tsx
│   │   ├── TemplatePreviewPage.tsx
│   │   ├── TemplatesPage.tsx
│   │   └── UploadPage.tsx
│   ├── store
│   │   └── useJobStore.ts
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.example
├── FRONTEND_DEPENDENCIES.md
├── index.html
├── package-lock.json
├── package.json
├── postcss.config.js
├── README.md
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── vitest.config.ts
```

## File Contents

### Files from `frontend`

#### `frontend/FRONTEND_DEPENDENCIES.md`

**Language hint:** `markdown`

```markdown
# Frontend Dependencies (Detailed)

This document explains all dependencies required by the `frontend` app, why each one exists, where it is used, and what can break if it is removed or changed.

It covers:

1. Runtime (`dependencies`) packages
2. Development/build (`devDependencies`) packages
3. Environment and tooling dependencies
4. Backend/API contract dependencies (critical for runtime behavior)
5. Optional replacement guidance

---

## 1) Runtime Dependencies (`package.json -> dependencies`)

## `react` (`^18.2.0`)
- **Role:** Core UI library used by the entire app.
- **Why needed:** All pages and components are React function components with hooks.
- **Where used:** Every file under `src/` that returns JSX.
- **If removed/broken:** App cannot render; build fails immediately.

## `react-dom` (`^18.2.0`)
- **Role:** React renderer for browser DOM.
- **Why needed:** Mounts root app into `index.html`.
- **Where used:** `src/main.tsx` via `createRoot`.
- **If removed/broken:** React app cannot attach to DOM.

## `react-router-dom` (`^6.22.3`)
- **Role:** Client-side routing.
- **Why needed:** Navigation between upload, progress, output, and templates pages.
- **Where used:** Route setup and `useNavigate` calls in pages.
- **If removed/broken:** Route transitions fail; app becomes single-page without navigation logic.

## `zustand` (`^4.5.2`)
- **Role:** Lightweight state management for job/workflow state.
- **Why needed:** Shares document ID, selected templates, workflow IDs, progress, and output data across pages.
- **Where used:** `src/store/useJobStore.ts` and consumers in `src/pages/*`, `src/components/*`.
- **If removed/broken:** Cross-page generation flow state is lost; progress/output pages cannot function reliably.

## `axios` (`^1.6.7`)
- **Role:** HTTP client for backend API requests.
- **Why needed:** Handles uploads, workflow operations, templates CRUD, and output downloads.
- **Where used:** `src/api/client.ts`, `src/api/documentApi.ts`, `src/api/workflowApi.ts`, `src/api/templateApi.ts`.
- **Special behavior:** Response interceptor unwraps backend success envelope (`{ success: true, data: ... }`).
- **If removed/broken:** All backend communication fails.

## `react-markdown` (`^9.0.1`)
- **Role:** Renders generated section content (markdown) in output view.
- **Why needed:** Generated sections are displayed in markdown format.
- **Where used:** Output rendering components (markdown viewer path).
- **If removed/broken:** Section content may render as raw markdown text or fail to render rich formatting.

## `remark-gfm` (`^4.0.0`)
- **Role:** Plugin for GitHub Flavored Markdown features (tables, checklists, strikethrough).
- **Why needed:** Improves display of generated markdown content from backend.
- **Where used:** Markdown rendering pipeline with `react-markdown`.
- **If removed/broken:** GFM-specific markdown formatting may degrade.

## `docx-preview` (`^0.3.7`)
- **Role:** Browser-side DOCX renderer.
- **Why needed:** Template preview modal renders uploaded template `.docx` visually before selection.
- **Where used:** `src/components/templates/TemplatePreviewModal.tsx` (`renderAsync`).
- **If removed/broken:** Template preview popup cannot render DOCX content.

## `lucide-react` (`^0.363.0`)
- **Role:** Icon library.
- **Why needed:** Visual icons used throughout upload, progress, template, and output UI.
- **Where used:** Multiple components/pages using icon imports.
- **If removed/broken:** UI compiles fail where icons are imported.

## `clsx` (`^2.1.0`)
- **Role:** Conditional className utility.
- **Why needed:** Simplifies dynamic Tailwind class joining (if used in current or future components).
- **Where used:** Utility-level class composition patterns (may be limited in current snapshot).
- **If removed/broken:** Files importing it fail; can be replaced with template string logic.

---

## 2) Development Dependencies (`package.json -> devDependencies`)

## `typescript` (`^5.2.2`)
- **Role:** Type system and TS compiler.
- **Why needed:** Codebase is TypeScript (`.ts` / `.tsx`), build script runs `tsc`.
- **Where used:** Entire compile/build pipeline.
- **If removed/broken:** Type checks and TypeScript compilation fail.

## `vite` (`^5.2.0`)
- **Role:** Dev server and production bundler.
- **Why needed:** Runs local dev (`npm run dev`) and builds production assets (`vite build`).
- **Where used:** Script commands + `vite.config.ts`.
- **If removed/broken:** Dev server and build process stop working.

## `@vitejs/plugin-react` (`^4.2.1`)
- **Role:** Vite plugin for React fast refresh and JSX transform.
- **Why needed:** Proper React DX and compilation.
- **Where used:** `vite.config.ts` plugins list.
- **If removed/broken:** React HMR may fail; JSX tooling behavior degrades.

## `tailwindcss` (`^3.4.1`)
- **Role:** Utility-first CSS framework.
- **Why needed:** UI styling is built with Tailwind classes.
- **Where used:** Component classNames + `tailwind.config.js`.
- **If removed/broken:** Styles disappear or become incorrect.

## `postcss` (`^8.4.38`)
- **Role:** CSS processing engine used by Tailwind pipeline.
- **Why needed:** Tailwind plugin execution in CSS build path.
- **Where used:** `postcss.config.js`.
- **If removed/broken:** Tailwind CSS processing fails.

## `autoprefixer` (`^10.4.18`)
- **Role:** Adds vendor prefixes for browser compatibility.
- **Why needed:** Ensures CSS works across target browsers.
- **Where used:** PostCSS plugin chain.
- **If removed/broken:** Some CSS features may not work in older browser targets.

## `@types/react` (`^18.2.66`)
- **Role:** Type definitions for React.
- **Why needed:** TypeScript typing support for React APIs.
- **Where used:** TS compile/type-check.
- **If removed/broken:** TS errors for React types.

## `@types/react-dom` (`^18.2.22`)
- **Role:** Type definitions for ReactDOM APIs.
- **Why needed:** Typing support for root mounting and ReactDOM calls.
- **Where used:** TS compile/type-check.
- **If removed/broken:** TS errors around ReactDOM usage.

---

## 3) Scripts and Toolchain Dependencies

Defined scripts:

- `npm run dev` -> `vite`
- `npm run build` -> `tsc && vite build`
- `npm run preview` -> `vite preview`

Operational dependency chain:

1. Node.js + npm installed
2. `npm install` resolves lockfile and packages
3. Vite serves app at `http://localhost:3000`
4. Vite proxy forwards `/api` to backend target during local dev

If any of these are missing, frontend startup/build fails even if source code is valid.

---

## 4) Environment Variable Dependencies

From `.env.example` and Vite config:

## `VITE_API_BASE` (default `/api`)
- **Purpose:** Axios base path for all API requests.
- **Expected value in current setup:** `/api`
- **Risk if changed incorrectly:** Frontend requests wrong path and receives 404/CORS failures.

## `BACKEND_ORIGIN` or `VITE_DEV_PROXY_TARGET`
- **Purpose:** Dev-only backend origin for Vite proxy.
- **Default fallback:** `http://127.0.0.1:8000`
- **Risk if changed incorrectly:** Frontend dev server runs but API calls fail because proxy points to wrong backend host/port.

---

## 5) Backend Contract Dependencies (Non-NPM but Critical)

The frontend has strict runtime dependency on backend API shape and endpoint behavior.

## Required response envelope behavior
- Frontend API client unwraps only when payload matches:
  - `success: true`
  - `data: ...`
- This is implemented in `src/api/client.ts`.
- If backend stops sending envelope for success paths, data access patterns can break.

## Required endpoint set
- `POST /api/documents/upload`
- `POST /api/workflow-runs`
- `GET /api/workflow-runs/{workflow_run_id}/status`
- `GET /api/workflow-runs/{workflow_run_id}`
- `GET /api/templates`
- `GET /api/templates/{template_id}`
- `GET /api/templates/{template_id}/download`
- `POST /api/templates/upload`
- `DELETE /api/templates/{template_id}`
- `GET /api/outputs/{output_id}/download`

## Required workflow fields
The UI depends on these keys in workflow payloads:
- `workflow_run_id`
- `status`
- `current_phase`
- `overall_progress_percent`
- optional `current_step_label`
- `output_id`
- `assembled_document.sections[]` with `section_id`, `title`, optional `content`

## Required status semantics
- `FAILED` -> show failure state
- `COMPLETED` -> enable output loading/download
- anything else -> treated as running

## Binary download behavior dependencies
- Template and output download endpoints must return valid binary payloads (`.docx`).
- If these endpoints return JSON/error HTML, preview/download UX fails.

---

## 6) Dependency Map by Feature

## Upload and job creation
- React + React Router + Zustand + Axios + backend `/documents/upload` + `/workflow-runs`

## Progress tracking
- Zustand + Axios polling + backend `/workflow-runs/{id}/status`

## Output display
- React Markdown + remark-gfm + backend assembled sections payload

## Template management
- Axios + docx-preview + backend templates CRUD/download endpoints

## Styling and UI
- Tailwind + PostCSS + Autoprefixer + lucide-react

---

## 7) High-Risk Dependencies (Do Not Change Without Validation)

1. `src/api/client.ts` envelope unwrapping logic
2. `/api` prefix consistency between frontend and backend
3. Workflow status field names and values
4. Template/output DOCX binary download endpoints
5. Zustand store keys used across pages

Any change to these requires end-to-end testing of:
- upload -> workflow start -> progress polling -> output render -> DOCX download

---

## 8) Minimal Dependency Set (If You Want to Trim Later)

Hard-minimum runtime for current UX:
- `react`, `react-dom`, `react-router-dom`, `zustand`, `axios`, `react-markdown`, `remark-gfm`, `docx-preview`, `lucide-react`

Possible optional candidate:
- `clsx` (only if truly unused across codebase and replaced safely)

Do not remove `docx-preview` if template preview must remain.

---

## 9) Quick Verification Checklist After Any Dependency Change

1. `npm install` completes without peer conflicts
2. `npm run dev` starts on port 3000
3. `/templates`: list, upload, preview, delete all work
4. `/`: upload file + select types/templates + start generation
5. `/progress`: per-type progress updates and completion/failure handling
6. `/output`: sections render markdown correctly
7. Download buttons open valid DOCX for completed runs

---

## 10) Source of Truth

- Package manifest: `frontend/package.json`
- Dev server/proxy: `frontend/vite.config.ts`
- Env contract: `frontend/.env.example`
- Flow and API contract summary: `frontend/README.md`
```

#### `frontend/index.html`

**Language hint:** `html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI SDLC — Document Generator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;1,14..32,400&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

#### `frontend/postcss.config.js`

**Language hint:** `javascript`

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

#### `frontend/README.md`

**Language hint:** `markdown`

```markdown
# AI SDLC — Frontend

React + TypeScript + Vite + Tailwind UI for the document generation workflow. It talks to the **FastAPI** backend using the real `/api` contract (`success_response` envelopes are unwrapped in the Axios client).

## Stack

- React 18, Vite 5, TypeScript
- Tailwind CSS (black / `#FFD400` theme)
- Zustand for client state
- Axios (`baseURL` from `VITE_API_BASE`, default `/api`)
- react-markdown + remark-gfm (section preview)
- docx-preview (template DOCX popup preview)
- lucide-react

## Setup

```bash
npm install
npm run dev
```

App dev server: **http://localhost:3000** (see `vite.config.ts`).

The dev server proxies `/api` to **`BACKEND_ORIGIN`**, then **`VITE_DEV_PROXY_TARGET`**, then **`http://127.0.0.1:8000`** (see [`vite.config.ts`](vite.config.ts)). Set one of those in `frontend/.env` to match `APP_HOST` / `APP_PORT` in `backend/.env`.

Copy optional env:

```bash
cp .env.example .env
```

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE` | API path prefix for Axios (default `/api`). In dev, the Vite dev server proxies `/api` to the backend. |
| `BACKEND_ORIGIN` or `VITE_DEV_PROXY_TARGET` | Dev-only: origin of the FastAPI server for the Vite proxy (not exposed to `import.meta.env`). |

## API flow (aligned with backend)

Responses use `{ success, message, data, ... }`; the client interceptor exposes **`data`** as `response.data` to callers.

1. `POST /api/documents/upload` — multipart `file` → `document_id`
2. For each selected deliverable type (PDD / SDD / UAT), `POST /api/workflow-runs` with  
   `{ document_id, template_id, "start_immediately": true }` — one workflow run per type (templates must match that type).
3. Poll `GET /api/workflow-runs/{workflow_run_id}/status` for each run until all `COMPLETED` or any `FAILED`.
4. Review: `GET /api/workflow-runs/{workflow_run_id}` → `assembled_document.sections` for markdown content.
5. Download: `GET /api/outputs/{output_id}/download` when the workflow exposes `output_id` and export is ready.

Templates:

- `GET /api/templates` → `{ items, total }`
- `GET /api/templates/{template_id}` → template metadata
- `GET /api/templates/{template_id}/download` → raw uploaded template `.docx` (used by popup preview)
- `POST /api/templates/upload` — form fields `file`, `template_type` (e.g. `PDD` / `SDD` / `UAT`), optional `version`
- `DELETE /api/templates/{template_id}` — remove template (metadata + `.docx` binary when present)

## Routes

| Route | Purpose |
|-------|---------|
| `/` | Upload BRD, select output types, pick one template per type |
| `/progress` | Aggregated progress for all workflow runs |
| `/output` | Tabs per deliverable, section sidebar, markdown viewer, per-type DOCX download |
| `/templates` | Template library + upload + popup template preview |

## Template UX Notes

- Upload page template section is **selection-only** (no inline template upload tile).
- Templates are uploaded from `/templates`, then selected on `/`.
- Both template library and upload selection provide **Preview** that opens a popup modal.
- Popup preview renders the **actual DOCX layout** and includes collapsible metadata (hidden by default).

## Manual test checklist

1. Start backend on the proxied port (default 8000).
2. `npm run dev` in `frontend/`.
3. Upload template(s) on `/templates`, and verify Preview opens a popup with DOCX rendering.
4. Upload a PDF/DOCX on `/`, ensure each selected PDD/SDD/UAT has a selected template.
5. Generate → progress → review → download DOCX when `output_id` is present.

## Notes

- **ZIP “download all”** is not implemented server-side; the UI exposes per-type DOCX downloads only.
- Refreshing the browser clears Zustand state; you will lose in-progress workflow IDs unless persistence is added later.
```

#### `frontend/src/api/client.ts`

**Language hint:** `typescript`

```typescript
import axios, { type AxiosError, type AxiosResponse } from 'axios'
import { getApiErrorMessage } from './errors'
import type { ApiEnvelope } from './types'

const baseURL = import.meta.env.VITE_API_BASE ?? '/api'

const client = axios.create({
  baseURL,
  timeout: 120000,
})

function isSuccessEnvelope(payload: unknown): payload is ApiEnvelope {
  return (
    typeof payload === 'object' &&
    payload !== null &&
    'success' in payload &&
    (payload as ApiEnvelope).success === true &&
    'data' in payload
  )
}

client.interceptors.response.use(
  (res: AxiosResponse) => {
    const payload = res.data
    if (isSuccessEnvelope(payload)) {
      return { ...res, data: payload.data }
    }
    return res
  },
  (err: AxiosError) => {
    const msg = getApiErrorMessage(err)
    console.error('[API Error]', msg, err.response?.status)
    return Promise.reject(err)
  }
)

export default client
export { baseURL }
```

#### `frontend/src/api/documentApi.ts`

**Language hint:** `typescript`

```typescript
import client from './client'
import type { DocumentUploadData } from './types'

export async function uploadDocument(file: File): Promise<DocumentUploadData> {
  const form = new FormData()
  form.append('file', file)
  const res = await client.post<DocumentUploadData>('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}
```

#### `frontend/src/api/errors.ts`

**Language hint:** `typescript`

```typescript
import { isAxiosError, type AxiosError } from 'axios'

type ErrorBody = {
  success?: boolean
  message?: string
  errors?: Array<{ code?: string; message?: string; details?: unknown }>
  detail?: unknown
}

function formatDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'object' && item !== null && 'msg' in item) {
          return String((item as { msg: string }).msg)
        }
        return JSON.stringify(item)
      })
      .join('; ')
  }
  if (detail !== null && typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return String(detail)
}

function formatEnvelopeErrors(errors: ErrorBody['errors']): string {
  if (!errors?.length) return ''
  return errors
    .map((e) => {
      const parts = [e.code, e.message].filter(Boolean)
      return parts.join(': ')
    })
    .filter(Boolean)
    .join('; ')
}

/**
 * Human-readable message from API failures (FastAPI `detail`, backend `error_response`, or network).
 */
export function getApiErrorMessage(err: unknown, fallback = 'Request failed'): string {
  if (isAxiosError(err)) {
    const ax = err as AxiosError<ErrorBody>
    const data = ax.response?.data
    if (data && typeof data === 'object') {
      if (data.success === false && typeof data.message === 'string' && data.message) {
        const errPart = formatEnvelopeErrors(data.errors)
        return errPart ? `${data.message} (${errPart})` : data.message
      }
      if (data.detail !== undefined) {
        const d = formatDetail(data.detail)
        if (d) return d
      }
      const errPart = formatEnvelopeErrors(data.errors)
      if (errPart) return errPart
      if (typeof data.message === 'string' && data.message) {
        return data.message
      }
    }
    if (ax.message) return ax.message
  }
  if (err instanceof Error && err.message) return err.message
  return fallback
}
```

#### `frontend/src/api/outputApi.ts`

**Language hint:** `typescript`

```typescript
import { baseURL } from './client'

function downloadUrl(path: string): string {
  if (baseURL.startsWith('http')) {
    return `${baseURL.replace(/\/$/, '')}${path}`
  }
  return `${window.location.origin}${baseURL.replace(/\/$/, '')}${path}`
}

export const outputApi = {
  downloadByOutputId: (outputId: string) => {
    window.open(downloadUrl(`/outputs/${outputId}/download`), '_blank')
  },
}
```

#### `frontend/src/api/templateApi.ts`

**Language hint:** `typescript`

```typescript
import client from './client'
import type { TemplateDto, TemplateListData } from './types'
import type { Template } from '../store/useJobStore'

function dtoToTemplate(d: TemplateDto): Template {
  const t = (d.template_type || '').toUpperCase()
  const isCustom =
    t === 'CUSTOM' ||
    d.status === 'UPLOADED' ||
    (d.template_type != null && !['PDD', 'SDD', 'UAT'].includes(t))
  return {
    id: d.template_id,
    template_id: d.template_id,
    filename: d.filename,
    type: d.template_type || d.template_id,
    template_type: d.template_type,
    status: d.status,
    description: d.filename,
    sections_preview: [],
    is_custom: isCustom,
  }
}

export interface TemplateUploadPayload {
  file: File
  template_type: string
  version?: string
}

export interface TemplatePreview {
  id: string
  type: string
  description: string
  sections_preview: string[]
  content?: string
  section_details?: Array<{ title: string; description: string }>
}

export const templateApi = {
  listTemplates: async (): Promise<Template[]> => {
    const res = await client.get<TemplateListData>('/templates')
    const data = res.data
    return (data.items ?? []).map(dtoToTemplate)
  },

  getTemplateRaw: async (templateId: string): Promise<TemplateDto> => {
    const res = await client.get<TemplateDto>(`/templates/${templateId}`)
    return res.data
  },

  getTemplateBinary: async (templateId: string): Promise<ArrayBuffer> => {
    const res = await client.get<ArrayBuffer>(`/templates/${templateId}/download`, {
      responseType: 'arraybuffer',
    })
    return res.data
  },

  getTemplatePreview: async (templateId: string): Promise<TemplatePreview> => {
    const raw = await templateApi.getTemplateRaw(templateId)
    return {
      id: raw.template_id,
      type: raw.template_type || raw.template_id,
      description: raw.filename,
      sections_preview: [],
    }
  },

  uploadTemplate: async (payload: TemplateUploadPayload) => {
    const form = new FormData()
    form.append('file', payload.file)
    form.append('template_type', payload.template_type)
    if (payload.version) form.append('version', payload.version)
    const res = await client.post('/templates/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  deleteTemplate: async (templateId: string) => {
    const res = await client.delete(`/templates/${templateId}`)
    return res.data
  },
}
```

#### `frontend/src/api/types.ts`

**Language hint:** `typescript`

```typescript
/** Backend success envelope (unwrapped by axios interceptor). */
export interface ApiEnvelope<T = unknown> {
  success: boolean
  message: string
  data: T
  errors: unknown[]
  meta: Record<string, unknown>
}

export interface DocumentUploadData {
  document_id: string
  filename: string
  content_type?: string
  size?: number
  status?: string
  created_at?: string
}

export interface WorkflowCreateData {
  workflow_run_id: string
  status: string
  current_phase: string
  overall_progress_percent: number
  document_id: string
  template_id: string | null
  output_id: string | null
  dispatch_mode?: string | null
  created_at?: string
  updated_at?: string
  [key: string]: unknown
}

export interface CitationDto {
  path: string
  page?: number | null
  content_type?: string
  chunk_id: string
}

export interface SectionEvidenceBundleDto {
  context_text?: string
  citations?: CitationDto[]
}

export interface AssembledSectionRow {
  section_id: string
  title: string
  execution_order?: number
  output_type?: string
  content?: string | null
  metadata?: Record<string, unknown>
}

export interface AssembledDocumentData {
  workflow_run_id: string
  template_id: string | null
  total_sections: number
  title: string
  sections: AssembledSectionRow[]
}

export interface WorkflowStatusData extends Record<string, unknown> {
  workflow_run_id: string
  status: string
  current_phase: string
  overall_progress_percent: number
  current_step_label?: string | null
  document_id: string
  template_id: string | null
  output_id: string | null
  assembled_document?: AssembledDocumentData | null
  section_retrieval_results?: Record<string, SectionEvidenceBundleDto>
}

export interface TemplateDto {
  template_id: string
  filename: string
  template_type: string | null
  version: string | null
  status: string
  created_at: string
  updated_at: string
  compile_job_id: string | null
  compiled_artifacts: unknown[]
}

export interface TemplateListData {
  items: TemplateDto[]
  total: number
}
```

#### `frontend/src/api/workflowApi.test.ts`

**Language hint:** `typescript`

```typescript
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { subscribeToWorkflowEvents } from './workflowApi'

describe('subscribeToWorkflowEvents', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'EventSource',
      class MockEventSource {
        static readonly CONNECTING = 0
        static readonly OPEN = 1
        static readonly CLOSED = 2
        url: string
        readyState: number = MockEventSource.CONNECTING
        onopen: (() => void) | null = null
        onmessage: ((e: MessageEvent) => void) | null = null
        onerror: ((e: Event) => void) | null = null

        constructor(url: string) {
          this.url = url
          queueMicrotask(() => {
            this.readyState = MockEventSource.OPEN
            this.onopen?.()
          })
        }

        close() {
          this.readyState = MockEventSource.CLOSED
        }
      }
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('builds stream URL and forwards parsed events', async () => {
    const seen: string[] = []
    const { close, eventSource } = subscribeToWorkflowEvents('wf-abc', {
      onEvent: (e) => seen.push(e.type),
    })

    await new Promise<void>((r) => queueMicrotask(r))

    expect(eventSource.url).toContain('/workflow-runs/wf-abc/events')
    eventSource.onmessage?.({
      data: JSON.stringify({ type: 'phase.started', workflow_run_id: 'wf-abc', phase: 'INGESTION' }),
    } as MessageEvent)

    expect(seen).toEqual(['phase.started'])
    close()
    expect(eventSource.readyState).toBe(2)
  })
})
```

#### `frontend/src/api/workflowApi.ts`

**Language hint:** `typescript`

```typescript
import client, { baseURL } from './client'
import type { WorkflowCreateData, WorkflowStatusData } from './types'

export interface WorkflowSseEvent {
  type: string
  workflow_run_id: string
  timestamp?: string
  [key: string]: unknown
}

export interface SubscribeWorkflowEventsHandlers {
  onEvent?: (event: WorkflowSseEvent) => void
  onOpen?: () => void
  onError?: (ev: Event) => void
}

export function subscribeToWorkflowEvents(
  workflowRunId: string,
  handlers: SubscribeWorkflowEventsHandlers = {}
): { close: () => void; eventSource: EventSource } {
  const url = `${baseURL}/workflow-runs/${encodeURIComponent(workflowRunId)}/events`
  const es = new EventSource(url)

  es.onopen = () => handlers.onOpen?.()

  es.onmessage = (e: MessageEvent<string>) => {
    try {
      const parsed = JSON.parse(e.data) as WorkflowSseEvent
      if (parsed && typeof parsed.type === 'string') {
        handlers.onEvent?.(parsed)
      }
    } catch {
      /* ignore non-JSON payloads */
    }
  }

  es.onerror = (ev) => handlers.onError?.(ev)

  return {
    close: () => {
      es.close()
    },
    eventSource: es,
  }
}

export interface CreateWorkflowPayload {
  document_id: string
  template_id: string
  start_immediately?: boolean
}

export async function createWorkflow(
  payload: CreateWorkflowPayload
): Promise<WorkflowCreateData> {
  const res = await client.post<WorkflowCreateData>('/workflow-runs', {
    document_id: payload.document_id,
    template_id: payload.template_id,
    start_immediately: payload.start_immediately ?? true,
  })
  return res.data as WorkflowCreateData
}

export async function getWorkflowStatus(workflowRunId: string): Promise<WorkflowStatusData> {
  const res = await client.get<WorkflowStatusData>(`/workflow-runs/${workflowRunId}/status`)
  return res.data as WorkflowStatusData
}

export async function getWorkflow(workflowRunId: string): Promise<WorkflowStatusData> {
  const res = await client.get<WorkflowStatusData>(`/workflow-runs/${workflowRunId}`)
  return res.data as WorkflowStatusData
}
```

#### `frontend/src/App.tsx`

**Language hint:** `tsx`

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/layout/Navbar'
import { UploadPage } from './pages/UploadPage'
import { ProgressPage } from './pages/ProgressPage'
import { OutputPage } from './pages/OutputPage'
import { TemplatesPage } from './pages/TemplatesPage'
import { TemplatePreviewPage } from './pages/TemplatePreviewPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white">
        <Navbar />
        <Routes>
          <Route path="/"          element={<UploadPage />} />
          <Route path="/progress"  element={<ProgressPage />} />
          <Route path="/output"    element={<OutputPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/templates/:templateId/preview" element={<TemplatePreviewPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
```

#### `frontend/src/components/layout/Navbar.tsx`

**Language hint:** `tsx`

```tsx
import { useNavigate, useLocation } from 'react-router-dom'
import clsx from 'clsx'
import { useJobStore } from '../../store/useJobStore'

const navBtnFocus =
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ey-nav'

export function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { status, workflowRunByType, reset } = useJobStore()

  const hasWorkflowRuns = Object.values(workflowRunByType).some(Boolean)

  const jobSteps = [
    { label: 'Upload', path: '/' },
    { label: 'Generate', path: '/progress' },
    { label: 'Review', path: '/output' },
  ]

  const handleLogo = () => {
    reset()
    navigate('/')
  }

  const isTemplatesPage = location.pathname.startsWith('/templates')

  return (
    <nav
      className="bg-ey-nav text-white h-14 flex items-center px-6 sm:px-8 sticky top-0 z-50 gap-4 sm:gap-6 border-b border-white/10"
      aria-label="Primary"
    >
      <button
        type="button"
        onClick={handleLogo}
        className={clsx('flex items-center gap-3 group mr-auto shrink-0 min-w-0', navBtnFocus, 'rounded-sm')}
      >
        <img
          src="/brand/ey-logo.svg"
          alt="AI SDLC"
          width={132}
          height={28}
          className="h-7 w-auto block"
        />
        <span className="font-body font-semibold text-sm tracking-wide text-white/90 hidden lg:inline">
          Document Generator
        </span>
      </button>

      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        <button
          type="button"
          onClick={() => navigate('/templates')}
          className={clsx(
            navBtnFocus,
            'rounded-sm px-3 py-1.5 font-body text-[11px] font-semibold uppercase tracking-widest transition-colors border',
            isTemplatesPage
              ? 'text-ey-ink-strong bg-ey-primary border-ey-primary'
              : 'text-white/70 border-white/20 hover:text-white hover:border-white/40 bg-transparent'
          )}
        >
          Templates
        </button>

        <div className="hidden sm:block w-px h-6 bg-white/15 shrink-0" aria-hidden="true" />

        <div className="flex items-center gap-1 sm:gap-2 min-w-0 overflow-x-auto py-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
          {jobSteps.map((step, i) => {
            const active = location.pathname === step.path && !isTemplatesPage
            const isAccessible =
              step.path === '/' ||
              (step.path === '/progress' &&
                hasWorkflowRuns &&
                ['running', 'completed', 'failed'].includes(status)) ||
              (step.path === '/output' && status === 'completed')

            return (
              <button
                key={i}
                type="button"
                onClick={() => isAccessible && navigate(step.path)}
                disabled={!isAccessible}
                className={clsx(
                  navBtnFocus,
                  'shrink-0 rounded-sm px-2.5 sm:px-3 py-1.5 font-body text-[11px] sm:text-xs font-medium tracking-wide transition-colors',
                  active
                    ? 'text-ey-primary underline decoration-2 underline-offset-4'
                    : isAccessible
                      ? 'text-white/60 hover:text-white'
                      : 'text-white/25 cursor-not-allowed'
                )}
              >
                {step.label}
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
```

#### `frontend/src/components/output/CitationPanel.tsx`

**Language hint:** `tsx`

```tsx
import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { CitationDto } from '../../api/types'

function formatLine(c: CitationDto): string {
  const page = c.page == null ? '?' : String(c.page)
  const kind = c.content_type ?? 'text'
  return `${c.path}, p.${page} [${kind}]`
}

export function CitationPanel({ citations }: { citations: CitationDto[] }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="border-l border-ey-border bg-white shrink-0 w-72 flex flex-col max-h-full">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-5 py-4 border-b border-ey-border text-left w-full hover:bg-ey-surface/50 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ey-primary"
        aria-expanded={open}
      >
        {open ? <ChevronDown size={14} className="text-ey-muted shrink-0" /> : <ChevronRight size={14} className="text-ey-muted shrink-0" />}
        <div className="min-w-0">
          <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium">
            Citations
          </p>
          <p className="font-body text-xs text-ey-ink-strong mt-0.5">
            {citations.length} source{citations.length !== 1 ? 's' : ''}
          </p>
        </div>
      </button>
      {open && (
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {citations.length === 0 ? (
            <p className="font-body text-xs text-ey-muted">No citations for this section.</p>
          ) : (
            citations.map((c) => (
              <p
                key={c.chunk_id}
                className="font-body text-[11px] leading-snug text-ey-ink border-b border-ey-border/60 pb-3 last:border-0 last:pb-0"
              >
                {formatLine(c)}
              </p>
            ))
          )}
        </div>
      )}
    </div>
  )
}
```

#### `frontend/src/components/output/DocumentTabs.tsx`

**Language hint:** `tsx`

```tsx
import { useJobStore, type DocType } from '../../store/useJobStore'

export function DocumentTabs() {
  const {
    documents,
    activDoc,
    setActiveDoc,
    workflowDetailByType,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()

  if (!documents.length) return null

  const selectTab = (type: DocType) => {
    setActiveDoc(type)
    const w = workflowDetailByType[type]
    const first = w?.assembled_document?.sections?.[0]
    if (first) {
      setActiveSectionId(first.section_id)
      setSectionContent(first.content ?? '_No content for this section._')
    } else {
      setActiveSectionId(null)
      setSectionContent(null)
    }
  }

  return (
    <div
      role="tablist"
      aria-label="Generated document types"
      className="flex w-full items-stretch gap-0 border-b border-ey-border bg-ey-surface/60"
    >
      {documents.map(({ type }) => {
        const active = activDoc === type
        return (
          <button
            key={type}
            type="button"
            role="tab"
            aria-selected={active}
            id={`doc-tab-${type}`}
            onClick={() => selectTab(type as DocType)}
            className={`relative min-w-[5.5rem] flex-1 max-w-[12rem] px-4 py-3.5 text-center font-body text-sm font-semibold uppercase tracking-wide transition-colors border-b-[3px] -mb-px focus:outline-none focus-visible:z-10 focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-white ${
              active
                ? 'text-ey-ink-strong border-ey-primary bg-white'
                : 'text-ey-muted border-transparent hover:text-ey-ink hover:bg-white/80'
            }`}
          >
            {type}
          </button>
        )
      })}
    </div>
  )
}
```

#### `frontend/src/components/output/DocxViewer.tsx`

**Language hint:** `tsx`

```tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useJobStore } from '../../store/useJobStore'
import { FileText } from 'lucide-react'

function MarkdownPage({ content }: { content: string }) {
  return (
    <div className="bg-white w-full max-w-[820px] mx-auto shadow-[0_1px_4px_rgba(0,0,0,0.08)] px-16 py-14 mb-8">
      <div className="docx-prose">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </div>
  )
}

export function DocxViewer() {
  const { sectionContent, activeSectionId } = useJobStore()

  if (!activeSectionId) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-center px-8">
        <div className="w-14 h-14 bg-ey-surface flex items-center justify-center">
          <FileText size={24} className="text-ey-border" />
        </div>
        <p className="font-display font-bold text-xl uppercase text-ey-muted tracking-wide">
          Select a Section
        </p>
        <p className="font-body text-sm text-ey-muted max-w-xs">
          Choose a section from the left panel to view generated content.
        </p>
      </div>
    )
  }

  if (!sectionContent) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="font-body text-sm text-ey-muted">No content available.</p>
      </div>
    )
  }

  const pages = sectionContent.split('<!-- PAGE_BREAK -->')

  return (
    <div className="bg-ey-canvas flex-1 overflow-y-auto py-10 px-6 animate-fade-in">
      {pages.map((pageContent, i) => (
        <div key={i}>
          <MarkdownPage content={pageContent.trim()} />
          {i < pages.length - 1 && <hr className="page-break-divider my-2" />}
        </div>
      ))}
    </div>
  )
}
```

#### `frontend/src/components/output/DownloadPanel.tsx`

**Language hint:** `tsx`

```tsx
import { Download } from 'lucide-react'
import { useJobStore, type DocType } from '../../store/useJobStore'
import { outputApi } from '../../api/outputApi'

export function DownloadPanel() {
  const { documents, workflowDetailByType } = useJobStore()

  const hasAnyOutput = documents.some(
    (d) => workflowDetailByType[d.type as DocType]?.output_id
  )

  if (!documents.length) return null

  return (
    <div className="border-t border-ey-border bg-white px-6 py-4 flex items-center gap-4 flex-wrap">
      <span className="font-body text-xs font-medium tracking-widest uppercase text-ey-muted">
        Download
      </span>

      {documents.map(({ type }) => {
        const oid = workflowDetailByType[type as DocType]?.output_id
        const ready =
          (workflowDetailByType[type as DocType]?.status || '').toUpperCase() === 'COMPLETED' &&
          Boolean(oid)
        return (
          <button
            key={type}
            type="button"
            disabled={!ready}
            onClick={() => oid && outputApi.downloadByOutputId(oid)}
            className={`flex items-center gap-2 border px-4 py-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
              ready
                ? 'border-ey-border bg-white text-ey-ink-strong hover:border-ey-ink-strong'
                : 'border-ey-surface text-ey-muted cursor-not-allowed'
            }`}
          >
            <Download size={13} className={ready ? 'text-ey-muted' : 'text-ey-border'} />
            <span className="font-body text-xs font-medium">{type} (DOCX)</span>
          </button>
        )
      })}

      {!hasAnyOutput && (
        <span className="font-body text-xs text-ey-muted">
          Outputs appear when the workflow status is completed and an output_id is present.
        </span>
      )}
    </div>
  )
}
```

#### `frontend/src/components/output/SectionSidebar.tsx`

**Language hint:** `tsx`

```tsx
import { useJobStore } from '../../store/useJobStore'
import { ChevronRight } from 'lucide-react'

export function SectionSidebar() {
  const {
    activDoc,
    activeSectionId,
    documents,
    workflowDetailByType,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()

  const currentDoc = documents.find((d) => d.type === activDoc)
  const assembled = activDoc ? workflowDetailByType[activDoc]?.assembled_document : null

  const rows =
    assembled?.sections?.map((s) => ({ section_id: s.section_id, title: s.title })) ??
    currentDoc?.sections ??
    []

  const handleSelect = (sectionId: string) => {
    if (!activDoc || sectionId === activeSectionId) return
    setActiveSectionId(sectionId)
    const row = assembled?.sections?.find((s) => s.section_id === sectionId)
    const content = row?.content ?? null
    setSectionContent(content ?? '_No content for this section._')
  }

  if (rows.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="font-body text-xs text-ey-muted">No sections available.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col">
      <div className="px-5 py-4 border-b border-ey-border">
        <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium">
          Sections
        </p>
      </div>
      <div className="flex-1 overflow-y-auto">
        {rows.map((section, i) => {
          const active = activeSectionId === section.section_id
          return (
            <button
              key={section.section_id}
              type="button"
              onClick={() => handleSelect(section.section_id)}
              className={`w-full text-left px-5 py-3.5 flex items-center gap-3 border-b border-ey-border/60 transition-all group focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ey-primary ${
                active ? 'bg-ey-ink-strong text-white' : 'hover:bg-ey-surface text-ey-ink-strong'
              }`}
            >
              <span
                className={`font-body text-[10px] font-medium w-5 shrink-0 ${
                  active ? 'text-ey-primary' : 'text-ey-muted'
                }`}
              >
                {String(i + 1).padStart(2, '0')}
              </span>
              <span
                className={`font-body text-sm flex-1 leading-snug ${
                  active ? 'text-white font-medium' : 'text-ey-ink'
                }`}
              >
                {section.title}
              </span>
              <ChevronRight
                size={13}
                className={`shrink-0 transition-transform ${
                  active ? 'text-ey-primary' : 'text-ey-border group-hover:text-ey-ink-strong'
                }`}
              />
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

#### `frontend/src/components/progress/ProgressBar.tsx`

**Language hint:** `tsx`

```tsx
import { useJobStore } from '../../store/useJobStore'

const SEGMENTS = 12
const PAD = 1.35
const SLOT = 360 / SEGMENTS

function segmentPath(
  cx: number,
  cy: number,
  rOuter: number,
  rInner: number,
  index: number
): string {
  const startDeg = -90 + index * SLOT + PAD
  const endDeg = -90 + (index + 1) * SLOT - PAD
  const rad = (d: number) => (d * Math.PI) / 180
  const pt = (r: number, deg: number) => ({
    x: cx + r * Math.cos(rad(deg)),
    y: cy + r * Math.sin(rad(deg)),
  })
  const o1 = pt(rOuter, startDeg)
  const o2 = pt(rOuter, endDeg)
  const i2 = pt(rInner, endDeg)
  const i1 = pt(rInner, startDeg)
  const sweep = endDeg - startDeg
  const large = sweep > 180 ? 1 : 0
  return [
    `M ${o1.x} ${o1.y}`,
    `A ${rOuter} ${rOuter} 0 ${large} 1 ${o2.x} ${o2.y}`,
    `L ${i2.x} ${i2.y}`,
    `A ${rInner} ${rInner} 0 ${large} 0 ${i1.x} ${i1.y}`,
    'Z',
  ].join(' ')
}

export function ProgressBar() {
  const { progress, currentStep, status } = useJobStore()

  const isFailed = status === 'failed'
  const isComplete = status === 'completed'

  const filledCount = Math.min(
    SEGMENTS,
    Math.max(0, Math.round((progress / 100) * SEGMENTS))
  )

  const cx = 60
  const cy = 60
  const rOuter = 52
  const rInner = 38

  return (
    <div className="w-full animate-fade-in">
      <div className="flex justify-center py-2">
        <div className="relative w-44 h-44 sm:w-52 sm:h-52 shrink-0">
          <svg
            viewBox="0 0 120 120"
            className="h-full w-full"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
            aria-label={`Pipeline progress ${progress} percent`}
          >
            {Array.from({ length: SEGMENTS }, (_, i) => {
              const on = i < filledCount
              let fill: string
              if (isFailed) {
                fill = on ? '#EF4444' : '#E8E8E8'
              } else {
                fill = on ? '#FFE600' : '#E8E8E8'
              }
              return (
                <path
                  key={i}
                  d={segmentPath(cx, cy, rOuter, rInner, i)}
                  fill={fill}
                  className="transition-[fill] duration-500 ease-out"
                />
              )
            })}
          </svg>
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <span
              className={`font-display text-2xl sm:text-3xl font-bold tracking-tight tabular-nums ${
                isFailed ? 'text-red-500' : 'text-ey-ink-strong'
              }`}
            >
              {progress}
              <span className="text-ey-primary">%</span>
            </span>
          </div>
        </div>
      </div>

      <p className="font-body text-sm text-ey-muted text-center mt-4 max-w-xl mx-auto">
        {isFailed
          ? 'Generation failed'
          : isComplete
            ? 'All documents ready'
            : currentStep || 'Initialising pipeline…'}
      </p>
    </div>
  )
}
```

#### `frontend/src/components/templates/AddTemplatePanel.tsx`

**Language hint:** `tsx`

```tsx
import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import { Upload, X, FileText, Plus, Check } from 'lucide-react'
import { templateApi } from '../../api/templateApi'
import { getApiErrorMessage } from '../../api/errors'

const DOC_TYPES = ['PDD', 'SDD', 'UAT'] as const
type DocType = typeof DOC_TYPES[number]

interface Props {
  onSuccess: () => void
}

export function AddTemplatePanel({ onSuccess }: Props) {
  const [selectedType, setSelectedType] = useState<DocType | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase()
    if (ext !== 'docx') {
      setError('Only DOCX files are accepted for templates.')
      return
    }
    setError(null)
    setFile(f)
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const canSubmit = selectedType && file && !uploading

  const handleSubmit = async () => {
    if (!canSubmit) {
      if (!selectedType) setError('Select a document type first.')
      else if (!file) setError('Upload a DOCX template file.')
      return
    }
    setError(null)
    setUploading(true)
    try {
      await templateApi.uploadTemplate({
        file,
        template_type: selectedType,
      })
      setSuccess(true)
      setTimeout(() => {
        setSuccess(false)
        setFile(null)
        setSelectedType(null)
        onSuccess()
      }, 1500)
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Upload failed. Check backend logs.'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="border border-ey-border bg-white">
      <div className="flex items-center gap-3 px-6 py-4 border-b border-ey-border bg-ey-surface/80">
        <div className="w-6 h-6 bg-ey-ink-strong text-ey-primary flex items-center justify-center shrink-0">
          <Plus size={13} className="text-current" />
        </div>
        <h3 className="font-display font-bold text-lg uppercase tracking-wide text-ey-ink-strong">
          Add New Template
        </h3>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <label className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium block mb-3">
            Document Type
          </label>
          <div className="flex gap-3">
            {DOC_TYPES.map((type) => {
              const active = selectedType === type
              return (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSelectedType(type)}
                  className={`flex-1 py-3 border-2 font-display font-bold text-xl uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                    active
                      ? 'border-ey-ink-strong bg-ey-ink-strong text-ey-primary'
                      : 'border-ey-border bg-white text-ey-ink-strong hover:border-ey-ink-strong'
                  }`}
                >
                  {type}
                </button>
              )
            })}
          </div>
        </div>

        <div>
          <label className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium block mb-2">
            Template File (DOCX)
          </label>

          {file ? (
            <div className="border border-ey-border px-4 py-3 flex items-center gap-3 animate-fade-in">
              <FileText size={18} className="text-ey-muted shrink-0" />
              <span className="font-body text-sm text-ey-ink-strong flex-1 truncate">{file.name}</span>
              <span className="font-body text-xs text-ey-muted">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="shrink-0 hover:bg-ey-canvas p-1 transition-colors text-ey-muted hover:text-ey-ink-strong"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <div
              onDrop={onDrop}
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onClick={() => fileRef.current?.click()}
              className={`border-2 border-dashed cursor-pointer p-8 flex flex-col items-center gap-3 transition-all ${
                isDragging
                  ? 'border-ey-primary bg-ey-primary/10'
                  : 'border-ey-border bg-ey-surface hover:border-ey-ink-strong hover:bg-white'
              }`}
            >
              <Upload size={20} className={isDragging ? 'text-ey-ink-strong' : 'text-ey-muted'} />
              <p className="font-body text-sm text-ey-muted text-center">
                Drop DOCX here or <span className="text-ey-ink-strong font-medium underline">browse</span>
              </p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept=".docx"
            className="hidden"
            onChange={(e: ChangeEvent<HTMLInputElement>) => {
              const f = e.target.files?.[0]
              if (f) handleFile(f)
              e.target.value = ''
            }}
          />
        </div>

        {error && <p className="font-body text-xs text-red-500 animate-fade-in">{error}</p>}

        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-4">
            <Dot active={!!selectedType} label="Type" />
            <Dot active={!!file} label="File" />
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit || success}
            className={`flex items-center gap-2 px-6 py-3 font-display font-bold text-sm uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
              success
                ? 'bg-ey-primary text-ey-ink-strong'
                : canSubmit
                  ? 'bg-ey-ink-strong text-ey-primary hover:bg-ey-ink'
                  : 'bg-ey-canvas text-ey-muted cursor-not-allowed'
            }`}
          >
            {success ? (
              <>
                <Check size={14} strokeWidth={3} />
                Uploaded
              </>
            ) : uploading ? (
              'Uploading…'
            ) : (
              'Upload Template'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

function Dot({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div
        className={`w-1.5 h-1.5 rounded-full transition-colors ${active ? 'bg-ey-ink-strong' : 'bg-ey-border'}`}
      />
      <span
        className={`font-body text-xs transition-colors ${active ? 'text-ey-ink-strong font-medium' : 'text-ey-muted'}`}
      >
        {label}
      </span>
    </div>
  )
}
```

#### `frontend/src/components/templates/TemplateCard.tsx`

**Language hint:** `tsx`

```tsx
import { useState } from 'react'
import { Eye, Trash2, ChevronRight, AlertCircle } from 'lucide-react'
import { Template } from '../../store/useJobStore'
import { templateApi } from '../../api/templateApi'
import { TemplatePreviewModal } from './TemplatePreviewModal'

interface Props {
  template: Template
  onDeleted: () => void
}

export function TemplateCard({ template, onDeleted }: Props) {
  const [showPreview, setShowPreview] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await templateApi.deleteTemplate(template.id)
      onDeleted()
    } catch {
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  return (
    <>
      <div className="border border-ey-border bg-white hover:border-ey-ink-strong transition-all group animate-fade-in">
        <div className="h-1 bg-ey-primary" />

        <div className="p-5">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`font-body text-[9px] font-semibold tracking-widest uppercase px-2 py-0.5 ${
                    template.is_custom
                      ? 'bg-ey-ink-strong text-ey-primary'
                      : 'bg-ey-canvas text-ey-muted'
                  }`}
                >
                  {template.is_custom ? 'Custom' : 'Standard'}
                </span>
              </div>
              <h4 className="font-display font-bold text-lg uppercase tracking-wide text-ey-ink-strong leading-tight truncate">
                {template.filename}
              </h4>
              <p className="font-body text-[10px] text-ey-muted truncate">{template.template_id}</p>
            </div>
          </div>

          {template.description && (
            <p className="font-body text-xs text-ey-muted mb-4 leading-relaxed line-clamp-2">
              {template.description}
            </p>
          )}

          {template.sections_preview?.length > 0 && (
            <div className="space-y-1.5 mb-5">
              {template.sections_preview.slice(0, 4).map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <ChevronRight size={10} className="shrink-0 text-ey-border" />
                  <span className="font-body text-xs text-ey-muted truncate">{s}</span>
                </div>
              ))}
              {template.sections_preview.length > 4 && (
                <p className="font-body text-[10px] text-ey-muted pl-4">
                  +{template.sections_preview.length - 4} more sections
                </p>
              )}
            </div>
          )}

          {confirmDelete ? (
            <div className="border border-red-200 bg-red-50 p-3 animate-fade-in">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle size={13} color="#DC2626" />
                <p className="font-body text-xs text-red-600 font-medium">Delete this template?</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="flex-1 py-1.5 bg-red-600 text-white font-body text-xs font-medium hover:bg-red-700 transition-colors"
                >
                  {deleting ? 'Deleting…' : 'Yes, Delete'}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmDelete(false)}
                  className="flex-1 py-1.5 border border-ey-border text-ey-ink-strong font-body text-xs hover:border-ey-ink-strong transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowPreview(true)}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-ey-ink-strong text-white font-body text-xs font-medium hover:bg-ey-ink transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
              >
                <Eye size={13} className="group-hover:scale-110 transition-transform text-ey-primary" />
                Preview
              </button>
              {template.is_custom && (
                <button
                  type="button"
                  onClick={() => setConfirmDelete(true)}
                  className="w-10 flex items-center justify-center border border-ey-border text-ey-muted hover:border-red-300 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      {showPreview && (
        <TemplatePreviewModal
          template={template}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  )
}
```

#### `frontend/src/components/templates/TemplatePreviewModal.tsx`

**Language hint:** `tsx`

```tsx
import { useEffect, useState, useCallback, useRef } from 'react'
import { X, Loader2, AlertCircle, ChevronDown, ChevronRight, FileText } from 'lucide-react'
import { renderAsync } from 'docx-preview'
import { templateApi } from '../../api/templateApi'
import type { TemplateDto } from '../../api/types'
import { getApiErrorMessage } from '../../api/errors'
import { Template } from '../../store/useJobStore'

interface Props {
  template: Template
  onClose: () => void
}

export function TemplatePreviewModal({ template, onClose }: Props) {
  const [loadingMeta, setLoadingMeta] = useState(true)
  const [loadingDocx, setLoadingDocx] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dto, setDto] = useState<TemplateDto | null>(null)
  const [showMetadata, setShowMetadata] = useState(false)
  const docxContainerRef = useRef<HTMLDivElement | null>(null)

  const fetchPreview = useCallback(async () => {
    setLoadingMeta(true)
    setLoadingDocx(true)
    setError(null)
    try {
      const [data, binary] = await Promise.all([
        templateApi.getTemplateRaw(template.id),
        templateApi.getTemplateBinary(template.id),
      ])
      setDto(data)
      if (docxContainerRef.current) {
        docxContainerRef.current.innerHTML = ''
        await renderAsync(binary, docxContainerRef.current, undefined, {
          className: 'docx-preview-content',
          inWrapper: true,
          ignoreWidth: false,
          ignoreHeight: false,
        })
      }
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Could not load template preview.'))
      setDto(null)
    } finally {
      setLoadingMeta(false)
      setLoadingDocx(false)
    }
  }, [template.id])

  useEffect(() => {
    fetchPreview()
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [fetchPreview])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const titleType = dto?.template_type || template.type || template.id

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch bg-black/75"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="relative flex flex-col w-full max-w-6xl mx-auto my-6 bg-white shadow-2xl animate-slide-up">
        <div className="bg-ey-nav flex items-center gap-4 px-8 py-5 shrink-0">
          <div className="w-2 h-10 shrink-0 bg-ey-primary" />
          <div className="flex-1 min-w-0">
            <p className="font-body text-[10px] tracking-widest uppercase font-medium mb-0.5 text-ey-primary">
              Template preview
            </p>
            <h2 className="font-display font-bold text-2xl uppercase text-white tracking-tight leading-none truncate">
              {titleType} — {template.id}
            </h2>
          </div>
          <span
            className={`font-body text-[10px] font-semibold tracking-widest uppercase px-3 py-1 shrink-0 ${
              template.is_custom ? 'bg-ey-primary text-ey-ink-strong' : 'bg-white/10 text-white/70'
            }`}
          >
            {template.is_custom ? 'Custom' : 'Standard'}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors shrink-0 ml-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary rounded-sm"
          >
            <X size={18} />
          </button>
        </div>

        <div className="border-b border-ey-border bg-white px-8 py-3">
          <button
            type="button"
            onClick={() => setShowMetadata((v) => !v)}
            className="inline-flex items-center gap-2 font-body text-xs font-semibold tracking-widest uppercase text-ey-muted hover:text-ey-ink-strong"
          >
            {showMetadata ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            Metadata
          </button>
          {showMetadata && dto && (
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 font-body text-xs text-ey-muted">
              <p><span className="font-semibold text-ey-ink-strong">ID:</span> {dto.template_id}</p>
              <p><span className="font-semibold text-ey-ink-strong">Type:</span> {dto.template_type ?? '—'}</p>
              <p><span className="font-semibold text-ey-ink-strong">Version:</span> {dto.version ?? '—'}</p>
              <p><span className="font-semibold text-ey-ink-strong">Status:</span> {dto.status}</p>
              <p><span className="font-semibold text-ey-ink-strong">Created:</span> {dto.created_at}</p>
              <p><span className="font-semibold text-ey-ink-strong">Updated:</span> {dto.updated_at}</p>
              <p><span className="font-semibold text-ey-ink-strong">Compile job:</span> {dto.compile_job_id ?? '—'}</p>
              <p><span className="font-semibold text-ey-ink-strong">Artifacts:</span> {dto.compiled_artifacts?.length ?? 0}</p>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto bg-ey-canvas min-h-[420px]">
          {loadingMeta || loadingDocx ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[320px] gap-4">
              <Loader2 size={28} className="animate-spin text-ey-muted" />
              <p className="font-body text-sm text-ey-muted">Loading template DOCX…</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center min-h-[320px] gap-4 px-8 text-center">
              <AlertCircle size={28} color="#DC2626" />
              <p className="font-body text-sm text-red-600">{error}</p>
              <button type="button" onClick={fetchPreview} className="font-body text-xs underline text-ey-ink-strong">
                Retry
              </button>
            </div>
          ) : (
            <div className="py-10 px-6">
              <div className="bg-white w-full max-w-[980px] mx-auto shadow-[0_1px_4px_rgba(0,0,0,0.08)] px-8 py-8 animate-fade-in">
                <div className="flex items-center gap-2 mb-4 text-ey-muted">
                  <FileText size={14} />
                  <p className="font-body text-xs uppercase tracking-widest">Document view</p>
                </div>
                <div ref={docxContainerRef} className="docx-preview-host" />
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-ey-border bg-white px-8 py-4 flex items-center justify-between shrink-0">
          <p className="font-body text-xs text-ey-muted">
            Press <kbd className="font-mono bg-ey-canvas px-1.5 py-0.5 text-[10px]">Esc</kbd> to close
          </p>
          <button
            type="button"
            onClick={onClose}
            className="font-body text-xs font-medium px-6 py-2.5 bg-ey-ink-strong text-white hover:bg-ey-ink transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
```

#### `frontend/src/components/upload/DocumentSelector.tsx`

**Language hint:** `tsx`

```tsx
import { useJobStore, DocType } from '../../store/useJobStore'

const DOC_OPTIONS: { type: DocType; label: string; desc: string }[] = [
  { type: 'PDD', label: 'PDD', desc: 'Product Design Document' },
  { type: 'SDD', label: 'SDD', desc: 'System Design Document' },
  { type: 'UAT', label: 'UAT', desc: 'User Acceptance Testing' },
]

export function DocumentSelector() {
  const { selectedDocs, toggleDoc, setSelectedDocs } = useJobStore()

  const allSelected = selectedDocs.length === DOC_OPTIONS.length

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="font-body text-xs font-medium tracking-widest text-ey-muted uppercase">
          Documents to Generate
        </p>
        <button
          type="button"
          onClick={() =>
            allSelected
              ? setSelectedDocs([])
              : setSelectedDocs(DOC_OPTIONS.map((d) => d.type))
          }
          className="font-body text-xs text-ey-ink-strong underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary rounded-sm"
        >
          {allSelected ? 'Deselect all' : 'Select all'}
        </button>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {DOC_OPTIONS.map(({ type, label, desc }) => {
          const checked = selectedDocs.includes(type)
          return (
            <button
              key={type}
              type="button"
              onClick={() => toggleDoc(type)}
              className={`p-4 border-2 text-left transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                checked
                  ? 'border-ey-ink-strong bg-ey-ink-strong text-white'
                  : 'border-ey-border bg-white text-ey-ink-strong hover:border-ey-ink-strong'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span
                  className={`font-display font-bold text-2xl tracking-wide ${
                    checked ? 'text-ey-primary' : 'text-ey-ink-strong'
                  }`}
                >
                  {label}
                </span>
                <div
                  className={`w-5 h-5 border-2 flex items-center justify-center shrink-0 mt-1 transition-colors ${
                    checked ? 'border-ey-primary bg-ey-primary text-ey-ink-strong' : 'border-ey-border bg-white'
                  }`}
                >
                  {checked && (
                    <svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true">
                      <path
                        d="M1 4L3.5 6.5L9 1"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="square"
                      />
                    </svg>
                  )}
                </div>
              </div>
              <p className={`font-body text-xs ${checked ? 'text-white/70' : 'text-ey-muted'}`}>
                {desc}
              </p>
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

#### `frontend/src/components/upload/FileUploader.tsx`

**Language hint:** `tsx`

```tsx
import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import { Upload, File, X } from 'lucide-react'
import { useJobStore } from '../../store/useJobStore'

export function FileUploader() {
  const { uploadedFile, setUploadedFile } = useJobStore()
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext === 'pdf' || ext === 'docx') {
      setUploadedFile(file)
    } else {
      alert('Only PDF and DOCX files are supported.')
    }
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const onDragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const onDragLeave = () => setIsDragging(false)

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (uploadedFile) {
    return (
      <div className="border border-ey-border bg-white p-4 flex items-center gap-4 animate-fade-in">
        <div className="w-10 h-10 bg-ey-ink-strong text-ey-primary flex items-center justify-center shrink-0">
          <File size={18} className="text-current" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-body font-medium text-sm text-ey-ink-strong truncate">{uploadedFile.name}</p>
          <p className="font-body text-xs text-ey-muted mt-0.5">{formatSize(uploadedFile.size)}</p>
        </div>
        <button
          type="button"
          onClick={() => setUploadedFile(null)}
          className="w-8 h-8 flex items-center justify-center hover:bg-ey-surface transition-colors shrink-0 text-ey-muted hover:text-ey-ink-strong"
        >
          <X size={16} />
        </button>
      </div>
    )
  }

  return (
    <div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed transition-all cursor-pointer p-10 flex flex-col items-center gap-4
        ${isDragging
          ? 'border-ey-primary bg-ey-primary/10'
          : 'border-ey-border bg-ey-surface hover:border-ey-ink-strong hover:bg-white'
        }`}
    >
      <div
        className={`w-12 h-12 flex items-center justify-center transition-colors ${
          isDragging ? 'bg-ey-primary text-ey-ink-strong' : 'bg-ey-ink-strong text-ey-primary'
        }`}
      >
        <Upload size={22} className="text-current" />
      </div>
      <div className="text-center">
        <p className="font-display font-bold text-xl uppercase tracking-wide text-ey-ink-strong">
          Drop your BRD here
        </p>
        <p className="font-body text-sm text-ey-muted mt-1">
          or <span className="text-ey-ink-strong font-medium underline">browse files</span> — PDF or DOCX accepted
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        onChange={onChange}
        className="hidden"
      />
    </div>
  )
}
```

#### `frontend/src/components/upload/TemplateSelector.tsx`

**Language hint:** `tsx`

```tsx
import { useEffect, useState, useMemo } from 'react'
import { ChevronRight, Check, Eye } from 'lucide-react'
import { templateApi } from '../../api/templateApi'
import { useJobStore, type DocType, type Template } from '../../store/useJobStore'
import { TemplatePreviewModal } from '../templates/TemplatePreviewModal'

const DOC_ORDER: DocType[] = ['PDD', 'SDD', 'UAT']

function matchesType(tpl: Template, docType: DocType): boolean {
  const tt = (tpl.template_type || tpl.type || '').toUpperCase()
  return tt === docType
}

export function TemplateSelector() {
  const {
    selectedDocs,
    selectedTemplateByType,
    setSelectedTemplateForType,
  } = useJobStore()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null)

  const orderedSelected = useMemo(
    () => DOC_ORDER.filter((d) => selectedDocs.includes(d)),
    [selectedDocs]
  )

  const fetchTemplates = async () => {
    try {
      setLoading(true)
      const data = await templateApi.listTemplates()
      setTemplates(data)
    } catch {
      setError('Could not load templates. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTemplates()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        {orderedSelected.map((doc) => (
          <div key={doc} className="grid grid-cols-2 gap-4">
            {[1, 2].map((i) => (
              <div key={i} className="border border-ey-border p-5 animate-pulse">
                <div className="h-4 bg-ey-border w-16 mb-3" />
                <div className="h-3 bg-ey-border w-full mb-2" />
              </div>
            ))}
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="border border-ey-border p-6 text-center">
        <p className="font-body text-sm text-ey-muted">{error}</p>
        <button type="button" onClick={fetchTemplates} className="mt-3 font-body text-xs underline text-ey-ink-strong">
          Retry
        </button>
      </div>
    )
  }

  if (orderedSelected.length === 0) {
    return (
      <p className="font-body text-sm text-ey-muted">
        Select at least one output document type above to choose templates.
      </p>
    )
  }

  return (
    <div className="space-y-10">
      {orderedSelected.map((docType) => {
        const forType = templates.filter((t) => matchesType(t, docType))
        const selectedId = selectedTemplateByType[docType]

        return (
          <div key={docType}>
            <div className="flex items-center justify-between mb-4">
              <p className="font-body text-xs font-semibold tracking-widest uppercase text-ey-muted">
                {docType} template
              </p>
              {selectedId && (
                <button
                  type="button"
                  onClick={() => setSelectedTemplateForType(docType, null)}
                  className="font-body text-[11px] text-ey-muted underline hover:text-ey-ink-strong"
                >
                  Clear selection
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {forType.map((tpl) => {
                const selected = selectedId === tpl.id
                return (
                  <div
                    key={tpl.id}
                    onClick={() => setSelectedTemplateForType(docType, tpl.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        setSelectedTemplateForType(docType, tpl.id)
                      }
                    }}
                    className={`p-5 border-2 text-left transition-all relative group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                      selected
                        ? 'border-ey-ink-strong bg-ey-ink-strong text-white'
                        : 'border-ey-border bg-white hover:border-ey-ink-strong'
                    }`}
                  >
                    {selected && (
                      <div className="absolute top-3 right-3 w-5 h-5 bg-ey-primary text-ey-ink-strong flex items-center justify-center">
                        <Check size={11} strokeWidth={3} className="text-current" />
                      </div>
                    )}
                    <div
                      className={`inline-block px-2 py-0.5 mb-3 text-[10px] font-body font-semibold tracking-widest uppercase ${
                        tpl.is_custom
                          ? selected
                            ? 'bg-ey-primary text-ey-ink-strong'
                            : 'bg-ey-ink-strong text-ey-primary'
                          : selected
                            ? 'bg-white/20 text-white'
                            : 'bg-ey-surface text-ey-muted'
                      }`}
                    >
                      {tpl.is_custom ? 'Custom' : 'Standard'}
                    </div>
                    <p
                      className={`font-display font-bold text-lg tracking-wide uppercase mb-1 truncate ${
                        selected ? 'text-ey-primary' : 'text-ey-ink-strong'
                      }`}
                    >
                      {tpl.filename}
                    </p>
                    <p
                      className={`font-body text-xs mb-2 truncate ${
                        selected ? 'text-white/60' : 'text-ey-muted'
                      }`}
                    >
                      {tpl.template_id}
                    </p>
                    {tpl.sections_preview?.length > 0 && (
                      <div className="space-y-1">
                        {tpl.sections_preview.slice(0, 3).map((s, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <ChevronRight
                              size={10}
                              className={`shrink-0 ${selected ? 'text-ey-primary' : 'text-ey-muted'}`}
                            />
                            <span
                              className={`font-body text-xs truncate ${selected ? 'text-white/70' : 'text-ey-muted'}`}
                            >
                              {s}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="mt-4 pt-3 border-t border-black/10">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          setPreviewTemplate(tpl)
                        }}
                        className={`inline-flex items-center gap-1.5 font-body text-[11px] underline ${
                          selected ? 'text-white/80 hover:text-white' : 'text-ey-muted hover:text-ey-ink-strong'
                        }`}
                      >
                        <Eye size={12} />
                        Preview
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
            {forType.length === 0 && (
              <p className="font-body text-xs text-amber-700 mt-2">
                No {docType} templates in the library. Upload one from the Templates page, then return and select it here.
              </p>
            )}
          </div>
        )
      })}
      {previewTemplate && (
        <TemplatePreviewModal
          template={previewTemplate}
          onClose={() => setPreviewTemplate(null)}
        />
      )}
    </div>
  )
}
```

#### `frontend/src/index.css`

**Language hint:** `css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --ey-primary: #ffe600;
    --ey-primary-hover: #e6cf00;
    --ey-primary-rgb: 255, 230, 0;
    --ey-ink: #1a1a1a;
    --ey-ink-strong: #000000;
    --ey-muted: #6b6b6b;
    --ey-surface: #f7f7f7;
    --ey-border: #e5e5e5;
    --ey-nav: #000000;
    --ey-white: #ffffff;
    --ey-canvas: #f0f0f0;
    --font-sans: 'Inter', system-ui, sans-serif;
    /* Legacy aliases */
    --brand-black: var(--ey-ink-strong);
    --brand-yellow: var(--ey-primary);
    --brand-gray: var(--ey-surface);
    --brand-border: var(--ey-border);
    --brand-text: var(--ey-ink);
    --brand-muted: var(--ey-muted);
  }

  * {
    box-sizing: border-box;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    font-family: var(--font-sans);
    color: var(--ey-ink);
    background: var(--ey-white);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-sans);
    font-weight: 700;
    letter-spacing: -0.02em;
  }
}

/* ── DOCX Viewer Prose ─────────────────────────────────── */
.docx-prose {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.75;
  color: var(--ey-ink);
}

.docx-prose h1 {
  font-family: var(--font-sans);
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 3px solid var(--ey-primary);
  color: var(--ey-ink-strong);
}

.docx-prose h2 {
  font-family: var(--font-sans);
  font-size: 22px;
  font-weight: 700;
  margin: 28px 0 12px;
  color: var(--ey-ink-strong);
}

.docx-prose h3 {
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 600;
  margin: 20px 0 8px;
  color: var(--ey-ink-strong);
}

.docx-prose p {
  margin: 0 0 14px;
}

.docx-prose ul, .docx-prose ol {
  margin: 0 0 14px 20px;
}

.docx-prose li {
  margin-bottom: 4px;
}

.docx-prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 13px;
}

.docx-prose th {
  background: var(--ey-ink-strong);
  color: var(--ey-primary);
  font-family: var(--font-sans);
  font-weight: 600;
  padding: 10px 14px;
  text-align: left;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.docx-prose td {
  padding: 9px 14px;
  border-bottom: 1px solid var(--ey-border);
  vertical-align: top;
}

.docx-prose tr:last-child td {
  border-bottom: none;
}

.docx-prose tr:nth-child(even) td {
  background: var(--ey-surface);
}

.docx-prose img {
  max-width: 100%;
  margin: 16px auto;
  display: block;
}

.docx-prose code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 2px;
}

.docx-prose pre {
  background: var(--ey-ink);
  color: #e0e0e0;
  padding: 16px;
  overflow-x: auto;
  margin: 16px 0;
  font-size: 12px;
}

.docx-prose pre code {
  background: none;
  padding: 0;
  color: inherit;
}

.docx-prose strong {
  font-weight: 600;
}

.docx-prose blockquote {
  border-left: 3px solid var(--ey-primary);
  padding-left: 16px;
  margin: 16px 0;
  color: #555;
  font-style: italic;
}

/* ── Page divider ─────────────────────────────────── */
.page-break-divider {
  border: none;
  border-top: 1px dashed #d0d0d0;
  margin: 48px 0;
  position: relative;
}
.page-break-divider::before {
  content: 'PAGE BREAK';
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--ey-surface);
  font-size: 10px;
  color: #999;
  font-family: var(--font-sans);
  letter-spacing: 0.1em;
  padding: 0 8px;
}

/* ── Scrollbar ─────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d0d0d0; }
::-webkit-scrollbar-thumb:hover { background: #999; }

/* ── Drag state ─────────────────────────────────── */
.drop-active {
  border-color: var(--ey-primary) !important;
  background: rgba(var(--ey-primary-rgb), 0.08) !important;
}

/* ── Template DOCX popup preview ───────────────────────── */
.docx-preview-host .docx-wrapper {
  background: #f0f0f0 !important;
  padding: 12px 0 !important;
}

.docx-preview-host .docx {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  margin-bottom: 12px !important;
}
```

#### `frontend/src/main.tsx`

**Language hint:** `tsx`

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

#### `frontend/src/pages/OutputPage.tsx`

**Language hint:** `tsx`

```tsx
import { useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { DocumentTabs } from '../components/output/DocumentTabs'
import { SectionSidebar } from '../components/output/SectionSidebar'
import { DocxViewer } from '../components/output/DocxViewer'
import { DownloadPanel } from '../components/output/DownloadPanel'
import { CitationPanel } from '../components/output/CitationPanel'
import { useJobStore, type DocType } from '../store/useJobStore'
import { getWorkflow } from '../api/workflowApi'
import type { CitationDto } from '../api/types'

export function OutputPage() {
  const navigate = useNavigate()
  const {
    selectedDocs,
    workflowRunByType,
    documents,
    activDoc,
    activeSectionId,
    workflowDetailByType,
    setDocuments,
    setWorkflowDetail,
    setActiveDoc,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()

  const citationRows = useMemo((): CitationDto[] => {
    if (!activDoc || !activeSectionId) return []
    const bundle = workflowDetailByType[activDoc]?.section_retrieval_results?.[activeSectionId]
    return bundle?.citations ?? []
  }, [activDoc, activeSectionId, workflowDetailByType])

  useEffect(() => {
    const hasRuns = selectedDocs.some((d) => workflowRunByType[d])
    if (!hasRuns) {
      navigate('/')
      return
    }

    let cancelled = false
    ;(async () => {
      const docs: { type: DocType; sections: { section_id: string; title: string }[] }[] = []
      for (const doc of selectedDocs) {
        const runId = workflowRunByType[doc]
        if (!runId) continue
        const w = await getWorkflow(runId)
        if (cancelled) return
        setWorkflowDetail(doc, w)
        docs.push({
          type: doc,
          sections:
            w.assembled_document?.sections?.map((s) => ({
              section_id: s.section_id,
              title: s.title,
            })) ?? [],
        })
      }
      if (cancelled) return
      setDocuments(docs)
      if (docs.length > 0) {
        const firstType = docs[0].type
        setActiveDoc(firstType)
        const wf = useJobStore.getState().workflowDetailByType[firstType]
        const sec = wf?.assembled_document?.sections?.[0]
        if (sec) {
          setActiveSectionId(sec.section_id)
          setSectionContent(sec.content ?? '_No content for this section._')
        }
      }
    })().catch(() => {})

    return () => {
      cancelled = true
    }
  }, [
    navigate,
    selectedDocs,
    workflowRunByType,
    setDocuments,
    setWorkflowDetail,
    setActiveDoc,
    setActiveSectionId,
    setSectionContent,
  ])

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col bg-white">
      <div className="flex items-center justify-between px-8 py-5 border-b border-ey-border bg-white shrink-0">
        <div className="flex items-center gap-4 min-w-0">
          <img
            src="/brand/ey-logo.svg"
            alt="AI SDLC"
            className="h-8 w-auto shrink-0 hidden sm:block opacity-90"
            width={132}
            height={28}
          />
          <div className="min-w-0">
            <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium mb-1">
              Generated Output
            </p>
            <h1 className="font-display font-bold text-2xl uppercase text-ey-ink-strong tracking-tight leading-none">
              Document Review
            </h1>
          </div>
        </div>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="flex items-center gap-2 border border-ey-border px-4 py-2.5 hover:border-ey-ink-strong transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
        >
          <Plus size={14} className="group-hover:rotate-90 transition-transform text-ey-ink" />
          <span className="font-body text-xs font-medium text-ey-ink-strong">New Job</span>
        </button>
      </div>

      {documents.length > 0 && (
        <div className="px-8 bg-white shrink-0">
          <DocumentTabs />
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <div className="w-56 shrink-0 border-r border-ey-border overflow-y-auto bg-white">
          <SectionSidebar />
        </div>

        <div className="flex-1 flex min-w-0 overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            <DocxViewer />
          </div>
          <CitationPanel citations={citationRows} />
        </div>
      </div>

      <DownloadPanel />
    </div>
  )
}
```

#### `frontend/src/pages/ProgressPage.tsx`

**Language hint:** `tsx`

```tsx
import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, RefreshCw, AlertCircle } from 'lucide-react'
import { ProgressBar } from '../components/progress/ProgressBar'
import { useJobStore, type DocType } from '../store/useJobStore'
import { getWorkflowStatus, getWorkflow, subscribeToWorkflowEvents } from '../api/workflowApi'

const POLL_DEBOUNCE_MS = 320
/** If every SSE connection is still CLOSED after this delay following an error, use polling only. */
const SSE_ALL_CLOSED_CHECK_MS = 2000
/** While SSE is primary, full poll occasionally so quiet workflows stay fresh. */
const SSE_SAFETY_POLL_MS = 30_000

type WorkflowRunStatus = Awaited<ReturnType<typeof getWorkflowStatus>>

function docTypeForWorkflowRunId(
  runs: Partial<Record<DocType, string>>,
  workflowRunId: string
): DocType | undefined {
  return (['PDD', 'SDD', 'UAT'] as const).find((d) => runs[d] === workflowRunId)
}

function backendStatusUi(s: string | undefined): 'running' | 'completed' | 'failed' {
  const u = (s || '').toUpperCase()
  if (u === 'FAILED') return 'failed'
  if (u === 'COMPLETED') return 'completed'
  return 'running'
}

export function ProgressPage() {
  const navigate = useNavigate()
  const {
    selectedDocs,
    workflowRunByType,
    status,
    progress,
    currentStep,
    errorMessage,
    perTypeProgress,
    perTypeStep,
    setProgress,
    setStatus,
    setPerTypeProgress,
    setDocuments,
    setActiveDoc,
    setError,
    setWorkflowDetail,
    documents,
  } = useJobStore()

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const statusByDocRef = useRef<Partial<Record<DocType, WorkflowRunStatus>>>({})
  const pollRef = useRef<() => Promise<void>>(async () => {})

  const loadCompletedOutputs = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs, setWorkflowDetail, setDocuments, setActiveDoc } =
      useJobStore.getState()
    const out: { type: DocType; sections: { section_id: string; title: string }[] }[] = []
    for (const doc of docs) {
      const runId = runs[doc]
      if (!runId) continue
      const w = await getWorkflow(runId)
      setWorkflowDetail(doc, w)
      out.push({
        type: doc,
        sections:
          w.assembled_document?.sections?.map((s) => ({
            section_id: s.section_id,
            title: s.title,
          })) ?? [],
      })
    }
    setDocuments(out)
    if (out.length > 0) setActiveDoc(out[0].type)
  }, [])

  const reconcileFromSnapshot = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    if (docs.length === 0) return

    const snap = statusByDocRef.current
    const denom = docs.filter((d) => runs[d]).length
    let snapshotIncomplete = false
    let sumProgress = 0
    const stepParts: string[] = []
    let anyFailed = false

    for (const doc of docs) {
      if (!runs[doc]) continue
      const st = snap[doc]
      if (!st) {
        snapshotIncomplete = true
        sumProgress += 0
        stepParts.push(`${doc}: …`)
        setPerTypeProgress(doc, 0, 'Waiting for status…')
        continue
      }

      const p = st.overall_progress_percent ?? 0
      sumProgress += p
      const label = st.current_step_label || st.current_phase || '…'
      stepParts.push(`${doc}: ${label}`)
      setPerTypeProgress(doc, p, label)

      if (backendStatusUi(st.status) === 'failed') anyFailed = true
    }

    const avgProgress = denom > 0 ? Math.round(sumProgress / denom) : 0

    setProgress(avgProgress, stepParts.join(' · '))

    if (anyFailed) {
      const failedDoc = docs.find((doc) => {
        const st = snap[doc]
        return st && backendStatusUi(st.status) === 'failed'
      })
      setError(
        failedDoc
          ? `Pipeline failed (${failedDoc}). Check backend logs.`
          : 'Pipeline failed. Check backend logs.'
      )
      setStatus('failed')
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = null
      return
    }

    const allCompleted =
      docs.length > 0 &&
      docs.every((d) => {
        const st = snap[d]
        return runs[d] && st && backendStatusUi(st.status) === 'completed'
      })

    if (allCompleted && docs.every((d) => runs[d])) {
      setStatus('completed')
      try {
        await loadCompletedOutputs()
      } catch {
        /* ignore */
      }
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = null
      return
    }

    setStatus('running')

    if (snapshotIncomplete) {
      void pollRef.current()
    }
  }, [setProgress, setPerTypeProgress, setStatus, setError, loadCompletedOutputs])

  const poll = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    if (docs.length === 0) return
    try {
      const results = await Promise.all(
        docs.map(async (doc) => {
          const id = runs[doc]
          if (!id) return { doc, st: null as WorkflowRunStatus | null }
          const st = await getWorkflowStatus(id)
          return { doc, st }
        })
      )

      for (const { doc, st } of results) {
        if (st) statusByDocRef.current[doc] = st
      }

      await reconcileFromSnapshot()
    } catch {
      // network hiccup
    }
  }, [reconcileFromSnapshot])

  pollRef.current = poll

  const refreshSingleRun = useCallback(
    async (workflowRunId: string) => {
      const { workflowRunByType: runs } = useJobStore.getState()
      const doc = docTypeForWorkflowRunId(runs, workflowRunId)
      if (!doc) return
      try {
        const st = await getWorkflowStatus(workflowRunId)
        statusByDocRef.current[doc] = st
        await reconcileFromSnapshot()
      } catch {
        void poll()
      }
    },
    [reconcileFromSnapshot, poll]
  )

  const startPolling = useCallback(() => {
    void poll()
    intervalRef.current = setInterval(() => {
      void poll()
    }, 2500)
  }, [poll])

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  useEffect(() => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    const hasRuns = docs.length > 0 && docs.every((d) => runs[d])
    if (!hasRuns) {
      navigate('/')
      return
    }
    if (status !== 'running') {
      return () => {}
    }

    let cancelled = false
    const closeSubscriptions: Array<() => void> = []
    const eventSources: EventSource[] = []
    const debounceByRunId: Record<string, ReturnType<typeof setTimeout>> = {}
    let fallbackCheckTimer: ReturnType<typeof setTimeout> | null = null
    let safetyPollTimer: ReturnType<typeof setInterval> | null = null

    const clearRunDebounces = () => {
      for (const t of Object.values(debounceByRunId)) clearTimeout(t)
      for (const k of Object.keys(debounceByRunId)) delete debounceByRunId[k]
    }

    const scheduleDebouncedRefresh = (runId: string) => {
      const existing = debounceByRunId[runId]
      if (existing) clearTimeout(existing)
      debounceByRunId[runId] = setTimeout(() => {
        delete debounceByRunId[runId]
        if (!cancelled) void refreshSingleRun(runId)
      }, POLL_DEBOUNCE_MS)
    }

    const scheduleFallbackIfAllStreamsDead = () => {
      if (fallbackCheckTimer) clearTimeout(fallbackCheckTimer)
      fallbackCheckTimer = setTimeout(() => {
        fallbackCheckTimer = null
        if (cancelled || eventSources.length === 0) return
        const allClosed = eventSources.every((es) => es.readyState === EventSource.CLOSED)
        if (allClosed && !intervalRef.current) {
          clearRunDebounces()
          closeSubscriptions.forEach((c) => c())
          closeSubscriptions.length = 0
          eventSources.length = 0
          if (safetyPollTimer) {
            clearInterval(safetyPollTimer)
            safetyPollTimer = null
          }
          startPolling()
        }
      }, SSE_ALL_CLOSED_CHECK_MS)
    }

    const setup = async () => {
      await poll()
      if (cancelled) return

      for (const doc of docs) {
        const runId = runs[doc]
        if (!runId) continue
        const { close, eventSource } = subscribeToWorkflowEvents(runId, {
          onOpen: () => {
            // Defer: this handler can run before `eventSources.push(eventSource)` in this loop iteration.
            window.setTimeout(() => {
              if (
                cancelled ||
                !fallbackCheckTimer ||
                eventSources.length === 0 ||
                !eventSources.every((es) => es.readyState === EventSource.OPEN)
              ) {
                return
              }
              clearTimeout(fallbackCheckTimer)
              fallbackCheckTimer = null
            }, 0)
          },
          onEvent: (ev) => {
            const wid = typeof ev.workflow_run_id === 'string' ? ev.workflow_run_id : runId
            if (ev.type === 'workflow.failed' || ev.type === 'workflow.completed') {
              void refreshSingleRun(wid)
              return
            }
            scheduleDebouncedRefresh(wid)
          },
          onError: () => {
            scheduleFallbackIfAllStreamsDead()
          },
        })
        closeSubscriptions.push(close)
        eventSources.push(eventSource)
      }

      safetyPollTimer = setInterval(() => {
        if (!cancelled && !intervalRef.current) void poll()
      }, SSE_SAFETY_POLL_MS)
    }

    void setup()

    return () => {
      cancelled = true
      if (fallbackCheckTimer) clearTimeout(fallbackCheckTimer)
      if (safetyPollTimer) clearInterval(safetyPollTimer)
      clearRunDebounces()
      closeSubscriptions.forEach((c) => c())
      stopPolling()
    }
  }, [navigate, status, startPolling, poll, refreshSingleRun])

  useEffect(() => {
    if (status === 'completed' && documents.length === 0) {
      void loadCompletedOutputs().catch(() => {})
    }
  }, [status, documents.length, loadCompletedOutputs])

  const handleViewOutput = () => navigate('/output')

  const docLabels = selectedDocs.length ? selectedDocs : (['PDD', 'SDD', 'UAT'] as DocType[])

  return (
    <div className="min-h-[calc(100vh-56px)] bg-white flex flex-col">
      <div className="bg-ey-nav px-8 py-10">
        <div className="max-w-3xl mx-auto">
          <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-2 font-medium">
            Pipeline Running
          </p>
          <h1 className="font-display font-bold text-4xl uppercase text-white tracking-tight">
            Generating Documents
          </h1>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center px-8">
        <div className="w-full max-w-3xl py-20">
          {status === 'failed' ? (
            <div className="animate-fade-in">
              <div className="flex items-start gap-4 border border-red-200 bg-red-50 p-6 mb-8">
                <AlertCircle size={20} color="#DC2626" className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-body font-semibold text-red-700 text-sm mb-1">
                    Generation Failed
                  </p>
                  <p className="font-body text-sm text-red-600">
                    {errorMessage ?? 'An unexpected error occurred. Please check your backend.'}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => navigate('/')}
                className="flex items-center gap-3 px-8 py-4 bg-ey-ink-strong text-ey-primary font-display font-bold uppercase tracking-widest hover:bg-ey-ink transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
              >
                <RefreshCw size={16} className="shrink-0" />
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-6 mb-12 animate-fade-in">
                {docLabels.map((doc) => {
                  const done = status === 'completed'
                  const tp = perTypeProgress[doc]
                  return (
                    <div key={doc} className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full transition-colors duration-500 ${
                          done ? 'bg-ey-primary' : 'bg-ey-border animate-pulse'
                        }`}
                      />
                      <span className="font-display font-bold text-lg uppercase text-ey-ink-strong tracking-wide">
                        {doc}
                      </span>
                      {tp !== undefined && status === 'running' && (
                        <span className="font-body text-xs text-ey-muted">{tp}%</span>
                      )}
                    </div>
                  )
                })}
              </div>

              <ProgressBar />

              {status === 'running' && (
                <div className="mt-4 space-y-1 font-body text-xs text-ey-muted max-h-24 overflow-y-auto">
                  {selectedDocs.map((doc) =>
                    perTypeStep[doc] ? (
                      <p key={doc}>
                        <span className="font-semibold text-ey-ink-strong">{doc}:</span> {perTypeStep[doc]}
                      </p>
                    ) : null
                  )}
                </div>
              )}

              {status === 'running' && progress < 100 && (
                <p className="font-body text-xs text-ey-muted mt-6 animate-fade-in">
                  {currentStep || 'This may take a few minutes depending on document length.'}
                </p>
              )}

              {status === 'completed' && (
                <div className="mt-12 animate-slide-up">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-6 h-6 bg-ey-primary text-ey-ink-strong flex items-center justify-center">
                      <svg width="12" height="10" viewBox="0 0 12 10" fill="none" aria-hidden="true">
                        <path
                          d="M1 5L4.5 8.5L11 1"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="square"
                        />
                      </svg>
                    </div>
                    <span className="font-display font-bold text-xl uppercase tracking-wide text-ey-ink-strong">
                      {documents.length} Document{documents.length !== 1 ? 's' : ''} Ready
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleViewOutput}
                    className="group flex items-center gap-4 px-10 py-5 bg-ey-ink-strong text-ey-primary font-display font-bold text-xl uppercase tracking-widest hover:bg-ey-primary hover:text-ey-ink-strong transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
                  >
                    View &amp; Download
                    <ArrowRight size={20} className="transition-transform group-hover:translate-x-1 text-current" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
```

#### `frontend/src/pages/TemplatePreviewPage.tsx`

**Language hint:** `tsx`

```tsx
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ArrowLeft, AlertCircle, Loader2 } from 'lucide-react'
import { templateApi } from '../api/templateApi'
import type { TemplateDto } from '../api/types'
import { getApiErrorMessage } from '../api/errors'

function formatArtifactLine(a: unknown, i: number): string {
  if (a !== null && typeof a === 'object' && 'name' in a && typeof (a as { name: string }).name === 'string') {
    return `- ${(a as { name: string }).name}`
  }
  try {
    return `- \`${JSON.stringify(a)}\``
  } catch {
    return `- (artifact ${i + 1})`
  }
}

function buildMetadataMarkdown(dto: TemplateDto): string {
  const lines: string[] = []
  lines.push(`# ${dto.filename}`)
  lines.push('')
  lines.push('Metadata from the template registry (`GET /templates/{id}`). Section structure is determined when you run a workflow, not from this preview.')
  lines.push('')
  lines.push('## Details')
  lines.push('')
  lines.push('| Field | Value |')
  lines.push('| --- | --- |')
  lines.push(`| template_id | \`${dto.template_id}\` |`)
  lines.push(`| template_type | ${dto.template_type ?? '—'} |`)
  lines.push(`| version | ${dto.version ?? '—'} |`)
  lines.push(`| status | **${dto.status}** |`)
  lines.push(`| compile_job_id | ${dto.compile_job_id ?? '—'} |`)
  lines.push(`| created_at | ${dto.created_at} |`)
  lines.push(`| updated_at | ${dto.updated_at} |`)
  lines.push('')
  lines.push('## Compiled artifacts')
  lines.push('')
  const arts = dto.compiled_artifacts ?? []
  if (arts.length === 0) {
    lines.push('_None stored on this template record._')
  } else {
    lines.push(`_Count: ${arts.length}_`)
    lines.push('')
    arts.forEach((a, i) => lines.push(formatArtifactLine(a, i)))
  }
  return lines.join('\n')
}

export function TemplatePreviewPage() {
  const navigate = useNavigate()
  const { templateId } = useParams<{ templateId: string }>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dto, setDto] = useState<TemplateDto | null>(null)

  const fetchTemplate = useCallback(async () => {
    if (!templateId) {
      setError('Template ID is missing.')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await templateApi.getTemplateRaw(templateId)
      setDto(data)
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Could not load template preview.'))
      setDto(null)
    } finally {
      setLoading(false)
    }
  }, [templateId])

  useEffect(() => {
    fetchTemplate()
  }, [fetchTemplate])

  return (
    <div className="min-h-[calc(100vh-56px)] bg-ey-canvas">
      <div className="bg-ey-nav text-white px-8 py-8">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-1 h-10 bg-ey-primary shrink-0" />
            <div className="min-w-0">
              <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-1 font-medium">
                Template preview
              </p>
              <h1 className="font-display font-bold text-2xl uppercase tracking-tight truncate text-white">
                {dto?.template_type ?? 'Template'} — {templateId}
              </h1>
            </div>
          </div>
          <button
            type="button"
            onClick={() => navigate('/templates')}
            className="flex items-center gap-2 px-4 py-2 border border-white/20 text-white/80 hover:text-white hover:border-white/40 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ey-nav"
          >
            <ArrowLeft size={14} />
            Back to Library
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[320px] gap-4">
            <Loader2 size={28} className="animate-spin text-ey-muted" />
            <p className="font-body text-sm text-ey-muted">Loading template…</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center min-h-[320px] gap-4 px-8 text-center">
            <AlertCircle size={28} color="#DC2626" />
            <p className="font-body text-sm text-red-600">{error}</p>
            <button type="button" onClick={fetchTemplate} className="font-body text-xs underline text-ey-ink-strong">
              Retry
            </button>
          </div>
        ) : dto ? (
          <div className="bg-white w-full shadow-[0_1px_4px_rgba(0,0,0,0.08)] px-12 py-12">
            <div className="docx-prose">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{buildMetadataMarkdown(dto)}</ReactMarkdown>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
```

#### `frontend/src/pages/TemplatesPage.tsx`

**Language hint:** `tsx`

```tsx
import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, LayoutTemplate } from 'lucide-react'
import { templateApi } from '../api/templateApi'
import { Template } from '../store/useJobStore'
import { TemplateCard } from '../components/templates/TemplateCard'
import { AddTemplatePanel } from '../components/templates/AddTemplatePanel'

const DOC_TYPES = ['PDD', 'SDD', 'UAT'] as const
type DocType = typeof DOC_TYPES[number]

const TYPE_LABELS: Record<DocType, string> = {
  PDD: 'Product Design Document',
  SDD: 'System Design Document',
  UAT: 'User Acceptance Testing',
}

export function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await templateApi.listTemplates()
      setTemplates(data)
    } catch {
      setError('Could not load templates. Is the backend running (see VITE_API_BASE / Vite proxy)?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchTemplates() }, [fetchTemplates])

  const byType = (type: DocType) =>
    templates.filter(
      (t) => ((t.template_type || t.type) ?? '').toUpperCase() === type
    )

  return (
    <div className="min-h-[calc(100vh-56px)] bg-white">

      {/* ── Hero strip ── */}
      <div className="bg-ey-nav text-white px-8 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-start gap-4">
            <div className="w-1 h-12 bg-ey-primary shrink-0" />
            <div>
              <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-1 font-medium">
                AI SDLC Platform
              </p>
              <h1 className="font-display font-bold text-5xl uppercase leading-none tracking-tight text-white">
                Template<br />Library
              </h1>
            </div>
          </div>
          <p className="font-body text-sm text-white/50 max-w-lg leading-relaxed mt-6">
            Manage standard and custom document templates. Each template defines the structure
            and sections that the generation engine will produce.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-12 space-y-14">

        {/* ── Add Template ── */}
        <section className="animate-slide-up">
          <SectionHeader label="Add New Template" number="01" />
          <AddTemplatePanel onSuccess={fetchTemplates} />
        </section>

        {/* ── Three type lists ── */}
        <section className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-between mb-8">
            <SectionHeader label="Existing Templates" number="02" />
            <button
              type="button"
              onClick={fetchTemplates}
              disabled={loading}
              className="flex items-center gap-2 border border-ey-border px-4 py-2 font-body text-xs text-ey-ink hover:border-ey-ink-strong transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
            >
              <RefreshCw
                size={12}
                className={`transition-transform ${loading ? 'animate-spin' : 'group-hover:rotate-180'}`}
              />
              Refresh
            </button>
          </div>

          {error && (
            <div className="border border-red-200 bg-red-50 px-5 py-4 mb-8 flex items-center gap-3 animate-fade-in">
              <span className="font-body text-sm text-red-600">{error}</span>
              <button onClick={fetchTemplates} className="ml-auto font-body text-xs underline text-red-600">
                Retry
              </button>
            </div>
          )}

          {/* Three columns — one per doc type */}
          <div className="grid grid-cols-3 gap-8">
            {DOC_TYPES.map((type) => {
              const list = byType(type)
              return (
                <div key={type}>
                  {/* Column header */}
                  <div className="flex items-center gap-3 mb-4 pb-3 border-b-2 border-ey-ink-strong">
                    <div className="w-7 h-7 bg-ey-primary text-ey-ink-strong flex items-center justify-center shrink-0">
                      <LayoutTemplate size={13} className="text-current" />
                    </div>
                    <div>
                      <p className="font-display font-bold text-2xl uppercase tracking-wide text-ey-ink-strong leading-none">
                        {type}
                      </p>
                      <p className="font-body text-[10px] text-ey-muted mt-0.5">
                        {TYPE_LABELS[type]}
                      </p>
                    </div>
                    <span className="ml-auto font-display font-bold text-2xl text-ey-border">
                      {loading ? '—' : list.length}
                    </span>
                  </div>

                  {/* Template cards */}
                  <div className="space-y-4">
                    {loading ? (
                      <>
                        <SkeletonCard />
                        <SkeletonCard />
                      </>
                    ) : list.length === 0 ? (
                      <EmptyState type={type} />
                    ) : (
                      list.map((tpl) => (
                        <TemplateCard
                          key={tpl.id}
                          template={tpl}
                          onDeleted={fetchTemplates}
                        />
                      ))
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </section>

      </div>
    </div>
  )
}

/* ── Sub-components ────────────────────────────────────── */

function SectionHeader({ number, label }: { number: string; label: string }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <span className="font-display font-bold text-3xl text-ey-primary leading-none">{number}</span>
      <div className="h-px flex-1 bg-ey-border" />
      <span className="font-body text-xs font-semibold tracking-widest uppercase text-ey-muted">
        {label}
      </span>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="border border-ey-border p-5 animate-pulse">
      <div className="h-3 bg-ey-border w-16 mb-3 rounded" />
      <div className="h-5 bg-ey-border w-3/4 mb-2 rounded" />
      <div className="h-3 bg-ey-border w-full mb-1 rounded" />
      <div className="h-3 bg-ey-border w-2/3 mb-4 rounded" />
      <div className="h-8 bg-ey-border w-full rounded" />
    </div>
  )
}

function EmptyState({ type }: { type: string }) {
  return (
    <div className="border-2 border-dashed border-ey-border p-8 text-center">
      <p className="font-display font-bold text-lg uppercase text-ey-border tracking-wide mb-1">
        No {type} Templates
      </p>
      <p className="font-body text-xs text-ey-muted">
        Upload a custom template above to get started.
      </p>
    </div>
  )
}
```

#### `frontend/src/pages/UploadPage.tsx`

**Language hint:** `tsx`

```tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, AlertCircle } from 'lucide-react'
import { FileUploader } from '../components/upload/FileUploader'
import { DocumentSelector } from '../components/upload/DocumentSelector'
import { TemplateSelector } from '../components/upload/TemplateSelector'
import { useJobStore, type DocType } from '../store/useJobStore'
import { uploadDocument } from '../api/documentApi'
import { createWorkflow } from '../api/workflowApi'
import { getApiErrorMessage } from '../api/errors'

export function UploadPage() {
  const navigate = useNavigate()
  const {
    uploadedFile,
    selectedDocs,
    selectedTemplateByType,
    setDocumentId,
    setWorkflowRuns,
    setStatus,
    setError,
  } = useJobStore()

  const [submitting, setSubmitting] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  const templatesReady = selectedDocs.every(
    (d) => Boolean(selectedTemplateByType[d])
  )
  const canSubmit = Boolean(uploadedFile) && selectedDocs.length > 0 && templatesReady

  const handleGenerate = async () => {
    if (!uploadedFile) {
      setValidationError('Please upload a BRD or DOCX file.')
      return
    }
    if (selectedDocs.length === 0) {
      setValidationError('Select at least one document type.')
      return
    }
    const missing = selectedDocs.filter((d) => !selectedTemplateByType[d])
    if (missing.length > 0) {
      setValidationError(
        `Select a template for each output type (missing: ${missing.join(', ')}).`
      )
      return
    }
    setValidationError(null)

    const runs: Partial<Record<DocType, string>> = {}

    try {
      setSubmitting(true)
      setError(null)

      const docRes = await uploadDocument(uploadedFile)
      const document_id = docRes.document_id
      setDocumentId(document_id)

      // Serialize workflow creation to reduce concurrent ingestion on the same document_id.
      for (const doc of selectedDocs) {
        const template_id = selectedTemplateByType[doc]!
        try {
          const created = await createWorkflow({
            document_id,
            template_id,
            start_immediately: true,
          })
          runs[doc] = created.workflow_run_id
        } catch (workflowErr: unknown) {
          const msg = getApiErrorMessage(
            workflowErr,
            'Failed to create workflow run.'
          )
          setWorkflowRuns({ ...runs })
          const detail = `Failed while starting ${doc} (template ${template_id}): ${msg}`
          setError(detail)
          setValidationError(detail)
          setStatus(Object.keys(runs).length ? 'running' : 'idle')
          return
        }
      }

      setWorkflowRuns(runs)
      setStatus('running')

      navigate('/progress')
    } catch (err: unknown) {
      const msg = getApiErrorMessage(err, 'Failed to start pipeline. Check your backend.')
      setError(msg)
      setValidationError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-56px)] bg-white">
      <div className="bg-ey-nav text-white px-8 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-1 h-12 bg-ey-primary shrink-0" />
            <div>
              <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-1 font-medium">
                AI SDLC Platform
              </p>
              <h1 className="font-display font-bold text-5xl uppercase leading-none tracking-tight text-white">
                Document<br />Generator
              </h1>
            </div>
          </div>
          <p className="font-body text-sm text-white/50 max-w-lg leading-relaxed">
            Upload your Business Requirements Document and let the pipeline generate
            enterprise-grade PDD, SDD, and UAT documentation automatically.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="space-y-12">
          <section className="animate-slide-up">
            <SectionLabel number="01" label="Upload Document" />
            <FileUploader />
          </section>

          <section className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <SectionLabel number="02" label="Output Documents" />
            <DocumentSelector />
          </section>

          <section className="animate-slide-up" style={{ animationDelay: '0.15s' }}>
            <SectionLabel number="03" label="Templates (one per type)" />
            <TemplateSelector />
          </section>

          {validationError && (
            <div className="flex items-center gap-3 border border-red-200 bg-red-50 px-5 py-4 animate-fade-in">
              <AlertCircle size={16} color="#DC2626" />
              <p className="font-body text-sm text-red-600">{validationError}</p>
            </div>
          )}

          <div className="pt-2 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={submitting}
              className={`group flex items-center gap-4 px-10 py-5 font-display font-bold text-xl uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                submitting
                  ? 'bg-ey-border text-ey-muted cursor-not-allowed'
                  : canSubmit
                    ? 'bg-ey-ink-strong text-ey-primary hover:bg-ey-primary hover:text-ey-ink-strong'
                    : 'bg-ey-surface text-ey-muted hover:bg-ey-border'
              }`}
            >
              {submitting ? 'Starting Pipeline…' : 'Generate Documents'}
              {!submitting && (
                <ArrowRight
                  size={20}
                  className="transition-transform group-hover:translate-x-1 text-current"
                />
              )}
            </button>

            <div className="flex items-center gap-6 mt-5 flex-wrap">
              <StatusDot active={!!uploadedFile} label="File ready" />
              <StatusDot
                active={selectedDocs.length > 0}
                label={`${selectedDocs.length} doc(s) selected`}
              />
              <StatusDot active={templatesReady} label="Templates for each type" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SectionLabel({ number, label }: { number: string; label: string }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <span className="font-display font-bold text-3xl text-ey-primary leading-none">{number}</span>
      <div className="h-px flex-1 bg-ey-border" />
      <span className="font-body text-xs font-semibold tracking-widest uppercase text-ey-muted">
        {label}
      </span>
    </div>
  )
}

function StatusDot({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full transition-colors ${active ? 'bg-ey-ink-strong' : 'bg-ey-border'}`}
      />
      <span
        className={`font-body text-xs transition-colors ${active ? 'text-ey-ink-strong font-medium' : 'text-ey-muted'}`}
      >
        {label}
      </span>
    </div>
  )
}
```

#### `frontend/src/store/useJobStore.ts`

**Language hint:** `typescript`

```typescript
import { create } from 'zustand'
import type { WorkflowStatusData } from '../api/types'

export type DocType = 'PDD' | 'SDD' | 'UAT'

/** UI-facing template row (mapped from API). */
export interface Template {
  id: string
  template_id: string
  filename: string
  type: string
  template_type: string | null
  status: string
  description: string
  sections_preview: string[]
  is_custom?: boolean
}

export interface Section {
  section_id: string
  title: string
}

export interface DocumentOutput {
  type: DocType
  sections: Section[]
}

type UiStatus = 'idle' | 'running' | 'completed' | 'failed'

interface JobStore {
  documentId: string | null
  uploadedFile: File | null
  selectedDocs: DocType[]
  /** One template per deliverable type (required for each selected DocType). */
  selectedTemplateByType: Partial<Record<DocType, string>>

  workflowRunByType: Partial<Record<DocType, string>>
  workflowDetailByType: Partial<Record<DocType, WorkflowStatusData>>

  status: UiStatus
  progress: number
  currentStep: string
  errorMessage: string | null
  perTypeProgress: Partial<Record<DocType, number>>
  perTypeStep: Partial<Record<DocType, string>>

  documents: DocumentOutput[]
  activDoc: DocType | null
  activeSectionId: string | null
  sectionContent: string | null

  setDocumentId: (id: string | null) => void
  setUploadedFile: (f: File | null) => void
  toggleDoc: (doc: DocType) => void
  setSelectedDocs: (docs: DocType[]) => void
  setSelectedTemplateForType: (doc: DocType, templateId: string | null) => void
  setWorkflowRun: (doc: DocType, workflowRunId: string) => void
  setWorkflowRuns: (runs: Partial<Record<DocType, string>>) => void
  setWorkflowDetail: (doc: DocType, detail: WorkflowStatusData) => void
  setStatus: (s: UiStatus) => void
  setProgress: (p: number, step?: string) => void
  setPerTypeProgress: (doc: DocType, p: number, step?: string) => void
  setDocuments: (docs: DocumentOutput[]) => void
  setActiveDoc: (doc: DocType) => void
  setActiveSectionId: (id: string | null) => void
  setSectionContent: (c: string | null) => void
  setError: (msg: string | null) => void
  reset: () => void
}

const initialState = {
  documentId: null,
  uploadedFile: null,
  selectedDocs: ['PDD', 'SDD', 'UAT'] as DocType[],
  selectedTemplateByType: {} as Partial<Record<DocType, string>>,
  workflowRunByType: {} as Partial<Record<DocType, string>>,
  workflowDetailByType: {} as Partial<Record<DocType, WorkflowStatusData>>,
  status: 'idle' as const,
  progress: 0,
  currentStep: '',
  errorMessage: null,
  perTypeProgress: {} as Partial<Record<DocType, number>>,
  perTypeStep: {} as Partial<Record<DocType, string>>,
  documents: [] as DocumentOutput[],
  activDoc: null,
  activeSectionId: null,
  sectionContent: null,
}

export const useJobStore = create<JobStore>((set) => ({
  ...initialState,

  setDocumentId: (id) => set({ documentId: id }),
  setUploadedFile: (f) => set({ uploadedFile: f }),
  toggleDoc: (doc) =>
    set((state) => {
      const next = state.selectedDocs.includes(doc)
        ? state.selectedDocs.filter((d) => d !== doc)
        : [...state.selectedDocs, doc]
      const tpl = { ...state.selectedTemplateByType }
      if (!next.includes(doc)) delete tpl[doc]
      return { selectedDocs: next, selectedTemplateByType: tpl }
    }),
  setSelectedDocs: (docs) => set({ selectedDocs: docs }),
  setSelectedTemplateForType: (doc, templateId) =>
    set((state) => {
      const next = { ...state.selectedTemplateByType }
      if (templateId) next[doc] = templateId
      else delete next[doc]
      return { selectedTemplateByType: next }
    }),
  setWorkflowRun: (doc, workflowRunId) =>
    set((state) => ({
      workflowRunByType: { ...state.workflowRunByType, [doc]: workflowRunId },
    })),
  setWorkflowRuns: (runs) =>
    set({ workflowRunByType: runs, workflowDetailByType: {}, documents: [] }),
  setWorkflowDetail: (doc, detail) =>
    set((state) => ({
      workflowDetailByType: { ...state.workflowDetailByType, [doc]: detail },
    })),
  setStatus: (s) => set({ status: s }),
  setProgress: (p, step) => set({ progress: p, currentStep: step ?? '' }),
  setPerTypeProgress: (doc, p, step) =>
    set((state) => ({
      perTypeProgress: { ...state.perTypeProgress, [doc]: p },
      ...(step !== undefined ? { perTypeStep: { ...state.perTypeStep, [doc]: step } } : {}),
    })),
  setDocuments: (docs) => set({ documents: docs }),
  setActiveDoc: (doc) => set({ activDoc: doc, activeSectionId: null, sectionContent: null }),
  setActiveSectionId: (id) => set({ activeSectionId: id }),
  setSectionContent: (c) => set({ sectionContent: c }),
  setError: (msg) => set({ errorMessage: msg }),
  reset: () => set(initialState),
}))
```

#### `frontend/src/vite-env.d.ts`

**Language hint:** `typescript`

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

#### `frontend/tailwind.config.js`

**Language hint:** `javascript`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        /** EY-inspired semantic tokens (tune hexes against official brand when available). */
        ey: {
          primary: '#FFE600',
          primaryHover: '#E6CF00',
          ink: '#1A1A1A',
          'ink-strong': '#000000',
          muted: '#6B6B6B',
          surface: '#F7F7F7',
          border: '#E5E5E5',
          nav: '#000000',
          white: '#FFFFFF',
          /** Page well behind cards (viewer, previews). */
          canvas: '#f0f0f0',
        },
        /** Legacy aliases — map to same palette for gradual migration. */
        brand: {
          black: '#000000',
          yellow: '#FFE600',
          gray: '#F7F7F7',
          border: '#E5E5E5',
          text: '#1A1A1A',
          muted: '#6B6B6B',
        },
      },
      fontFamily: {
        display: ['Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-bar': 'pulseBar 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        pulseBar: { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.6 } },
      },
    },
  },
  plugins: [],
}
```

#### `frontend/tsconfig.json`

**Language hint:** `json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"],
  "exclude": ["src/**/*.test.ts", "src/**/*.test.tsx"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### `frontend/tsconfig.node.json`

**Language hint:** `json`

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

#### `frontend/vite.config.ts`

**Language hint:** `typescript`

```typescript
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// `loadEnv` loads .env files; BACKEND_ORIGIN / VITE_DEV_PROXY_TARGET are not exposed to the client bundle.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget =
    env.BACKEND_ORIGIN ||
    env.VITE_DEV_PROXY_TARGET ||
    'http://127.0.0.1:8000'

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
```

#### `frontend/vitest.config.ts`

**Language hint:** `typescript`

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
```