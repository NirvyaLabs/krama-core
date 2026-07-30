"""LLM provider failover."""

from __future__ import annotations

from collections.abc import Iterable

from krama.ai.providers.base import LLMProvider
from krama.exceptions import ProviderUnavailableError


class LLMRouter:
    """Try providers in priority order and return the first successful response."""

    def __init__(self, providers: Iterable[LLMProvider]) -> None:
        self.providers = list(providers)
        if not self.providers:
            raise ValueError("LLMRouter requires at least one provider")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        errors: list[str] = []
        for provider in self.providers:
            try:
                response = await provider.generate(prompt, system_prompt)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
                continue
            if response.strip():
                return response
            errors.append(f"{provider.name}: empty response")

        details = "; ".join(errors) or "no providers configured"
        raise ProviderUnavailableError(f"All LLM providers failed: {details}")
