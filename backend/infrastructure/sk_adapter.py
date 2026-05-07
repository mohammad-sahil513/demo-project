"""Azure OpenAI adapter (task-routed)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

from core.config import settings
from core.constants import (
    TASK_TO_MAX_COMPLETION_TOKENS,
    TASK_TO_MODEL,
    TASK_TO_REASONING_EFFORT,
)
from core.exceptions import GenerationException
from core.token_count import count_tokens

logger = logging.getLogger(__name__)

AZURE_OPENAI_TIMEOUT_SECONDS = 180.0
AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS = 15.0
AZURE_OPENAI_WRITE_TIMEOUT_SECONDS = 30.0
AZURE_OPENAI_RETRIES = 2


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
        self._endpoint = (endpoint or settings.azure_openai_endpoint or "").rstrip("/")
        self._api_key = api_key or settings.azure_openai_api_key
        self._api_version = api_version or settings.azure_openai_api_version
        self._gpt5_deployment = gpt5_deployment or settings.azure_openai_gpt5_deployment
        self._gpt5mini_deployment = gpt5mini_deployment or settings.azure_openai_gpt5mini_deployment
        self._embedding_deployment = embedding_deployment or settings.azure_openai_embedding_deployment

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key)

    async def invoke_text(self, prompt: str, *, task: str = "default", cost_tracker=None) -> str:
        """
        Invoke a chat/completions model and return plain text.

        Behavior:
        - retries transport failures in _post_chat_completion()
        - retries empty assistant content once with a stricter prompt and lower reasoning effort
        - reduces completion budget on retry to avoid spending everything in reasoning
        """
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.", code="MODEL_NOT_CONFIGURED")

        model_alias = self._resolve_model_for_task(task)

        body = await self._call_chat_completion(
            prompt=prompt,
            task=task,
            model_alias=model_alias,
        )
        text = self._extract_text_from_chat_response(body)

        if not text or not text.strip():
            logger.warning(
                "sk_adapter.empty_text_response task=%s model=%s raw_preview=%s",
                task,
                model_alias,
                str(body)[:2000].replace("\n", "\\n"),
            )

            finish_reason = self._extract_finish_reason(body)
            strict_prompt = self._make_strict_retry_prompt(prompt, task=task)

            retry_body = await self._call_chat_completion(
                prompt=strict_prompt,
                task=task,
                model_alias=model_alias,
                reasoning_effort_override="low",
                max_completion_tokens_override=self._retry_completion_budget(task),
            )
            retry_text = self._extract_text_from_chat_response(retry_body)

            if retry_text and retry_text.strip():
                body = retry_body
                text = retry_text
            else:
                logger.error(
                    "sk_adapter.empty_text_response_after_retry task=%s model=%s raw_preview=%s",
                    task,
                    model_alias,
                    str(retry_body)[:2000].replace("\n", "\\n"),
                )

                final_finish_reason = self._extract_finish_reason(retry_body) or finish_reason
                if final_finish_reason == "length":
                    raise GenerationException(
                        "Model exhausted completion budget without producing visible content.",
                        code="MODEL_RESPONSE_TRUNCATED",
                    )

                raise GenerationException(
                    "Model response is empty.",
                    code="INVALID_JSON_RESPONSE",
                )

        self._track_usage(
            cost_tracker,
            model_alias,
            task,
            body,
            prompt=prompt,
            output_text=text,
        )
        return text.strip()

    async def invoke_json(
        self,
        prompt: str,
        *,
        task: str,
        cost_tracker: Any | None = None,
    ) -> dict[str, Any]:
        """
        Invoke a chat model and parse the returned text as JSON object.
        """
        text = await self.invoke_text(prompt, task=task, cost_tracker=cost_tracker)

        logger.debug(
            "sk_adapter.invoke_json.raw_preview task=%s preview=%s",
            task,
            (text[:1200].replace("\n", "\\n") if isinstance(text, str) else str(text)[:1200]),
        )

        parsed = self._parse_json_payload(text)
        if not isinstance(parsed, dict):
            raise GenerationException(
                "Model returned non-object JSON payload.",
                code="JSON_OBJECT_REQUIRED",
            )

        return parsed

    async def generate_embedding(self, text: str) -> list[float]:
        result = await self.generate_embedding_with_usage(text)
        return result.embedding

    async def generate_embedding_with_usage(self, text: str) -> EmbeddingUsageResult:
        """
        Generate an embedding vector and return vector + prompt token usage.
        """
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.", code="MODEL_NOT_CONFIGURED")

        if not self._embedding_deployment:
            raise GenerationException(
                "Embedding deployment is not configured.",
                code="EMBEDDING_MODEL_NOT_CONFIGURED",
            )

        url = (
            f"{self._endpoint}/openai/deployments/{self._embedding_deployment}/embeddings"
            f"?api-version={self._api_version}"
        )
        headers = {"api-key": self._api_key}
        payload = {"input": text}

        timeout = httpx.Timeout(
            timeout=AZURE_OPENAI_TIMEOUT_SECONDS,
            connect=AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS,
            write=AZURE_OPENAI_WRITE_TIMEOUT_SECONDS,
            read=AZURE_OPENAI_TIMEOUT_SECONDS,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        data = body.get("data") or []
        if not data or not isinstance(data, list):
            raise GenerationException(
                "Embedding response missing data field.",
                code="EMBEDDING_RESPONSE_INVALID",
            )

        embedding = data[0].get("embedding")
        if not isinstance(embedding, list):
            raise GenerationException(
                "Embedding response missing vector.",
                code="EMBEDDING_VECTOR_MISSING",
            )

        vector = [float(v) for v in embedding]
        usage = body.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        if prompt_tokens <= 0:
            prompt_tokens = count_tokens(text)

        return EmbeddingUsageResult(embedding=vector, prompt_tokens=prompt_tokens)

    async def _call_chat_completion(
        self,
        *,
        prompt: str,
        task: str,
        model_alias: str,
        reasoning_effort_override: str | None = None,
        max_completion_tokens_override: int | None = None,
    ) -> dict[str, Any]:
        deployment = self._deployment_for_model(model_alias)

        payload: dict[str, Any] = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }

        max_completion_tokens = (
            max_completion_tokens_override
            if max_completion_tokens_override is not None
            else TASK_TO_MAX_COMPLETION_TOKENS.get(task)
        )
        if max_completion_tokens:
            payload["max_completion_tokens"] = max_completion_tokens

        reasoning_effort = reasoning_effort_override or TASK_TO_REASONING_EFFORT.get(task)
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort

        return await self._post_chat_completion(deployment, payload, task=task)

    async def _post_chat_completion(
        self,
        deployment: str,
        payload: dict[str, Any],
        *,
        task: str,
    ) -> dict[str, Any]:
        url = f"{self._endpoint}/openai/deployments/{deployment}/chat/completions?api-version={self._api_version}"
        headers = {"api-key": self._api_key}

        timeout = httpx.Timeout(
            timeout=AZURE_OPENAI_TIMEOUT_SECONDS,
            connect=AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS,
            write=AZURE_OPENAI_WRITE_TIMEOUT_SECONDS,
            read=AZURE_OPENAI_TIMEOUT_SECONDS,
        )

        last_error: Exception | None = None

        for attempt in range(1, AZURE_OPENAI_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()

            except httpx.ReadTimeout as exc:
                last_error = exc
                logger.warning(
                    "sk_adapter.chat_timeout task=%s deployment=%s attempt=%s",
                    task,
                    deployment,
                    attempt,
                )
                if attempt >= AZURE_OPENAI_RETRIES:
                    raise GenerationException(
                        f"Azure OpenAI request timed out for task {task}.",
                        code="MODEL_TIMEOUT",
                    ) from exc

            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    "sk_adapter.chat_request_error task=%s deployment=%s attempt=%s detail=%s",
                    task,
                    deployment,
                    attempt,
                    str(exc),
                )
                if attempt >= AZURE_OPENAI_RETRIES:
                    raise GenerationException(
                        f"Azure OpenAI request failed for task {task}: {exc}",
                        code="MODEL_REQUEST_ERROR",
                    ) from exc

            except httpx.HTTPStatusError as exc:
                body_preview = exc.response.text[:2000] if exc.response is not None else ""
                raise GenerationException(
                    f"Azure OpenAI returned status {exc.response.status_code if exc.response else 'unknown'} "
                    f"for task {task}: {body_preview}",
                    code="MODEL_HTTP_ERROR",
                ) from exc

        raise GenerationException(
            f"Azure OpenAI request failed for task {task}: {last_error}",
            code="MODEL_REQUEST_ERROR",
        )

    def _deployment_for_model(self, model_alias: str) -> str:
        """
        Resolve model alias or deployment-like value into an Azure deployment name.
        """
        normalized = self._normalize_model_alias(model_alias)

        if normalized == "gpt5":
            if not self._gpt5_deployment:
                raise GenerationException(
                    "GPT-5 deployment is not configured.",
                    code="MODEL_NOT_CONFIGURED",
                )
            return self._gpt5_deployment

        if normalized == "gpt5mini":
            if not self._gpt5mini_deployment:
                raise GenerationException(
                    "GPT-5-mini deployment is not configured.",
                    code="MODEL_NOT_CONFIGURED",
                )
            return self._gpt5mini_deployment

        # If TASK_TO_MODEL stores an actual deployment name, allow it.
        if isinstance(model_alias, str) and model_alias.strip():
            return model_alias.strip()

        raise GenerationException(
            f"Unsupported model alias: {model_alias}",
            code="UNSUPPORTED_MODEL_ALIAS",
        )

    def _resolve_model_for_task(self, task: str | None) -> str:
        """
        Resolve which model alias to use for a given task.
        Strategy:
        1. Use TASK_TO_MODEL if defined.
        2. Prefer gpt5mini.
        3. Fallback to gpt5.
        """
        normalized_task = (task or "").strip().lower()
        model_alias = TASK_TO_MODEL.get(normalized_task)
        if isinstance(model_alias, str) and model_alias.strip():
            return model_alias.strip()

        if self._gpt5mini_deployment:
            return "gpt-5-mini"
        if self._gpt5_deployment:
            return "gpt-5"

        raise GenerationException(
            "Azure OpenAI deployment is not configured.",
            code="MODEL_NOT_CONFIGURED",
        )

    def _normalize_model_alias(self, value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"[\s_\-]", "", value.strip().lower())

    def _extract_text_from_chat_response(self, body: dict) -> str:
        """
        Extract assistant text from a chat completion response body.

        Supports:
        - choices[0].message.content as plain string
        - choices[0].message.content as structured list of parts
        - fallback to choices[0].text
        """
        if not isinstance(body, dict):
            return ""

        choices = body.get("choices") or []
        if not choices:
            return ""

        first = choices[0] or {}

        message = first.get("message") or {}
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    if isinstance(item.get("text"), str):
                        parts.append(item["text"])
                    elif item.get("type") == "text" and isinstance(item.get("content"), str):
                        parts.append(item["content"])
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts).strip()

        text = first.get("text")
        if isinstance(text, str):
            return text

        return ""

    def _extract_finish_reason(self, body: dict[str, Any]) -> str | None:
        if not isinstance(body, dict):
            return None
        choices = body.get("choices") or []
        if not choices:
            return None
        first = choices[0] or {}
        reason = first.get("finish_reason")
        return str(reason) if isinstance(reason, str) else None

    def _extract_text(self, body: dict[str, Any]) -> str:
        """
        Backward-compatible alias for any older callers.
        """
        text = self._extract_text_from_chat_response(body)
        if text:
            return text

        raise GenerationException(
            "Completion response missing text content.",
            code="COMPLETION_TEXT_MISSING",
        )

    def _parse_json_payload(self, text: str) -> dict[str, Any]:
        """
        Parse model output into a JSON object.

        Tolerates:
        - fenced code blocks
        - leading/trailing explanatory text
        - smart quotes
        - trailing commas before } or ]
        """
        raw = (text or "").strip()
        if not raw:
            raise GenerationException("Model response is empty.", code="INVALID_JSON_RESPONSE")

        cleaned = self._coerce_json_candidate(raw)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "sk_adapter.json_parse_failed preview=%s",
                raw[:1200].replace("\n", "\\n"),
            )
            raise GenerationException(
                "Model response is not valid JSON.",
                code="INVALID_JSON_RESPONSE",
            ) from None

        if not isinstance(parsed, dict):
            raise GenerationException(
                "Model response JSON must be an object.",
                code="INVALID_JSON_RESPONSE",
            )

        return parsed

    def _coerce_json_candidate(self, text: str) -> str:
        """
        Convert noisy model output into the most likely JSON candidate.
        """
        candidate = text.strip().lstrip("\ufeff")

        candidate = (
            candidate.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

        fenced = re.search(
            r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```",
            candidate,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced:
            candidate = fenced.group(1).strip()
        else:
            extracted = self._extract_first_json_block(candidate)
            if extracted:
                candidate = extracted

        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        return candidate

    def _extract_first_json_block(self, text: str) -> str | None:
        """
        Find the first balanced JSON object or array in free-form text.
        """
        starts = []
        obj_start = text.find("{")
        arr_start = text.find("[")

        if obj_start != -1:
            starts.append((obj_start, "{", "}"))
        if arr_start != -1:
            starts.append((arr_start, "[", "]"))

        if not starts:
            return None

        start_index, open_ch, close_ch = min(starts, key=lambda x: x[0])

        depth = 0
        in_string = False
        escape = False

        for idx in range(start_index, len(text)):
            ch = text[idx]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue

            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start_index : idx + 1]

        return None

    def _track_usage(
        self,
        cost_tracker: Any,
        model_alias: str,
        task: str,
        response_body: dict[str, Any] | None,
        *,
        prompt: str,
        output_text: str,
    ) -> None:
        """
        Best-effort usage tracking.

        Safe no-op if:
        - cost_tracker is None
        - usage block is missing
        - tracker shape is unsupported
        """
        if cost_tracker is None:
            return

        try:
            usage = response_body.get("usage", {}) if isinstance(response_body, dict) else {}
            prompt_tokens = int(usage.get("prompt_tokens") or 0)
            completion_tokens = int(usage.get("completion_tokens") or 0)
            total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))

            if prompt_tokens <= 0:
                prompt_tokens = count_tokens(prompt or "")
            if completion_tokens <= 0:
                completion_tokens = count_tokens(output_text or "")
            if total_tokens <= 0:
                total_tokens = prompt_tokens + completion_tokens

            event = {
                "task": task,
                "model": model_alias,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "input_chars": len(prompt or ""),
                "output_chars": len(output_text or ""),
            }

            # Current generation tracker path
            track_call = getattr(cost_tracker, "track_call", None)
            if callable(track_call):
                track_call(
                    model=model_alias,
                    task=task,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                )
                return

            # Dict/list compatibility
            if isinstance(cost_tracker, dict):
                cost_tracker.setdefault("calls", []).append(event)
                cost_tracker["call_count"] = int(cost_tracker.get("call_count", 0)) + 1
                cost_tracker["prompt_tokens"] = int(cost_tracker.get("prompt_tokens", 0)) + prompt_tokens
                cost_tracker["completion_tokens"] = int(cost_tracker.get("completion_tokens", 0)) + completion_tokens
                cost_tracker["total_tokens"] = int(cost_tracker.get("total_tokens", 0)) + total_tokens
                return

            if isinstance(cost_tracker, list):
                cost_tracker.append(event)
                return

            add_usage = getattr(cost_tracker, "add_usage", None)
            if callable(add_usage):
                add_usage(
                    task=task,
                    model=model_alias,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    prompt=prompt,
                    output_text=output_text,
                )
                return

        except Exception:
            logger.exception("sk_adapter.track_usage.failed task=%s model=%s", task, model_alias)

    def _make_strict_retry_prompt(self, prompt: str, *, task: str) -> str:
        if task == "template_classification":
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY a valid JSON object.\n"
                "- The JSON MUST contain a top-level key named \"sections\".\n"
                "- Do not include markdown fences.\n"
                "- Do not include commentary or explanations.\n"
            )
        elif "diagram" in task:
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY raw diagram syntax.\n"
                "- Do not include markdown fences.\n"
                "- Do not include explanation text.\n"
                "- If PlantUML is requested, include @startuml and @enduml.\n"
            )
        else:
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY the final answer content.\n"
                "- Do not include explanations before or after the answer.\n"
            )

        return f"{prompt.rstrip()}\n{suffix}"

    def _retry_completion_budget(self, task: str) -> int | None:
        original = TASK_TO_MAX_COMPLETION_TOKENS.get(task)
        if not original:
            return None

        # Retry with a smaller budget to discourage long internal reasoning chains.
        reduced = max(400, int(original * 0.6))
        return reduced
