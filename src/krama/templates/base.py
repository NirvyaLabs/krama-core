"""Clinical template data models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

SECTION_TYPES = {
    "text",
    "textarea",
    "dental_chart",
    "dosha_assessment",
    "checklist",
    "select",
    "radio",
    "procedure_list",
    "number",
    "date",
    "vital_group",
    "imaging_review",
}


class TemplateSection(BaseModel):
    """A single field or field group in a clinical encounter form."""

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1)
    type: str
    required: bool = False
    ai_assist: bool = False
    icd_coding: bool = False
    rx_link: bool = False
    options: list[str] | None = None
    items: list[str] | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        section_type = value.strip().lower()
        if section_type not in SECTION_TYPES:
            allowed = ", ".join(sorted(SECTION_TYPES))
            raise ValueError(f"section type must be one of {allowed}")
        return section_type

    @model_validator(mode="after")
    def validate_options_and_items(self) -> "TemplateSection":
        if self.type in {"select", "radio", "dosha_assessment"} and not self.options:
            raise ValueError(f"{self.type} sections require options")
        if self.type == "checklist" and not self.items:
            raise ValueError("checklist sections require items")
        return self


class ClinicalTemplate(BaseModel):
    """A complete clinical encounter template for a medical domain."""

    domain: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    encounter_type: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    sections: list[TemplateSection] = Field(min_length=1)
    vitals: list[str] = Field(default_factory=list)
    coding_system: str = Field(min_length=1)
    prescription_type: str = Field(min_length=1)
    jurisdiction: str = "GLOBAL"
    metadata: dict[str, str | list[str]] = Field(default_factory=dict)

    @field_validator("domain", "encounter_type", "coding_system", "prescription_type")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("vitals")
    @classmethod
    def normalize_vitals(cls, value: list[str]) -> list[str]:
        return [item.strip().lower() for item in value]

    @field_validator("jurisdiction")
    @classmethod
    def normalize_jurisdiction(cls, value: str) -> str:
        return value.strip().upper() or "GLOBAL"

    @model_validator(mode="after")
    def validate_unique_sections(self) -> "ClinicalTemplate":
        section_ids = [section.id for section in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("template section ids must be unique")
        return self
