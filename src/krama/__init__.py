"""Krama Core: Python-first ABDM/FHIR tooling by Nirvya Labs."""

from krama.client import KramaClient
from krama.templates import ClinicalTemplate, TemplateRegistry, TemplateSection

__version__ = "0.5.0"

__all__ = [
    "ClinicalTemplate",
    "KramaClient",
    "TemplateRegistry",
    "TemplateSection",
    "__version__",
]
