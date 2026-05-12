"""Application services — orchestration between API and domain modules.

Services compose repositories, infrastructure adapters, and domain
modules into business-level operations the API layer can call. The
public methods on a service correspond roughly 1:1 with API endpoints
and represent the *use cases* of the system:

- :mod:`services.document_service`   upload / list / delete BRDs.
- :mod:`services.template_service`   custom template upload, compile,
                                     contract validation, fidelity probe.
- :mod:`services.workflow_service`   workflow run record management +
                                     validation guards.
- :mod:`services.workflow_executor`  the long-running phase pipeline.
- :mod:`services.output_service`     final artifact records and downloads.
- :mod:`services.event_service`      in-memory SSE event broker.
- :mod:`services.policy`             cross-cutting validation rules.

Services never import from ``api`` — that would invert the layering. The
API layer constructs each service in ``api.deps`` and injects it via
FastAPI dependency wiring.
"""
