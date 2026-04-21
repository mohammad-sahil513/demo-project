"""Generation phase: prompts, LLM calls, diagram rendering."""

from __future__ import annotations

from modules.generation.cost_tracking import (
    GenerationCostTracker,
    GenerationCostSnapshot,
    llm_delta_between_snapshots,
)
from modules.generation.diagram_generator import DiagramSectionGenerator, extract_mermaid, extract_plantuml
from modules.generation.kroki import KrokiRenderer
from modules.generation.models import GenerationSectionResult
from modules.generation.observability import merge_generation_observability
from modules.generation.orchestrator import GenerationOrchestrator, compute_execution_waves
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator

__all__ = [
    "GenerationCostSnapshot",
    "GenerationCostTracker",
    "GenerationOrchestrator",
    "GenerationPromptLoader",
    "GenerationSectionResult",
    "DiagramSectionGenerator",
    "KrokiRenderer",
    "TableSectionGenerator",
    "TextSectionGenerator",
    "compute_execution_waves",
    "extract_mermaid",
    "extract_plantuml",
    "llm_delta_between_snapshots",
    "merge_generation_observability",
]
