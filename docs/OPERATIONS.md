# Operations

Consolidated operational and engineering guardrails (replaces numbered rules/checklists-oriented docs).

## Purpose
- Provide daily implementation rules and operational guardrails in one place.

## Inputs
- Current architecture boundaries.
- Runtime configuration and deployment posture.
- Team workflow and review expectations.

## Outputs
- Consistent coding and integration patterns.
- Safer releases and easier incident response.
- Reduced regressions from contract/layer violations.

## Failure Modes
- Rule drift increases coupling and maintenance cost.
- Missing operational checks can cause production regressions.
- Inconsistent conventions reduce team velocity and review quality.

## 1) Engineering Rules

- Respect layer boundaries (API -> services; modules stay domain-focused).
- Use typed IDs and enum constants (avoid raw string statuses).
- Keep async paths non-blocking.
- Preserve response envelope conventions.
- Route cloud/provider calls through infrastructure adapters.

## 2) Storage and Artifact Rules

- Use configured storage root paths only.
- Keep runtime-generated artifacts out of source control.
- Persist workflow/output artifacts with deterministic naming.

## 3) Error and Reliability Rules

- Use domain exceptions for expected failures.
- Emit phase and workflow terminal events consistently.
- Preserve partial workflow state on failure where appropriate.

## 4) Observability and Logging Rules

- Track LLM calls/costs consistently.
- Keep per-workflow logs/observability records available for diagnosis.
- Ensure warning/error payloads are actionable.

## 5) Release and Template Ops

Operational runbooks are split by concern:
- Template lifecycle and strict-fidelity policy: [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md)
- Release/go-live checks: [`RELEASE_OPERATIONS.md`](RELEASE_OPERATIONS.md)

## 6) Team Workflow Notes

- Keep docs updated with behavior/contract changes.
- Validate backend/frontend test baselines before release.
- Prefer small, reviewable changes with explicit rationale.
