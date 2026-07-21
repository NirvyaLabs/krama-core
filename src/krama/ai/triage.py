"""Clinical urgency triage."""

from __future__ import annotations

import json
from enum import Enum

from pydantic import BaseModel, Field

from krama.ai.clinical_nlp import SAFETY_DISCLAIMER
from krama.ai.providers.router import LLMRouter


class Urgency(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"


class TriageResult(BaseModel):
    """Suggested care urgency."""

    urgency: Urgency
    reasoning: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)
    disclaimer: str = SAFETY_DISCLAIMER


class TriageClassifier:
    """Classify symptom urgency with optional LLM support."""

    def __init__(self, router: LLMRouter | None = None) -> None:
        self._router = router

    async def classify_urgency(self, symptoms: str) -> TriageResult:
        if self._router is None:
            return _rule_based_triage(symptoms)

        response = await self._router.generate(
            "Classify urgency as emergency, urgent, or routine. Return JSON "
            "with urgency, reasoning, recommended_action. Symptoms: "
            f"{symptoms}",
            "Be conservative. Emergency red flags require immediate escalation.",
        )
        return _parse_triage(response)


def _parse_triage(response: str) -> TriageResult:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return _rule_based_triage(response)
    return TriageResult(**parsed)


def _rule_based_triage(symptoms: str) -> TriageResult:
    lowered = symptoms.lower()
    emergency_terms = {"chest pain", "stroke", "seizure", "unconscious", "breathless"}
    urgent_terms = {"fever", "severe pain", "bleeding", "infection", "dehydration"}

    if any(term in lowered for term in emergency_terms):
        return TriageResult(
            urgency=Urgency.EMERGENCY,
            reasoning="Symptoms include emergency red flags.",
            recommended_action="Seek emergency care immediately.",
        )
    if any(term in lowered for term in urgent_terms):
        return TriageResult(
            urgency=Urgency.URGENT,
            reasoning="Symptoms may need timely clinical assessment.",
            recommended_action="Arrange same-day or next-day clinician review.",
        )
    return TriageResult(
        urgency=Urgency.ROUTINE,
        reasoning="No emergency red flags were identified from the provided text.",
        recommended_action="Book routine follow-up and monitor for worsening symptoms.",
    )
