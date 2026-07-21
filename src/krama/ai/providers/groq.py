"""Groq LLM provider."""

from __future__ import annotations

from typing import Any

from krama.ai.providers.base import LLMProvider
from krama.exceptions import ProviderUnavailableError


class GroqProvider(LLMProvider):
    """Adapter for the optional groq SDK."""

    name = "groq"

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "llama-3.3-70b-versatile",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = client

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        client = self._client or self._build_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return str(response.choices[0].message.content or "")

    def _build_client(self) -> Any:
        try:
            from groq import AsyncGroq
        except ImportError as exc:
            raise ProviderUnavailableError("groq is required for GroqProvider") from exc

        self._client = AsyncGroq(api_key=self.api_key)
        return self._client
