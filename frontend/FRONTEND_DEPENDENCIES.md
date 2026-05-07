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
