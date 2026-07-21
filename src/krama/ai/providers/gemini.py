"""Google Gemini provider."""

from __future__ import annotations

import asyncio
from typing import Any

from krama.ai.providers.base import LLMProvider
from krama.exceptions import ProviderUnavailableError


class GeminiProvider(LLMProvider):
    """Adapter for the optional google-generativeai SDK."""

    name = "gemini"

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gemini-1.5-flash",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = client

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        client = self._client or self._build_client()
        full_prompt = f"{system_prompt}\n\n{prompt}".strip()

        def _call() -> str:
            response = client.generate_content(full_prompt)
            return str(getattr(response, "text", "") or "")

        return await asyncio.to_thread(_call)

    def _build_client(self) -> Any:
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ProviderUnavailableError(
                "google-generativeai is required for GeminiProvider"
            ) from exc

        genai.configure(api_key=self.api_key)
        self._client = genai.GenerativeModel(self.model)
        return self._client
