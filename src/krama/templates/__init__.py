"""Clinical domain templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection
from krama.templates.registry import TemplateRegistry
from krama.templates.universal import (
    UniversalClinicalTemplateBuilder,
    UniversalTemplateContext,
    create_universal_template,
)

__all__ = [
    "ClinicalTemplate",
    "TemplateRegistry",
    "TemplateSection",
    "UniversalClinicalTemplateBuilder",
    "UniversalTemplateContext",
    "create_universal_template",
]
