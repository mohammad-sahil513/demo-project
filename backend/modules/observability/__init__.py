"""Cost rollup and observability helpers.

Single module today: :mod:`modules.observability.cost_rollup` aggregates the
per-call cost JSONL into a workflow-level summary that the API exposes via
``GET /workflow-runs/{id}/observability``.
"""
