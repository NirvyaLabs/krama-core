"""Country-specific healthcare adapters."""

from krama.adapters.australia import AustraliaAdapter
from krama.adapters.base import (
    ComplianceRules,
    Consent,
    CountryAdapter,
    PatientIdentity,
)
from krama.adapters.india import IndiaAdapter
from krama.adapters.uk import UKAdapter
from krama.adapters.us import USAdapter

__all__ = [
    "AustraliaAdapter",
    "ComplianceRules",
    "Consent",
    "CountryAdapter",
    "IndiaAdapter",
    "PatientIdentity",
    "UKAdapter",
    "USAdapter",
]
