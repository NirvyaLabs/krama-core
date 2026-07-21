"""Validation helpers for clinical templates."""

from __future__ import annotations

from krama.exceptions import ValidationError
from krama.templates.base import ClinicalTemplate


class TemplateValidator:
    """Validate template structure before registry insertion."""

    @staticmethod
    def validate(template: ClinicalTemplate) -> None:
        if not template.sections:
            raise ValidationError("template must include at least one section")
        if not any(section.required for section in template.sections):
            raise ValidationError("template must include at least one required section")
        if not template.coding_system:
            raise ValidationError("template must define a coding_system")
        if not template.prescription_type:
            raise ValidationError("template must define a prescription_type")
