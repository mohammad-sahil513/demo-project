"""Kroki base URL validation (defense-in-depth against SSRF misconfiguration).

``KROKI_URL`` is trusted configuration: the renderer POSTs diagram sources to
``{base}/{diagram_type}/png``. Operators must point it at a dedicated Kroki
instance. This module rejects obviously unsafe shapes so a typo cannot aim
the client at cloud metadata endpoints or non-HTTP schemes.
"""

from __future__ import annotations

from urllib.parse import urlparse

# Hostnames and literals commonly used for instance metadata (SSRF targets).
_BLOCKED_HOSTS: frozenset[str] = frozenset(
    {
        "169.254.169.254",
        "metadata.google.internal",
        "metadata.gce.internal",
    }
)


def validate_kroki_base_url(raw: str) -> str:
    """Return a normalized base URL (no trailing slash) or raise ``ValueError``.

    Empty strings are not accepted here — callers that mean "disabled" should
    pass through before invoking this (see :class:`Settings` ``kroki_url``).
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("KROKI_URL is empty; omit the variable to use the default or set a valid http(s) URL.")

    parsed = urlparse(s)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("KROKI_URL must use http or https.")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("KROKI_URL must include a hostname.")

    if host in _BLOCKED_HOSTS:
        raise ValueError(f"KROKI_URL host {host!r} is not allowed (metadata / SSRF hardening).")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("KROKI_URL must not include user credentials.")

    if parsed.query or parsed.fragment:
        raise ValueError("KROKI_URL must not include a query string or fragment.")

    return s.rstrip("/")
