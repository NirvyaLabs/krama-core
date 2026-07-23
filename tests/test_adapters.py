import asyncio

import pytest

from krama.adapters import (
    AustraliaAdapter,
    IndiaAdapter,
    PatientIdentity,
    UKAdapter,
    USAdapter,
)
from krama.exceptions import ConfigurationError
from krama import KramaClient


def run(coro):
    return asyncio.run(coro)


class FakeABHA:
    async def verify(self, identifier):
        return {
            "abha_number": identifier,
            "name": "Ravi Kumar",
        }


class FakeHIP:
    async def publish(self, bundle):
        assert bundle["resourceType"] == "Bundle"
        return "txn-1"


class FakeConsent:
    async def request(self, patient_id, purpose):
        return {
            "consent_id": "consent-1",
            "status": "REQUESTED",
            "patient_id": patient_id,
            "purpose": purpose,
        }


class FakeHIU:
    def __init__(self):
        self.consent = FakeConsent()


def test_india_adapter_delegates_to_abha_hip_hiu():
    adapter = IndiaAdapter(abha=FakeABHA(), hip=FakeHIP(), hiu=FakeHIU())

    identity = run(adapter.verify_patient_identity({"abha_number": "12345678901234"}))
    transaction_id = run(adapter.publish_health_record({"resourceType": "Bundle"}))
    consent = run(adapter.request_consent("ravi.kumar@abdm", "Care management"))

    assert isinstance(identity, PatientIdentity)
    assert identity.patient_id == "12345678901234"
    assert transaction_id == "txn-1"
    assert consent.consent_id == "consent-1"
    assert adapter.get_drug_formulary() == "indian_pharmacopoeia"
    assert adapter.get_coding_system() == "icd10"
    assert "DPDP Act" in adapter.get_compliance_rules().frameworks
    assert adapter.get_data_residency_region() == "ap-south-1"
    assert adapter.get_supported_patient_identifiers() == [
        "india_abha",
        "india_abha_address",
        "local_mrn",
    ]


def test_australia_stub_metadata_and_not_implemented():
    adapter = AustraliaAdapter()

    assert adapter.get_coding_system() == "icd10_am"
    assert adapter.get_drug_formulary() == "pbs"
    assert adapter.get_data_residency_region() == "ap-southeast-2"
    assert "Privacy Act 1988" in adapter.get_compliance_rules().frameworks
    assert adapter.get_supported_patient_identifiers() == [
        "australia_ihi",
        "australia_mrn",
        "australia_medicare",
    ]
    with pytest.raises(NotImplementedError, match="Australia MHR"):
        run(adapter.verify_patient_identity({}))


def test_us_stub_metadata_and_not_implemented():
    adapter = USAdapter()

    assert adapter.get_coding_system() == "icd10_cm"
    assert adapter.get_drug_formulary() == "fda_ndc"
    assert adapter.get_data_residency_region() == "us-east-1"
    assert "HIPAA" in adapter.get_compliance_rules().frameworks
    assert adapter.get_supported_patient_identifiers() == [
        "us_mrn",
        "us_mbi",
        "local_mrn",
    ]
    with pytest.raises(NotImplementedError, match="US adapter"):
        run(adapter.publish_health_record({}))


def test_uk_stub_metadata_and_not_implemented():
    adapter = UKAdapter()

    assert adapter.get_coding_system() == "icd10"
    assert adapter.get_drug_formulary() == "nhs_dm_d"
    assert adapter.get_data_residency_region() == "eu-west-2"
    assert "UK GDPR" in adapter.get_compliance_rules().frameworks
    assert adapter.get_supported_patient_identifiers() == [
        "uk_nhs_number",
        "uk_mrn",
    ]
    with pytest.raises(NotImplementedError, match="UK NHS"):
        run(adapter.request_consent("9000000009", "Care management"))


def test_krama_client_adapter_selection_by_country_code():
    client = KramaClient(
        client_id="client",
        client_secret="secret",
        base_url="https://abdm.example",
    )

    try:
        assert isinstance(client.adapter("IND"), IndiaAdapter)
        assert isinstance(client.adapter("AU"), AustraliaAdapter)
        assert isinstance(client.adapter("US"), USAdapter)
        assert isinstance(client.adapter("GB"), UKAdapter)
        with pytest.raises(ConfigurationError):
            client.adapter("CA")
    finally:
        run(client.close())
