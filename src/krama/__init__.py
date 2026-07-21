"""Krama Core: Python-first ABDM/FHIR tooling by Nirvya Labs."""

from krama.adapters import (
    AustraliaAdapter,
    ComplianceRules,
    Consent,
    CountryAdapter,
    IndiaAdapter,
    PatientIdentity,
    USAdapter,
)
from krama.ai import AIAssistant
from krama.client import KramaClient
from krama.gateway import CircuitBreaker, CircuitState, GatewayHealthClient, RetryConfig
from krama.templates import ClinicalTemplate, TemplateRegistry, TemplateSection

__version__ = "1.0.0a1"

__all__ = [
    "AIAssistant",
    "AustraliaAdapter",
    "CircuitBreaker",
    "CircuitState",
    "ClinicalTemplate",
    "ComplianceRules",
    "Consent",
    "CountryAdapter",
    "GatewayHealthClient",
    "IndiaAdapter",
    "KramaClient",
    "PatientIdentity",
    "RetryConfig",
    "TemplateRegistry",
    "TemplateSection",
    "USAdapter",
    "__version__",
]
