"""Load plain-text generation prompts (YAML files read as UTF-8 templates)."""

from __future__ import annotations

from pathlib import Path

from core.exceptions import GenerationException


class GenerationPromptLoader:
    def __init__(self, prompts_root: Path | None = None) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        self._root = prompts_root or (backend_root / "prompts" / "generation")

    @staticmethod
    def render_template(template: str, mapping: dict[str, str]) -> str:
        class _Missing(dict[str, str]):
            def __missing__(self, key: str) -> str:
                return ""

        return template.format_map(_Missing(mapping))

    def load_template(self, category: str, selector: str) -> str:
        """category: text | table | diagram"""
        normalized = self._normalize_selector(selector)
        path = self._root / category / f"{normalized}.yaml"
        if not path.is_file():
            path = self._root / category / "default.yaml"
        if not path.is_file():
            raise GenerationException(f"Missing generation prompt for {category}/{selector}", code="PROMPT_MISSING")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _normalize_selector(selector: str) -> str:
        cleaned = (selector or "default").strip().lower().replace(" ", "_")
        return cleaned or "default"
