"""Server-side LLM access. `LLM_PROVIDER` picks self-hosted vLLM or Gemini."""

import logging
from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.settings import Settings, settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class VllmProvider:
    """Any OpenAI-compatible server: vLLM in production, Ollama on a CPU laptop."""

    def __init__(self, config: Settings) -> None:
        self._config = config

    def complete(self, system: str, user: str, temperature: float) -> str:
        headers = {}
        if self._config.vllm_api_key:
            headers["Authorization"] = f"Bearer {self._config.vllm_api_key}"

        response = httpx.post(
            f"{self._config.vllm_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            timeout=self._config.llm_timeout_seconds,
            json={
                "model": self._config.vllm_model,
                "temperature": temperature,
                "max_tokens": 2048,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class GeminiProvider:
    def __init__(self, config: Settings) -> None:
        self._model = config.gemini_model
        self._client = genai.Client(
            api_key=config.gemini_api_key,
            http_options=types.HttpOptions(timeout=int(config.llm_timeout_seconds * 1000)),
        )

    def complete(self, system: str, user: str, temperature: float) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=temperature,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )
        return response.text or ""


def request_json(system: str, prompt: str, temperature: float, model_cls: type[T]) -> T | None:
    """Ask the model for JSON matching `model_cls`; one retry, `None` when it still fails."""
    provider = (
        GeminiProvider(settings) if settings.llm_provider == "gemini" else VllmProvider(settings)
    )
    for attempt in range(2):
        user = prompt if attempt == 0 else f"{prompt}\n\nReply with valid JSON only."
        try:
            return model_cls.model_validate_json(provider.complete(system, user, temperature))
        except (httpx.HTTPError, ValidationError, KeyError, errors.APIError) as error:
            logger.warning("LLM call failed: %s", error)
    return None
