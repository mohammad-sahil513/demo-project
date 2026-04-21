"""LLM text section generation."""

from __future__ import annotations

from typing import Any

from core.constants import TASK_TO_MODEL
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition


class TextSectionGenerator:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_loader: GenerationPromptLoader | None = None) -> None:
        self._sk = sk_adapter
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        return self._sk.is_configured()

    def _task_for_section(self, section: SectionDefinition) -> str:
        if section.is_complex:
            return "complex_section"
        return "text_generation"

    async def generate(
        self,
        *,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
    ) -> dict[str, Any]:
        template = self._prompts.load_template("text", section.prompt_selector)
        evidence_context = evidence_text_from_retrieval(retrieval_payload)
        mapping = build_prompt_mapping(section, doc_type, evidence_context)
        prompt = self._prompts.render_template(template, mapping)
        task = self._task_for_section(section)
        model = TASK_TO_MODEL[task]
        before = cost_tracker.snapshot()
        text = await self._sk.invoke_text(prompt, task=task, cost_tracker=cost_tracker)
        after = cost_tracker.snapshot()
        t_in, t_out, cost_usd = llm_delta_between_snapshots(before, after)
        return {
            "output_type": "text",
            "content": text.strip(),
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": task,
            "error": None,
        }
