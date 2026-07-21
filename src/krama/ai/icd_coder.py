"""ICD-10 coding suggestions."""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field

from krama.ai.clinical_nlp import SAFETY_DISCLAIMER
from krama.ai.providers.router import LLMRouter


class ICDSuggestion(BaseModel):
    """Suggested ICD code with confidence."""

    code: str = Field(min_length=1)
    display: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    disclaimer: str = SAFETY_DISCLAIMER


class ICDCoder:
    """Suggest ICD-10 codes from assessment text."""

    def __init__(self, router: LLMRouter | None = None) -> None:
        self._router = router

    async def suggest_codes(self, assessment_text: str) -> list[ICDSuggestion]:
        if self._router is None:
            return []

        response = await self._router.generate(
            "Suggest ICD-10 codes as JSON array with code, display, confidence "
            f"for this assessment: {assessment_text}",
            "Return only coding suggestions. Physician review is required.",
        )
        return _parse_suggestions(response)


def _parse_suggestions(response: str) -> list[ICDSuggestion]:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return _parse_line_suggestions(response)

    if not isinstance(parsed, list):
        return []
    suggestions: list[ICDSuggestion] = []
    for item in parsed:
        if isinstance(item, dict):
            suggestions.append(ICDSuggestion(**item))
    return suggestions


def _parse_line_suggestions(response: str) -> list[ICDSuggestion]:
    suggestions: list[ICDSuggestion] = []
    pattern = re.compile(r"(?P<code>[A-Z][0-9][A-Z0-9.]+)\s*[-|:]\s*(?P<display>.+)")
    for line in response.splitlines():
        match = pattern.search(line.strip())
        if match:
            suggestions.append(
                ICDSuggestion(
                    code=match.group("code"),
                    display=match.group("display").strip(),
                    confidence=0.5,
                )
            )
    return suggestions
