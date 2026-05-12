# Release Operations

This document is the consolidated pre-release and go-live checklist for production deployments.

## Purpose
- Provide a single release gate for build hygiene, config safety, tests, CI, and smoke validation.

## Inputs
- Candidate release branch and artifacts.
- Deployment environment variables and feature flags.
- Test/CI evidence.

## Outputs
- Go/no-go readiness signal.
- Reduced deployment risk.
- Repeatable release workflow.

## Failure Modes
- Skipped checks can push unstable builds.
- Misconfigured flags can violate export/fidelity guarantees.
- Missing post-deploy verification can delay incident detection.

## 1) Branch and Artifact Hygiene
- Work from a clean release branch with only intentional changes.
- Ensure runtime artifacts are excluded from git (`backend/storage`, `frontend/dist`, caches).
- Remove temporary debug files/scripts from release scope.

## 2) Backend Safety Gates
- `APP_ENV` is `staging` or `production`.
- `APP_DEBUG=false` in production.
- Strict template profile enabled:
  - `TEMPLATE_DOCX_PLACEHOLDER_NATIVE_ENABLED=true`
  - `TEMPLATE_SECTION_BINDING_STRICT=true`
  - `TEMPLATE_FIDELITY_STRICT_ENABLED=true`
  - `TEMPLATE_SCHEMA_VALIDATION_BLOCKING=true`
  - `TEMPLATE_FIDELITY_MEDIA_INTEGRITY_BLOCKING=true`
  - `TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED=false`
  - `TEMPLATE_DOCX_REQUIRE_NATIVE_FOR_CUSTOM=true`
- Health checks pass:
  - `GET /api/health` returns `200`
  - `GET /api/ready` returns `200` in target env

### CORS, Kroki URL, and Azure deployment names

- **CORS:** Set `CORS_ORIGINS` to an explicit comma-separated allowlist of browser origins (for example the Static Web App and any admin domains). Do not ship production with `CORS_ORIGINS=*` unless you have consciously accepted open cross-origin API access and non-credentialed clients only.
- **Kroki:** Set `KROKI_URL` to the base URL of a **trusted** Kroki sidecar (same cluster/VNet as the API, or a known SaaS endpoint). The backend POSTs user-influenced diagram source to `{KROKI_URL}/{diagram_type}/png`. A mistaken value (for example an internal metadata URL) is an SSRF-style risk; restrict with network policy and configuration review. At startup, `core.config.Settings` rejects empty-host URLs, non-`http(s)` schemes, userinfo, query/fragment, and a small blocklist of metadata host literals (`core.kroki_url`); this does not replace network controls.
- **Azure OpenAI deployments:** `AZURE_OPENAI_GPT5_DEPLOYMENT`, `AZURE_OPENAI_GPT5MINI_DEPLOYMENT`, and `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` must **exactly** match the deployment names in your Azure OpenAI resource. The values in `backend/.env.example` align with `core.config.Settings` defaults; production must override them to match the portal.

## 3) Dependency and Test Integrity
- Backend: install from `backend/requirements.txt` and run `pytest -q`.
- Frontend: run `npm test`.
- Address or explicitly accept warnings before release cut.

## 4) Build and CI Checks
- Run frontend production build: `npm run build`.
- Ensure required CI workflows pass on release commit.
- Verify required deployment env vars are present.

## 5) Deployment and Rollback Readiness
- Promote/deploy only after gates above pass.
- Ensure rollback plan is documented and accessible to on-call.
- Confirm owner/on-call visibility for first post-release window.

## 6) Post-Deploy Smoke Validation
- Execute one end-to-end workflow run.
- Verify progress/SSE, output generation, and download endpoints.
- Check telemetry for `workflow.failed` and export integrity warnings/errors.
