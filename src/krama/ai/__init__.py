"""Clinical AI helpers."""

from krama.ai.clinical_nlp import ClinicalNLP, SAFETY_DISCLAIMER
from krama.ai.drug_checker import DrugChecker, InteractionResult
from krama.ai.icd_coder import ICDCoder, ICDSuggestion
from krama.ai.providers.base import LLMProvider
from krama.ai.providers.gemini import GeminiProvider
from krama.ai.providers.groq import GroqProvider
from krama.ai.providers.router import LLMRouter
from krama.ai.triage import TriageClassifier, TriageResult


class AIAssistant:
    """Facade for clinical AI workflows."""

    def __init__(self, router: LLMRouter | None = None) -> None:
        self.router = router
        self.clinical_nlp = ClinicalNLP(router)
        self.icd_coder = ICDCoder(router)
        self.drug_checker = DrugChecker()
        self.triage = TriageClassifier(router)


__all__ = [
    "AIAssistant",
    "ClinicalNLP",
    "DrugChecker",
    "GeminiProvider",
    "GroqProvider",
    "ICDCoder",
    "ICDSuggestion",
    "InteractionResult",
    "LLMProvider",
    "LLMRouter",
    "SAFETY_DISCLAIMER",
    "TriageClassifier",
    "TriageResult",
]
