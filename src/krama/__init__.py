"""Krama Core: Python-first ABDM/FHIR tooling by Nirvya Labs."""

from krama.adapters import (
    AustraliaAdapter,
    ComplianceRules,
    Consent,
    CountryAdapter,
    IndiaAdapter,
    PatientIdentity,
    UKAdapter,
    USAdapter,
)
from krama.ai import AIAssistant
from krama.client import KramaClient
from krama.compliance import ComplianceContext, ComplianceEngine, ComplianceResult
from krama.fhir import PatientIdentifier, PatientIdentifierType
from krama.gateway import CircuitBreaker, CircuitState, GatewayHealthClient, RetryConfig
from krama.templates import (
    ClinicalTemplate,
    TemplateRegistry,
    TemplateSection,
    UniversalTemplateContext,
    create_universal_template,
)

__version__ = "1.0.0a3"

__all__ = [
    "AIAssistant",
    "AustraliaAdapter",
    "CircuitBreaker",
    "CircuitState",
    "ClinicalTemplate",
    "ComplianceContext",
    "ComplianceEngine",
    "ComplianceResult",
    "ComplianceRules",
    "Consent",
    "CountryAdapter",
    "GatewayHealthClient",
    "IndiaAdapter",
    "KramaClient",
    "PatientIdentity",
    "PatientIdentifier",
    "PatientIdentifierType",
    "RetryConfig",
    "TemplateRegistry",
    "TemplateSection",
    "UKAdapter",
    "USAdapter",
    "UniversalTemplateContext",
    "__version__",
    "create_universal_template",
]
