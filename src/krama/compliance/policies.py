"""Country compliance policy metadata."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.compliance.models import ComplianceSeverity


class CountryCompliancePolicy(BaseModel):
    """Country-specific policy metadata used by the compliance engine."""

    country: str
    frameworks: list[str]
    required_identifier_types: list[str] = Field(default_factory=list)
    data_residency_region: str = ""
    consent_or_lawful_basis_required: bool = True
    encryption_required: bool = True
    minimum_necessary_severity: ComplianceSeverity = ComplianceSeverity.WARNING
    source_urls: list[str] = Field(default_factory=list)


POLICIES: dict[str, CountryCompliancePolicy] = {
    "IND": CountryCompliancePolicy(
        country="IND",
        frameworks=["DPDP Act", "DISHA", "ABDM"],
        required_identifier_types=["india_abha", "india_abha_address", "local_mrn"],
        data_residency_region="ap-south-1",
        source_urls=[
            "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
            "https://nrces.in/ndhm/fhir/r4/",
        ],
    ),
    "AUS": CountryCompliancePolicy(
        country="AUS",
        frameworks=["Privacy Act 1988", "Australian Privacy Principles"],
        required_identifier_types=["australia_ihi", "australia_mrn", "local_mrn"],
        data_residency_region="ap-southeast-2",
        source_urls=[
            "https://www.oaic.gov.au/privacy/privacy-legislation/the-privacy-act",
            "https://www.oaic.gov.au/privacy/your-privacy-rights/health-information",
        ],
    ),
    "USA": CountryCompliancePolicy(
        country="USA",
        frameworks=["HIPAA Privacy Rule", "HIPAA Security Rule"],
        required_identifier_types=["us_mrn", "us_mbi", "local_mrn"],
        data_residency_region="us-east-1",
        minimum_necessary_severity=ComplianceSeverity.BLOCKER,
        source_urls=[
            "https://www.hhs.gov/hipaa/for-professionals/privacy/index.html",
            "https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html",
            "https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html",
        ],
    ),
    "GBR": CountryCompliancePolicy(
        country="GBR",
        frameworks=["UK GDPR", "Data Protection Act 2018", "NHS"],
        required_identifier_types=["uk_nhs_number", "uk_mrn"],
        data_residency_region="eu-west-2",
        source_urls=[
            "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/",
            "https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir",
        ],
    ),
}


DEFAULT_POLICY = CountryCompliancePolicy(
    country="GLOBAL",
    frameworks=["FHIR", "Local healthcare privacy law"],
    required_identifier_types=["local_mrn", "custom"],
)


def get_policy(country: str) -> CountryCompliancePolicy:
    """Return a country compliance policy with conservative global fallback."""

    normalized = _normalize_country(country)
    return POLICIES.get(normalized, DEFAULT_POLICY.model_copy(update={"country": normalized}))


def _normalize_country(country: str) -> str:
    normalized = country.strip().upper()
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
