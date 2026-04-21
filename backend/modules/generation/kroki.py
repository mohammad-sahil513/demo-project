"""Kroki HTTP render client (PlantUML / Mermaid → PNG)."""

from __future__ import annotations

import httpx

from core.exceptions import GenerationException


class KrokiRenderer:
    def __init__(self, base_url: str, *, timeout_seconds: float = 60.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self._base)

    async def render_png(self, diagram_type: str, source: str) -> bytes:
        if not self.is_configured():
            raise GenerationException("Kroki URL is not configured.", code="KROKI_NOT_CONFIGURED")
        url = f"{self._base}/{diagram_type}/png"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
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
