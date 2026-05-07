"""Compile-time classifier timeout and retries."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from core.config import settings
from core.exceptions import TemplateException
from services.template_service import TemplateService


def test_classify_resilient_fails_after_timeouts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "template_classifier_timeout_seconds", 0.05)
    monkeypatch.setattr(settings, "template_classifier_max_retries", 1)

    mock_repo = MagicMock()
    svc = TemplateService(mock_repo)

    async def slow(_skeleton: object) -> dict[str, object]:
        await asyncio.sleep(1.0)
        return {}

    svc._classifier.classify_sections = slow  # type: ignore[method-assign]

    async def _run() -> object:
        return await svc._classify_sections_resilient({})

    with pytest.raises(TemplateException, match="timed out"):
        asyncio.run(_run())
