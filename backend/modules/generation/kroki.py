"""Kroki HTTP render client (PlantUML / Mermaid -> PNG).

Kroki is run as a sidecar service (default ``http://localhost:8001``). We
POST the diagram source to ``/<diagram_type>/png`` and receive PNG bytes
back. The renderer is stateless; failures raise :class:`GenerationException`
so the diagram generator can fall back to a neutral placeholder.
"""

from __future__ import annotations

import httpx

from core.exceptions import GenerationException


class KrokiRenderer:
    """Thin HTTP adapter over the Kroki ``POST /<type>/png`` endpoint."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 60.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self._base)

    async def render_png(self, diagram_type: str, source: str) -> bytes:
        """POST ``source`` to Kroki and return the rendered PNG bytes.

        ``diagram_type`` must be one Kroki understands (``plantuml``,
        ``mermaid``, etc.). Any HTTP failure becomes a
        ``KROKI_RENDER_FAILED`` :class:`GenerationException` — diagram
        generators wrap this into a neutral fallback rather than failing
        the whole workflow.
        """
        if not self.is_configured():
            raise GenerationException("Kroki URL is not configured.", code="KROKI_NOT_CONFIGURED")
        url = f"{self._base}/{diagram_type}/png"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                # Kroki accepts the raw diagram source as the request body
                # — no JSON wrapping. ``Content-Type: text/plain`` is what
                # the server documentation specifies.
                response = await client.post(
                    url,
                    content=source.encode("utf-8"),
                    headers={"Content-Type": "text/plain"},
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as exc:
            raise GenerationException(
                f"Kroki render failed for {diagram_type}: {exc}",
                code="KROKI_RENDER_FAILED",
            ) from exc
