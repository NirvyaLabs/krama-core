import asyncio

import pytest

from krama.ai import AIAssistant, SAFETY_DISCLAIMER
from krama.ai.drug_checker import DrugChecker, InteractionResult
from krama.ai.icd_coder import ICDCoder
from krama.ai.providers.base import LLMProvider
from krama.ai.providers.router import LLMRouter
from krama.ai.triage import TriageClassifier, Urgency
from krama.exceptions import ProviderUnavailableError


def run(coro):
    return asyncio.run(coro)


class FakeProvider(LLMProvider):
    def __init__(self, name, responses):
        self.name = name
        self.responses = list(responses)

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_router_failover_returns_first_successful_response():
    router = LLMRouter(
        [
            FakeProvider("gemini", [RuntimeError("down")]),
            FakeProvider("groq", ["clinical response"]),
        ]
    )

    assert run(router.generate("prompt")) == "clinical response"


def test_router_raises_when_all_providers_fail():
    router = LLMRouter(
        [
            FakeProvider("gemini", [RuntimeError("down")]),
            FakeProvider("groq", [RuntimeError("also down")]),
        ]
    )

    with pytest.raises(ProviderUnavailableError):
        run(router.generate("prompt"))


def test_clinical_nlp_functions_include_safety_disclaimer():
    router = LLMRouter(
        [
            FakeProvider(
                "mock",
                [
                    "- Add duration of fever\n- Document red flags",
                    "Ravi was seen for fever and given a follow-up plan.",
                ],
            )
        ]
    )
    assistant = AIAssistant(router)

    suggestions = run(
        assistant.clinical_nlp.suggest_soap_improvement("subjective", "Fever")
    )
    summary = run(
        assistant.clinical_nlp.generate_encounter_summary(
            {"assessment": "viral fever", "plan": "fluids"}
        )
    )

    assert "Add duration of fever" in suggestions
    assert suggestions[-1] == SAFETY_DISCLAIMER
    assert SAFETY_DISCLAIMER in summary


def test_icd_coder_parses_mocked_llm_response_with_disclaimer():
    router = LLMRouter(
        [
            FakeProvider(
                "mock",
                ['[{"code": "I10", "display": "Essential hypertension", "confidence": 0.91}]'],
            )
        ]
    )

    suggestions = run(ICDCoder(router).suggest_codes("Essential hypertension"))

    assert suggestions[0].code == "I10"
    assert suggestions[0].confidence == 0.91
    assert suggestions[0].disclaimer == SAFETY_DISCLAIMER


def test_interaction_result_model_and_checker_blockers():
    result = DrugChecker().check_interactions(
        medications=["Amoxicillin", "Warfarin", "Aspirin"],
        patient_allergies=["amoxicillin"],
    )

    assert isinstance(result, InteractionResult)
    assert result.passed is False
    assert result.blockers
    assert result.warnings
    assert result.disclaimer == SAFETY_DISCLAIMER


def test_triage_classifier_parses_llm_response_and_disclaimer():
    router = LLMRouter(
        [
            FakeProvider(
                "mock",
                [
                    (
                        '{"urgency": "urgent", "reasoning": "Persistent fever", '
                        '"recommended_action": "Same-day review"}'
                    )
                ],
            )
        ]
    )

    result = run(TriageClassifier(router).classify_urgency("Persistent fever"))

    assert result.urgency == Urgency.URGENT
    assert result.disclaimer == SAFETY_DISCLAIMER
