# API

Consolidated API contract reference (replaces numbered API contract doc).

## Purpose
- Define backend HTTP/SSE contracts the frontend and integrators depend on.

## Inputs
- FastAPI route surfaces.
- Response envelope/error conventions.
- Frontend status/SSE consumption requirements.

## Outputs
- Endpoint behavior reference.
- Required payload fields and status semantics.
- Integration safety constraints for API changes.

## Failure Modes
- Contract drift can break frontend parsing and UX.
- Missing fields can block progress/output flows.
- Incorrect status semantics can mis-handle retries/failures.

## 1) Response Envelope

JSON endpoints use:
- success: `{ success, message, data, errors, meta }`
- error: same envelope with `success=false` and populated `errors`

Binary/file and SSE endpoints are not wrapped.

## 2) Health and Readiness

- `GET /api/health`
- `GET /api/ready` (includes configuration + storage writable checks; returns 200/503 based on critical checks)

## 3) Core Resource Endpoints

### Documents
- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{document_id}`
- `DELETE /api/documents/{document_id}`

### Templates
- `POST /api/templates/upload`
- `GET /api/templates`
- `GET /api/templates/{template_id}`
- `GET /api/templates/{template_id}/compile-status`
- `GET /api/templates/{template_id}/download`
- `GET /api/templates/{template_id}/preview-html`
- `DELETE /api/templates/{template_id}`

### Workflows
- `POST /api/workflow-runs`
- `GET /api/workflow-runs`
- `GET /api/workflow-runs/{workflow_run_id}`
- `GET /api/workflow-runs/{workflow_run_id}/status`
- `GET /api/workflow-runs/{workflow_run_id}/sections`
- `GET /api/workflow-runs/{workflow_run_id}/sections/{section_id}/diagram`
- `GET /api/workflow-runs/{workflow_run_id}/observability`
- `GET /api/workflow-runs/{workflow_run_id}/errors`
- `GET /api/workflow-runs/{workflow_run_id}/diagnostics`
- `GET /api/workflow-runs/{workflow_run_id}/events` (SSE)

### Outputs
- `GET /api/outputs/{output_id}`
- `GET /api/outputs/{output_id}/download`

## 4) Frontend-Critical Contract Fields

Minimum fields required by frontend status flow:
- `workflow_run_id`
- `status`
- `current_phase`
- `overall_progress_percent`
- `current_step_label`
- `output_id`

Terminal semantics:
- `FAILED` -> show failure UX
- `COMPLETED` -> enable output loading/downloading

## 5) SSE Event Model

Each event includes:
- `type`
- `workflow_run_id`
- `timestamp`
- event-specific payload fields

Terminal events close frontend stream handling:
- `workflow.completed`
- `workflow.failed`

## 6) Change Management Rules

Before changing API payload shape:
- update frontend callers/types,
- update docs,
- preserve backward compatibility when possible.

## 7) Related Docs

- Architecture and models: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Pipeline/phase behavior behind endpoints: [`PIPELINE.md`](PIPELINE.md)
