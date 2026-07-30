"""United States adapter placeholder."""

from __future__ import annotations

from typing import Any

from krama.adapters.base import (
    ComplianceRules,
    Consent,
    CountryAdapter,
    PatientIdentity,
)


class USAdapter(CountryAdapter):
    """US adapter metadata; network support arrives in v2.0."""

    country_code = "USA"
    _MESSAGE = "US adapter coming in v2.0"

    async def verify_patient_identity(self, id_data: dict[str, Any]) -> PatientIdentity:
        raise NotImplementedError(self._MESSAGE)

    async def publish_health_record(self, bundle: dict[str, Any]) -> str:
        raise NotImplementedError(self._MESSAGE)

    async def request_consent(self, patient_id: str, purpose: str) -> Consent:
        raise NotImplementedError(self._MESSAGE)

    def get_drug_formulary(self) -> str:
        return "fda_ndc"

    def get_coding_system(self) -> str:
        return "icd10_cm"

    def get_compliance_rules(self) -> ComplianceRules:
        return ComplianceRules(frameworks=["HIPAA"])

    def get_data_residency_region(self) -> str:
        return "us-east-1"

    def get_supported_patient_identifiers(self) -> list[str]:
        return ["us_mrn", "us_mbi", "local_mrn"]
