"""Per-resource HTTP route modules.

Each module here exposes a ``router = APIRouter()`` plus the path operations
for one resource. The central :mod:`api.router` mounts them under their
URL prefix. See :doc:`docs/API` for the full
public contract and JSON envelopes.
"""
