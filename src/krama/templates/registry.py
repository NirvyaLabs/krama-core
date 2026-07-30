"""Clinical template registry."""

from __future__ import annotations

from collections.abc import Iterable

from krama.exceptions import TemplateNotFoundError
from krama.templates.base import ClinicalTemplate
from krama.templates.universal import (
    UniversalTemplateContext,
    create_universal_template,
)
from krama.templates.validators import TemplateValidator


class TemplateRegistry:
    """Registry of built-in and custom clinical templates."""

    def __init__(self, templates: Iterable[ClinicalTemplate] | None = None) -> None:
        self._templates: dict[str, ClinicalTemplate] = {}
        if templates is None:
            self._load_builtin_templates()
        else:
            for template in templates:
                self.register(template)

    def register(self, template: ClinicalTemplate) -> None:
        TemplateValidator.validate(template)
        self._templates[self._key(template.domain, template.encounter_type)] = template

    def get(self, domain: str, encounter_type: str) -> ClinicalTemplate:
        key = self._key(domain, encounter_type)
        try:
            return self._templates[key]
        except KeyError as exc:
            raise TemplateNotFoundError(f"No clinical template registered for {key}") from exc

    def list_domains(self) -> list[str]:
        return sorted({template.domain for template in self._templates.values()})

    def list_templates(self, domain: str | None = None) -> list[ClinicalTemplate]:
        templates = list(self._templates.values())
        if domain is None:
            return sorted(templates, key=lambda item: (item.domain, item.encounter_type))
        normalized = domain.strip().lower()
        return sorted(
            [template for template in templates if template.domain == normalized],
            key=lambda item: item.encounter_type,
        )

    def universal(self, country: str = "GLOBAL") -> ClinicalTemplate:
        """Return the universal adaptive template for a country."""

        return create_universal_template(UniversalTemplateContext(country=country))

    def _load_builtin_templates(self) -> None:
        from krama.templates.domains import BUILTIN_TEMPLATE_MODULES

        for module in BUILTIN_TEMPLATE_MODULES:
            for template in module.TEMPLATES:
                self.register(template)

    def _key(self, domain: str, encounter_type: str) -> str:
        return f"{domain.strip().lower()}:{encounter_type.strip().lower()}"
