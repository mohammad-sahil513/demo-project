"""Section classification for custom template headings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.exceptions import TemplateException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.models import DocumentSkeleton


class TemplateClassifier:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_path: Path | None = None) -> None:
        self._sk_adapter = sk_adapter
        self._prompt_path = prompt_path or (
            Path(__file__).resolve().parents[2] / "prompts" / "template" / "classifier.yaml"
        )

    def is_configured(self) -> bool:
        return self._sk_adapter.is_configured()

    async def classify_sections(self, skeleton: DocumentSkeleton) -> list[dict[str, Any]]:
        if not self.is_configured():
            # Offline-safe fallback classification for local environments.
            return [self._fallback_classification(i, heading) for i, heading in enumerate(skeleton.headings)]

        prompt_template = self._load_prompt_template()
        headings_blob = "\n".join(f"- {heading}" for heading in skeleton.headings)
        prompt = prompt_template.format(headings=headings_blob, title=skeleton.title)
        payload = await self._sk_adapter.invoke_json(prompt, task="template_classification")
        raw_items = payload.get("sections")
        if not isinstance(raw_items, list):
            raise TemplateException("Template classifier returned invalid payload.")
        results: list[dict[str, Any]] = []
        for idx, item in enumerate(raw_items):
            if not isinstance(item, dict):
                continue
            results.append(
                {
                    "heading": str(item.get("heading") or skeleton.headings[min(idx, len(skeleton.headings) - 1)]),
                    "output_type": self._normalize_output_type(str(item.get("output_type") or "text")),
                    "description": str(item.get("description") or ""),
                    "prompt_selector": str(item.get("prompt_selector") or "default"),
                    "required_fields": list(item.get("required_fields") or []),
                    "is_complex": bool(item.get("is_complex") or False),
                },
            )
        if not results:
            raise TemplateException("Template classifier returned empty section list.")
        return results

    def _load_prompt_template(self) -> str:
        if not self._prompt_path.is_file():
            raise TemplateException(f"Template classifier prompt missing: {self._prompt_path}")
        return self._prompt_path.read_text(encoding="utf-8")

    def _fallback_classification(self, index: int, heading: str) -> dict[str, Any]:
        lower = heading.lower()
        output_type = "table" if any(token in lower for token in ("matrix", "table", "register", "log")) else "text"
        if "diagram" in lower or "architecture" in lower:
            output_type = "diagram"
        return {
            "heading": heading,
            "output_type": output_type,
            "description": f"Generated section for heading: {heading}",
            "prompt_selector": "default",
            "required_fields": [],
            "is_complex": index <= 1,
        }

    def _normalize_output_type(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"text", "table", "diagram"}:
            return normalized
        return "text"
