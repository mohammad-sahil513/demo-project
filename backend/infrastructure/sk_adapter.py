"""Azure OpenAI adapter (task-routed)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import httpx
import orjson

from core.config import settings
from core.constants import (
    TASK_TO_MAX_COMPLETION_TOKENS,
    TASK_TO_MODEL,
    TASK_TO_REASONING_EFFORT,
)
from core.exceptions import GenerationException

AZURE_OPENAI_TIMEOUT_SECONDS = 90.0


@dataclass(frozen=True, slots=True)
class EmbeddingUsageResult:
    embedding: list[float]
    prompt_tokens: int


class AzureSKAdapter:
    """Task-routed LLM/embedding adapter for Azure OpenAI."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str | None = None,
        gpt5_deployment: str | None = None,
        gpt5mini_deployment: str | None = None,
        embedding_deployment: str | None = None,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_openai_endpoint).rstrip("/")
        self._api_key = api_key or settings.azure_openai_api_key
        self._api_version = api_version or settings.azure_openai_api_version
        self._gpt5_deployment = gpt5_deployment or settings.azure_openai_gpt5_deployment
        self._gpt5mini_deployment = gpt5mini_deployment or settings.azure_openai_gpt5mini_deployment
        self._embedding_deployment = embedding_deployment or settings.azure_openai_embedding_deployment

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key)

    async def invoke_text(
        self,
        prompt: str,
        *,
        task: str,
        cost_tracker: Any | None = None,
    ) -> str:
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.")
        model_alias = TASK_TO_MODEL.get(task)
        if not model_alias:
            raise GenerationException(f"Unsupported task: {task}", code="UNSUPPORTED_TASK")

        deployment = self._deployment_for_model(model_alias)
        payload: dict[str, Any] = {
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": TASK_TO_MAX_COMPLETION_TOKENS[task],
            "reasoning_effort": TASK_TO_REASONING_EFFORT[task],
        }
        body = await self._post_chat_completion(deployment, payload)
        text = self._extract_text(body)
        self._track_usage(cost_tracker, model_alias, task, body)
        return text

    async def invoke_json(
        self,
        prompt: str,
        *,
        task: str,
        cost_tracker: Any | None = None,
    ) -> dict[str, Any]:
        text = await self.invoke_text(prompt, task=task, cost_tracker=cost_tracker)
        parsed = self._parse_json_payload(text)
        if not isinstance(parsed, dict):
            raise GenerationException("Model returned non-object JSON payload.", code="JSON_OBJECT_REQUIRED")
        return parsed

    async def generate_embedding(self, text: str) -> list[float]:
        result = await self.generate_embedding_with_usage(text)
        return result.embedding

    async def generate_embedding_with_usage(self, text: str) -> EmbeddingUsageResult:
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.")
        url = (
            f"{self._endpoint}/openai/deployments/{self._embedding_deployment}/embeddings"
            f"?api-version={self._api_version}"
        )
        headers = {"api-key": self._api_key}
        payload = {"input": text}
        async with httpx.AsyncClient(timeout=AZURE_OPENAI_TIMEOUT_SECONDS) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        data = body.get("data") or []
        if not data or not isinstance(data, list):
            raise GenerationException("Embedding response missing data field.", code="EMBEDDING_RESPONSE_INVALID")
        embedding = data[0].get("embedding")
        if not isinstance(embedding, list):
            raise GenerationException("Embedding response missing vector.", code="EMBEDDING_VECTOR_MISSING")
        vector = [float(v) for v in embedding]
        usage = body.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        return EmbeddingUsageResult(embedding=vector, prompt_tokens=prompt_tokens)

    async def _post_chat_completion(self, deployment: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._endpoint}/openai/deployments/{deployment}/chat/completions?api-version={self._api_version}"
        headers = {"api-key": self._api_key}
        async with httpx.AsyncClient(timeout=AZURE_OPENAI_TIMEOUT_SECONDS) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _deployment_for_model(self, model_alias: str) -> str:
        if model_alias == "gpt5":
            return self._gpt5_deployment
        if model_alias == "gpt5mini":
            return self._gpt5mini_deployment
        raise GenerationException(f"Unsupported model alias: {model_alias}", code="UNSUPPORTED_MODEL_ALIAS")

    def _extract_text(self, body: dict[str, Any]) -> str:
        choices = body.get("choices") or []
        if not choices or not isinstance(choices, list):
            raise GenerationException("Completion response missing choices.", code="COMPLETION_RESPONSE_INVALID")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            if chunks:
                return "\n".join(chunks)
        raise GenerationException("Completion response missing text content.", code="COMPLETION_TEXT_MISSING")

    def _parse_json_payload(self, text: str) -> Any:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
            if fenced_match:
                cleaned = fenced_match.group(1).strip()
        try:
            return orjson.loads(cleaned)
        except orjson.JSONDecodeError:
            brace_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not brace_match:
                raise GenerationException("Model response is not valid JSON.", code="INVALID_JSON_RESPONSE") from None
            try:
                return orjson.loads(brace_match.group(0))
            except orjson.JSONDecodeError as exc:
                raise GenerationException("Model response is not valid JSON.", code="INVALID_JSON_RESPONSE") from exc

    def _track_usage(self, cost_tracker: Any | None, model_alias: str, task: str, body: dict[str, Any]) -> None:
        if cost_tracker is None:
            return
        usage = body.get("usage") or {}
        input_tokens = int(usage.get("prompt_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or 0)

        if hasattr(cost_tracker, "track_call"):
            cost_tracker.track_call(
                model=model_alias,
                task=task,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
