"""Diagram generation: LLM → PlantUML/Mermaid → Kroki PNG."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Protocol

from core.constants import TASK_TO_MODEL
from core.exceptions import GenerationException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition

MAX_PLANTUML_ATTEMPTS = 6
MAX_MERMAID_ATTEMPTS = 3


class DiagramRenderClient(Protocol):
    async def render_png(self, diagram_type: str, source: str) -> bytes: ...


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    fence = re.search(r"^```(?:[a-zA-Z0-9_-]+)?\s*(.*?)\s*```$", cleaned, flags=re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return cleaned


def extract_plantuml(text: str) -> str:
    cleaned = _strip_code_fence(text)
    if "@startuml" in cleaned and "@enduml" in cleaned:
        start = cleaned.index("@startuml")
        end = cleaned.rindex("@enduml") + len("@enduml")
        return cleaned[start:end].strip()
    return cleaned.strip()


def extract_mermaid(text: str) -> str:
    return _strip_code_fence(text).strip()


class DiagramSectionGenerator:
    def __init__(
        self,
        sk_adapter: AzureSKAdapter,
        *,
        kroki: KrokiRenderer | DiagramRenderClient,
        storage_root: Path,
        prompt_loader: GenerationPromptLoader | None = None,
    ) -> None:
        self._sk = sk_adapter
        self._kroki = kroki
        self._storage_root = storage_root
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        if not self._sk.is_configured():
            return False
        if hasattr(self._kroki, "is_configured"):
            return bool(self._kroki.is_configured())
        return True

    def _write_png(self, workflow_run_id: str, section_id: str, fmt: str, attempt: int, data: bytes) -> str:
        rel_dir = Path("diagrams") / workflow_run_id
        out_dir = self._storage_root / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{section_id}_{fmt}_a{attempt}.png"
        out_path = out_dir / filename
        out_path.write_bytes(data)
        return str(rel_dir / filename).replace("\\", "/")

    async def generate(
        self,
        *,
        workflow_run_id: str,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
    ) -> dict[str, Any]:
        evidence_context = evidence_text_from_retrieval(retrieval_payload)
        base_mapping = build_prompt_mapping(section, doc_type, evidence_context)
        tokens_in = tokens_out = 0
        cost_usd = 0.0
        model = TASK_TO_MODEL["diagram_generation"]
        last_error: str | None = None
        diagram_path: str | None = None
        diagram_format: str | None = None
        last_source = ""

        plantuml_template = self._prompts.load_template("diagram", section.prompt_selector)
        correction_template = self._prompts.load_template("diagram", "correction")

        for attempt in range(1, MAX_PLANTUML_ATTEMPTS + 1):
            before = cost_tracker.snapshot()
            if attempt == 1:
                prompt = self._prompts.render_template(plantuml_template, base_mapping)
                try:
                    raw = await self._sk.invoke_text(prompt, task="diagram_generation", cost_tracker=cost_tracker)
                except GenerationException as exc:
                    last_error = str(exc.message)
                    break
            else:
                correction_map = build_prompt_mapping(
                    section,
                    doc_type,
                    evidence_context,
                    render_error=last_error or "Unknown render error",
                    failed_diagram_source=last_source or "(empty)",
                )
                prompt = self._prompts.render_template(correction_template, correction_map)
                try:
                    raw = await self._sk.invoke_text(prompt, task="diagram_correction", cost_tracker=cost_tracker)
                except GenerationException as exc:
                    last_error = str(exc.message)
                    break
            after = cost_tracker.snapshot()
            di, do, dc = llm_delta_between_snapshots(before, after)
            tokens_in += di
            tokens_out += do
            cost_usd += dc

            last_source = extract_plantuml(raw)
            try:
                png = await self._kroki.render_png("plantuml", last_source)
            except GenerationException as exc:
                last_error = str(exc.message)
                continue

            diagram_path = self._write_png(workflow_run_id, section.section_id, "plantuml", attempt, png)
            diagram_format = "plantuml"
            caption = f"### {section.title}\n\n![{section.title}]({diagram_path})\n"
            return {
                "output_type": "diagram",
                "content": caption.strip(),
                "diagram_path": diagram_path,
                "diagram_format": diagram_format,
                "diagram_source": last_source,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "model": model,
                "task": "diagram_generation",
                "error": None,
            }

        mermaid_template = self._prompts.load_template("diagram", "mermaid_default")
        for attempt in range(1, MAX_MERMAID_ATTEMPTS + 1):
            before = cost_tracker.snapshot()
            prompt = self._prompts.render_template(mermaid_template, base_mapping)
            try:
                raw = await self._sk.invoke_text(prompt, task="diagram_generation", cost_tracker=cost_tracker)
            except GenerationException as exc:
                last_error = str(exc.message)
                break
            after = cost_tracker.snapshot()
            di, do, dc = llm_delta_between_snapshots(before, after)
            tokens_in += di
            tokens_out += do
            cost_usd += dc

            source = extract_mermaid(raw)
            try:
                png = await self._kroki.render_png("mermaid", source)
            except GenerationException as exc:
                last_error = str(exc.message)
                continue

            diagram_path = self._write_png(workflow_run_id, section.section_id, "mermaid", attempt, png)
            diagram_format = "mermaid"
            caption = f"### {section.title}\n\n![{section.title}]({diagram_path})\n"
            return {
                "output_type": "diagram",
                "content": caption.strip(),
                "diagram_path": diagram_path,
                "diagram_format": diagram_format,
                "diagram_source": source,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "model": model,
                "task": "diagram_generation",
                "error": None,
            }

        err_text = last_error or "Diagram generation failed."
        return {
            "output_type": "diagram",
            "content": f"### {section.title}\n\n_Diagram generation failed: {err_text}_\n",
            "diagram_path": diagram_path,
            "diagram_format": diagram_format,
            "diagram_source": last_source,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": "diagram_generation",
            "error": err_text,
        }
