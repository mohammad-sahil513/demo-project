"""Section classification for custom template headings.

Given a :class:`DocumentSkeleton` (parsed headings + structure), the
classifier asks the LLM to label each heading with:

- ``output_type``      ``"text"`` | ``"table"`` | ``"diagram"``
- ``description``      short blurb shown in the UI and used as prompt context
- ``prompt_selector``  which prompt YAML to use during generation
- ``required_fields``  expected columns / structured fields per section
- ``content_mode``     ``"generate"`` | ``"skip"`` | ``"heading_only"``
- ``is_complex``       route to the stronger LLM

Robustness: the classifier falls back to a deterministic heuristic any time
the LLM call or the response is unusable (no adapter, no prompt file,
non-dict payload, missing sections list, empty results, etc.). The heuristic
keys off heading text — words like "matrix", "table", "register" -> table;
"diagram", "architecture", "flow" -> diagram. Anything else -> text.
"""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any

import yaml

from core.exceptions import TemplateException
from core.logging import get_logger
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.heading_plan_filter import all_heading_items_from_skeleton
from modules.template.models import DocumentSkeleton, ExtractedHeading
from modules.template.planner import _normalize_content_mode

logger = get_logger(__name__)


class TemplateClassifier:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_path: Path | None = None) -> None:
        self._sk_adapter = sk_adapter
        base = Path(__file__).resolve().parents[2]
        self._prompt_candidates: list[Path] = [
            prompt_path if prompt_path is not None else base / "prompts" / "template" / "classifier.yaml",
            base / "prompts" / "template" / "classifier.yaml",
            base / "prompts" / "classifier.yaml",
        ]

    def is_configured(self) -> bool:
        return self._sk_adapter.is_configured()

    async def classify_sections(self, skeleton: DocumentSkeleton) -> list[dict[str, Any]]:
        """
        Classify extracted headings into structured section metadata.

        Fallback behavior:
        - If SK adapter is not configured -> heuristic fallback
        - If prompt file is missing -> heuristic fallback
        - If model returns invalid/empty JSON -> heuristic fallback
        """
        heading_items = all_heading_items_from_skeleton(skeleton)
        if not heading_items:
            return []

        if not self.is_configured():
            logger.info("template.classifier.fallback reason=adapter_not_configured")
            return self._fallback_all(heading_items)

        try:
            prompt_template = self._load_prompt_template()
        except TemplateException:
            logger.warning("template.classifier.fallback reason=prompt_missing")
            return self._fallback_all(heading_items)

        headings_blob = "\n".join(self._format_heading_line(item) for item in heading_items)

        prompt = Template(prompt_template).safe_substitute(
            headings=headings_blob,
            title=skeleton.title or "",
        )

        try:
            payload = await self._sk_adapter.invoke_json(prompt, task="template_classification")
        except Exception:
            logger.exception("template.classifier.invoke_json.failed")
            return self._fallback_all(heading_items)

        if not isinstance(payload, dict):
            logger.warning("template.classifier.fallback reason=payload_not_dict")
            return self._fallback_all(heading_items)

        raw_items = payload.get("sections")
        if not isinstance(raw_items, list):
            logger.warning("template.classifier.fallback reason=sections_missing_or_invalid")
            return self._fallback_all(heading_items)

        results: list[dict[str, Any]] = []

        for idx, item in enumerate(raw_items):
            if not isinstance(item, dict):
                continue

            fallback_heading = (
                heading_items[min(idx, len(heading_items) - 1)].text
                if heading_items
                else f"Section {idx + 1}"
            )

            required_fields = item.get("required_fields") or []
            if not isinstance(required_fields, list):
                required_fields = []

            inc = item.get("include_in_section_plan")
            if inc is None:
                include_flag: bool | None = None
            else:
                include_flag = bool(inc)

            results.append(
                {
                    "heading": str(item.get("heading") or fallback_heading),
                    "output_type": self._normalize_output_type(str(item.get("output_type") or "text")),
                    "description": str(item.get("description") or ""),
                    "prompt_selector": str(item.get("prompt_selector") or "default"),
                    "required_fields": [str(field) for field in required_fields],
                    "is_complex": bool(item.get("is_complex") or False),
                    "content_mode": _normalize_content_mode(item.get("content_mode")),
                    "include_in_section_plan": include_flag,
                }
            )

        if not results:
            logger.warning("template.classifier.fallback reason=empty_results")
            return self._fallback_all(heading_items)

        # Ensure one result per heading, preserving order
        if len(results) < len(heading_items):
            for idx in range(len(results), len(heading_items)):
                item = heading_items[idx]
                results.append(self._fallback_classification(idx, item.text, order=item.order))

        if len(results) > len(heading_items):
            results = results[: len(heading_items)]

        self._attach_heading_keys(results, heading_items)
        logger.info("template.classifier.completed sections=%s", len(results))
        return results

    def _format_heading_line(self, item: ExtractedHeading) -> str:
        numbering = f"{item.numbering} " if item.numbering else ""
        return f'- [L{item.level}] {numbering}{item.text}'

    def _load_prompt_template(self) -> str:
        """
        Search for the classifier prompt in multiple supported locations.

        Supported formats:
        - YAML:
            prompt: |
              ...
        - Plain text prompt file
        """
        checked: list[str] = []

        for candidate in self._prompt_candidates:
            if candidate is None:
                continue

            checked.append(str(candidate))
            if not candidate.is_file():
                continue

            raw = candidate.read_text(encoding="utf-8")

            try:
                data = yaml.safe_load(raw)
            except Exception:
                data = None

            if isinstance(data, dict):
                for key in ("prompt", "template", "content", "text"):
                    value = data.get(key)
                    if isinstance(value, str) and value.strip():
                        logger.info("template.classifier.prompt.loaded path=%s", str(candidate))
                        return value

            if raw.strip():
                logger.info("template.classifier.prompt.loaded path=%s", str(candidate))
                return raw

        raise TemplateException(
            f"Template classifier prompt missing. Checked: {', '.join(checked)}"
        )

    def _fallback_all(self, heading_items: list[ExtractedHeading]) -> list[dict[str, Any]]:
        rows = [
            self._fallback_classification(index, item.text, order=item.order)
            for index, item in enumerate(heading_items)
        ]
        self._attach_heading_keys(rows, heading_items)
        return rows

    @staticmethod
    def _attach_heading_keys(results: list[dict[str, Any]], heading_items: list[ExtractedHeading]) -> None:
        for i, row in enumerate(results):
            if i < len(heading_items):
                row["heading_key"] = str(heading_items[i].order)

    def _fallback_classification(self, index: int, heading: str, *, order: int) -> dict[str, Any]:
        lower = heading.lower()
        output_type = "text"

        if any(token in lower for token in ("matrix", "table", "register", "log", "grid", "checklist")):
            output_type = "table"

        if any(token in lower for token in ("diagram", "architecture", "flow", "sequence", "component")):
            output_type = "diagram"

        return {
            "heading": heading,
            "heading_key": str(order),
            "output_type": output_type,
            "description": f"Generated section for heading: {heading}",
            "prompt_selector": "default",
            "required_fields": [],
            "is_complex": index <= 1,
            "content_mode": "generate",
            "include_in_section_plan": None,
        }

    def _normalize_output_type(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"text", "table", "diagram"}:
            return normalized
        return "text"
