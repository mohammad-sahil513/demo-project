"""HTTP API layer (FastAPI router, routes, and dependency wiring).

This package is the **only** layer allowed to import from
:mod:`services`. Routes translate validated HTTP input into service
calls and wrap the result in the standard JSON envelope from
:mod:`core.response`.

Layout:

- :mod:`api.router`         Mounts every feature router under the public
                            ``/api`` prefix.
- :mod:`api.deps`           Dependency providers used via FastAPI's
                            ``Depends(...)`` so every route gets a wired
                            service instance.
- :mod:`api.routes`         One module per resource: documents,
                            templates, workflows, outputs, events, health.

Routes never instantiate repositories or infrastructure adapters
directly — they only consume services.
"""
