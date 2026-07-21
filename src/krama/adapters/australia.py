"""Australia My Health Record adapter placeholder."""

from __future__ import annotations

from typing import Any

from krama.adapters.base import ComplianceRules, Consent, CountryAdapter, PatientIdentity


class AustraliaAdapter(CountryAdapter):
    """Australia adapter metadata; network support arrives in v2.0."""

    country_code = "AUS"
    _MESSAGE = "Australia MHR adapter coming in v2.0"

    async def verify_patient_identity(self, id_data: dict[str, Any]) -> PatientIdentity:
        raise NotImplementedError(self._MESSAGE)

    async def publish_health_record(self, bundle: dict[str, Any]) -> str:
        raise NotImplementedError(self._MESSAGE)

    async def request_consent(self, patient_id: str, purpose: str) -> Consent:
        raise NotImplementedError(self._MESSAGE)

    def get_drug_formulary(self) -> str:
        return "pbs"

    def get_coding_system(self) -> str:
        return "icd10_am"

    def get_compliance_rules(self) -> ComplianceRules:
        return ComplianceRules(frameworks=["Privacy Act 1988"])

    def get_data_residency_region(self) -> str:
        return "ap-southeast-2"
