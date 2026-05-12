# Docs Start Here

This index is the fastest path to understand the repository without guessing reading order.

## Purpose
- Provide a single entry point and navigation map for the documentation set.

## Inputs
- Reader role (backend, frontend, ops/release).
- Current task (onboarding, implementation, debugging, release).

## Outputs
- Ordered reading paths.
- File-by-file doc purpose map.
- Links to operational runbooks and contribution workflow.

## Failure Modes
- Broken or stale links can misroute onboarding.
- Missing docs references can hide important contracts.
- Overlapping docs can create conflicting guidance.

## Recommended First-Day Reading Order

1. [`../README.md`](../README.md) - local setup, environment variables, smoke test.
2. [`HANDOVER.md`](HANDOVER.md) - full transfer-of-ownership runbook (start here for new maintainers).
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) - system architecture, runtime stack, and core models.
4. [`API.md`](API.md) - API request/response contract and SSE expectations.
5. [`PIPELINE.md`](PIPELINE.md) - workflow phases, template/generation behavior, observability flow.
6. [`OPERATIONS.md`](OPERATIONS.md) - engineering/operational guardrails.
7. [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md) - template lifecycle and strict-fidelity operations.

## Role-Based Reading Paths

### Backend Engineer

1. [`ARCHITECTURE.md`](ARCHITECTURE.md)
2. [`API.md`](API.md)
3. [`PIPELINE.md`](PIPELINE.md)
4. [`OPERATIONS.md`](OPERATIONS.md)
5. [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md)

### Frontend Engineer

1. [`../frontend/README.md`](../frontend/README.md)
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) (user journey + integration shape)
3. [`API.md`](API.md)
4. [`PIPELINE.md`](PIPELINE.md)
5. [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md)

### Ops / Release / QA

1. [`../README.md`](../README.md) (environment + smoke test)
2. [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. [`RELEASE_OPERATIONS.md`](RELEASE_OPERATIONS.md)
4. [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md)
5. [`OPERATIONS.md`](OPERATIONS.md)

## File Catalog (What Each Doc Covers)

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System overview, layers, stack, and key data model contracts.
- [`API.md`](API.md) - REST + SSE endpoint contracts and frontend-critical fields.
- [`PIPELINE.md`](PIPELINE.md) - Workflow phases, template flow, generation, assembly/export, observability.
- [`OPERATIONS.md`](OPERATIONS.md) - Engineering and operational guardrails.
- [`HANDOVER.md`](HANDOVER.md) - Detailed handover guide for onboarding and operational continuity.
- [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md) - Consolidated template authoring, runbook, fidelity, flags, validation, and UAT observability.
- [`RELEASE_OPERATIONS.md`](RELEASE_OPERATIONS.md) - Consolidated go-live and release checklist.

## Related Operational Docs

- Repository setup and environment: [`../README.md`](../README.md)
- Backend runtime conventions: [`../backend/README.md`](../backend/README.md)
- Root setup scripts runbook: [`../scripts/README.md`](../scripts/README.md)
- Contribution workflow: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
