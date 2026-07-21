"""Abstract LLM provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Provider-neutral async LLM interface."""

    name: str = "llm"

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text for a prompt."""
