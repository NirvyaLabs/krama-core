"""Country adapter interface and shared schemas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class PatientIdentity(BaseModel):
    """Normalized patient identity across national systems."""

    patient_id: str = Field(min_length=1)
    display: str = ""
    verified: bool = True
    raw: dict[str, Any] = Field(default_factory=dict)


class Consent(BaseModel):
    """Normalized consent record."""

    consent_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    raw: dict[str, Any] = Field(default_factory=dict)


class ComplianceRules(BaseModel):
    """Country compliance metadata."""

    frameworks: list[str]
    notes: str = ""


class CountryAdapter(ABC):
    """Interface for country-specific health network integrations."""

    country_code: str

    @abstractmethod
    async def verify_patient_identity(self, id_data: dict[str, Any]) -> PatientIdentity:
        """Verify a patient identity payload."""

    @abstractmethod
    async def publish_health_record(self, bundle: dict[str, Any]) -> str:
        """Publish a health record and return a transaction id."""

    @abstractmethod
    async def request_consent(self, patient_id: str, purpose: str) -> Consent:
        """Request access consent from a patient."""

    @abstractmethod
    def get_drug_formulary(self) -> str:
        """Return the country formulary identifier."""

    @abstractmethod
    def get_coding_system(self) -> str:
        """Return the default diagnosis coding system."""

    @abstractmethod
    def get_compliance_rules(self) -> ComplianceRules:
        """Return applicable compliance frameworks."""

    @abstractmethod
    def get_data_residency_region(self) -> str:
        """Return default cloud data residency region."""
