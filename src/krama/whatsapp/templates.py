"""WhatsApp template loading and rendering."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from krama.exceptions import TemplateNotFoundError, ValidationError


_PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


class WhatsAppTemplate(BaseModel):
    """A text template with named placeholders."""

    name: str = Field(min_length=1)
    body: str = Field(min_length=1)
    language: str = "en"

    @property
    def placeholders(self) -> set[str]:
        return set(_PLACEHOLDER_RE.findall(self.body))


class WhatsAppTemplateStore:
    """In-memory template registry and renderer."""

    def __init__(self, templates: list[WhatsAppTemplate] | None = None) -> None:
        self._templates: dict[str, WhatsAppTemplate] = {}
        for template in templates or []:
            self.register(template)

    def register(self, template: WhatsAppTemplate) -> None:
        self.validate(template)
        self._templates[template.name] = template

    def get(self, name: str) -> WhatsAppTemplate:
        try:
            return self._templates[name]
        except KeyError as exc:
            raise TemplateNotFoundError(f"WhatsApp template not found: {name}") from exc

    def list_templates(self) -> list[str]:
        return sorted(self._templates)

    def render(self, name: str, params: dict[str, object]) -> str:
        template = self.get(name)
        normalized = {key: str(value) for key, value in params.items()}
        missing = template.placeholders - normalized.keys()
        if missing:
            missing_names = ", ".join(sorted(missing))
            raise ValidationError(f"Missing template params: {missing_names}")

        return _PLACEHOLDER_RE.sub(
            lambda match: normalized[match.group(1)],
            template.body,
        )

    def validate(self, template: WhatsAppTemplate) -> None:
        if "{{" in template.body and "}}" not in template.body:
            raise ValidationError("Template placeholder is not closed")
        for placeholder in template.placeholders:
            if not placeholder.strip():
                raise ValidationError("Template placeholder cannot be empty")
