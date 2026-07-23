"""Compliance data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


COMPLIANCE_DISCLAIMER = (
    "Compliance checks are implementation guardrails only and do not replace "
    "legal, privacy, security, or clinical governance review."
)


class ComplianceSeverity(str, Enum):
    """Compliance finding severity."""

    BLOCKER = "blocker"
    WARNING = "warning"


class ComplianceFinding(BaseModel):
    """A single compliance issue or advisory."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    framework: str = Field(min_length=1)
    severity: ComplianceSeverity


class ComplianceContext(BaseModel):
    """Workflow facts evaluated by the compliance engine."""

    country: str = "GLOBAL"
    purpose: str = ""
    patient_identifiers: list[str] = Field(default_factory=list)
    consent_present: bool = False
    lawful_basis: str = ""
    encrypted: bool = False
    data_residency_region: str = ""
    requested_fields: list[str] = Field(default_factory=list)
    necessary_fields: list[str] = Field(default_factory=list)
    actor_id: str = ""
    audit_event_id: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)

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

    @field_validator(
        "patient_identifiers",
        "requested_fields",
        "necessary_fields",
    )
    @classmethod
    def normalize_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ComplianceResult(BaseModel):
    """Country compliance evaluation result."""

    country: str
    frameworks: list[str]
    passed: bool
    blockers: list[ComplianceFinding] = Field(default_factory=list)
    warnings: list[ComplianceFinding] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    disclaimer: str = COMPLIANCE_DISCLAIMER
