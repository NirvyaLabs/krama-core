"""Clinical NLP helpers."""

from __future__ import annotations

from krama.ai.providers.router import LLMRouter

SAFETY_DISCLAIMER = (
    "AI output is a clinical suggestion only and requires physician review."
)


class ClinicalNLP:
    """Assist with SOAP quality and patient-friendly summaries."""

    def __init__(self, router: LLMRouter | None = None) -> None:
        self._router = router

    async def suggest_soap_improvement(self, section_name: str, text: str) -> list[str]:
        prompt = (
            "Suggest concise clinical improvements or missing details for this "
            f"SOAP section.\nSection: {section_name}\nText: {text}"
        )
        response = await self._generate(prompt)
        suggestions = _split_suggestions(response)
        return suggestions + [SAFETY_DISCLAIMER]

    async def generate_encounter_summary(self, soap_dict: dict[str, str]) -> str:
        soap_text = "\n".join(f"{key}: {value}" for key, value in soap_dict.items())
        prompt = (
            "Write a patient-friendly encounter summary in plain language. "
            f"Keep it short and clinically careful.\n{soap_text}"
        )
        response = await self._generate(prompt)
        return f"{response.strip()}\n\n{SAFETY_DISCLAIMER}"

    async def _generate(self, prompt: str) -> str:
        if self._router is None:
            return "Review completeness, red flags, diagnosis clarity, and follow-up plan."
        return await self._router.generate(prompt, _clinical_system_prompt())


def _split_suggestions(response: str) -> list[str]:
    suggestions: list[str] = []
    for line in response.splitlines():
        cleaned = line.strip(" -\t")
        if cleaned:
            suggestions.append(cleaned)
    return suggestions or [response.strip()]


def _clinical_system_prompt() -> str:
    return (
        "You are a cautious clinical documentation assistant. Never diagnose "
        "independently. State uncertainty and require physician review."
    )
