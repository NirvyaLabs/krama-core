"""Country-adaptive universal clinical template."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from krama.templates.base import ClinicalTemplate, TemplateSection


COUNTRY_TEMPLATE_DEFAULTS = {
    "IND": {
        "coding_system": "icd10",
        "prescription_type": "standard",
        "identifier_types": ["india_abha", "india_abha_address", "local_mrn"],
        "compliance_frameworks": ["DPDP Act", "DISHA"],
        "data_residency_region": "ap-south-1",
    },
    "AUS": {
        "coding_system": "icd10_am",
        "prescription_type": "standard",
        "identifier_types": ["australia_ihi", "australia_mrn", "australia_medicare"],
        "compliance_frameworks": ["Privacy Act 1988", "Australian Privacy Principles"],
        "data_residency_region": "ap-southeast-2",
    },
    "USA": {
        "coding_system": "icd10_cm",
        "prescription_type": "standard",
        "identifier_types": ["us_mrn", "us_mbi", "local_mrn"],
        "compliance_frameworks": ["HIPAA Privacy Rule", "HIPAA Security Rule"],
        "data_residency_region": "us-east-1",
    },
    "GBR": {
        "coding_system": "icd10",
        "prescription_type": "standard",
        "identifier_types": ["uk_nhs_number", "uk_mrn"],
        "compliance_frameworks": ["UK GDPR", "Data Protection Act 2018"],
        "data_residency_region": "eu-west-2",
    },
}


class UniversalTemplateContext(BaseModel):
    """Inputs used to adapt the universal template for a jurisdiction."""

    country: str = "GLOBAL"
    domain: str = "global"
    encounter_type: str = "adaptive_encounter"
    name: str = "Universal Clinical Encounter"
    description: str = (
        "Country-adaptive clinical encounter template for structured history, "
        "examination, assessment, plan, orders, consent, and follow-up."
    )
    coding_system: str | None = None
    prescription_type: str | None = None
    identifier_types: list[str] = Field(default_factory=list)
    compliance_frameworks: list[str] = Field(default_factory=list)
    data_residency_region: str | None = None

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        normalized = value.strip().upper()
        aliases = {
            "IN": "IND",
            "INDIA": "IND",
            "AU": "AUS",
            "AUSTRALIA": "AUS",
            "US": "USA",
            "UNITED STATES": "USA",
            "UK": "GBR",
            "GB": "GBR",
            "UNITED KINGDOM": "GBR",
        }
        return aliases.get(normalized, normalized or "GLOBAL")


class UniversalClinicalTemplateBuilder:
    """Build one robust template adapted by country metadata."""

    def build(self, context: UniversalTemplateContext | None = None) -> ClinicalTemplate:
        ctx = self._with_country_defaults(context or UniversalTemplateContext())
        return ClinicalTemplate(
            domain=ctx.domain,
            encounter_type=ctx.encounter_type,
            name=ctx.name,
            description=ctx.description,
            jurisdiction=ctx.country,
            sections=_universal_sections(ctx),
            vitals=[
                "bp",
                "heart_rate",
                "respiratory_rate",
                "temperature",
                "spo2",
                "weight",
                "height",
                "pain_score",
            ],
            coding_system=ctx.coding_system or "icd10",
            prescription_type=ctx.prescription_type or "standard",
            metadata={
                "identifier_types": ctx.identifier_types,
                "compliance_frameworks": ctx.compliance_frameworks,
                "data_residency_region": ctx.data_residency_region or "",
            },
        )

    def _with_country_defaults(
        self,
        context: UniversalTemplateContext,
    ) -> UniversalTemplateContext:
        defaults = COUNTRY_TEMPLATE_DEFAULTS.get(context.country, {})
        return context.model_copy(
            update={
                "coding_system": context.coding_system or defaults.get("coding_system"),
                "prescription_type": (
                    context.prescription_type or defaults.get("prescription_type")
                ),
                "identifier_types": (
                    context.identifier_types
                    or list(defaults.get("identifier_types", ["local_mrn"]))
                ),
                "compliance_frameworks": (
                    context.compliance_frameworks
                    or list(defaults.get("compliance_frameworks", []))
                ),
                "data_residency_region": (
                    context.data_residency_region
                    or defaults.get("data_residency_region")
                ),
            }
        )


def create_universal_template(
    context: UniversalTemplateContext | None = None,
) -> ClinicalTemplate:
    """Create a country-adaptive universal clinical template."""

    return UniversalClinicalTemplateBuilder().build(context)


def _universal_sections(context: UniversalTemplateContext) -> list[TemplateSection]:
    identifier_items = [
        f"Capture at least one supported identifier: {', '.join(context.identifier_types)}",
        "Record assigning authority for local MRNs",
        "Confirm patient demographics before clinical documentation",
    ]
    compliance_items = [
        "Record purpose of use",
        "Confirm consent or lawful basis where required",
        "Limit data captured/shared to the minimum necessary for the purpose",
        "Use encrypted transport/storage for health data",
        f"Route data to residency region: {context.data_residency_region or 'configured'}",
    ]

    return [
        TemplateSection(
            id="patient_identity",
            label="Patient Identity",
            type="checklist",
            required=True,
            items=identifier_items,
        ),
        TemplateSection(
            id="chief_complaint",
            label="Chief Complaint",
            type="textarea",
            required=True,
            ai_assist=True,
        ),
        TemplateSection(
            id="history",
            label="History",
            type="textarea",
            required=True,
            ai_assist=True,
        ),
        TemplateSection(
            id="vitals",
            label="Vitals",
            type="vital_group",
            required=True,
        ),
        TemplateSection(
            id="examination",
            label="Clinical Examination",
            type="textarea",
            ai_assist=True,
        ),
        TemplateSection(
            id="assessment",
            label="Assessment",
            type="textarea",
            required=True,
            ai_assist=True,
            icd_coding=True,
        ),
        TemplateSection(
            id="plan",
            label="Plan",
            type="textarea",
            required=True,
            ai_assist=True,
        ),
        TemplateSection(
            id="medications",
            label="Medications",
            type="procedure_list",
            rx_link=True,
        ),
        TemplateSection(
            id="allergies",
            label="Allergies And Alerts",
            type="textarea",
        ),
        TemplateSection(
            id="orders",
            label="Diagnostics And Referrals",
            type="procedure_list",
        ),
        TemplateSection(
            id="follow_up",
            label="Follow-up",
            type="textarea",
            required=True,
        ),
        TemplateSection(
            id="compliance",
            label="Compliance Checklist",
            type="checklist",
            required=True,
            items=compliance_items,
        ),
    ]
