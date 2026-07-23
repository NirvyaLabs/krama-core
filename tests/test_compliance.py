from krama.compliance import (
    ComplianceContext,
    ComplianceEngine,
    ComplianceSeverity,
    get_policy,
)


def test_compliance_engine_passes_complete_india_context():
    result = ComplianceEngine().evaluate(
        ComplianceContext(
            country="IND",
            purpose="Care management",
            patient_identifiers=["india_abha_address"],
            consent_present=True,
            encrypted=True,
            data_residency_region="ap-south-1",
            requested_fields=["diagnosis", "medications"],
            necessary_fields=["diagnosis", "medications"],
            actor_id="doctor-1",
            audit_event_id="audit-1",
        )
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.warnings == []
    assert "DPDP Act" in result.frameworks


def test_compliance_engine_blocks_missing_required_safety_controls():
    result = ComplianceEngine().evaluate(ComplianceContext(country="AUS"))

    codes = {finding.code for finding in result.blockers}

    assert result.passed is False
    assert codes == {
        "patient_identifier_required",
        "purpose_required",
        "consent_or_lawful_basis_required",
        "encryption_required",
    }
    assert result.warnings[0].code == "audit_trail_recommended"


def test_us_minimum_necessary_violation_is_blocker():
    result = ComplianceEngine().evaluate(
        ComplianceContext(
            country="US",
            purpose="Referral",
            patient_identifiers=["us_mrn"],
            lawful_basis="treatment",
            encrypted=True,
            requested_fields=["diagnosis", "medications", "full_record"],
            necessary_fields=["diagnosis", "medications"],
            actor_id="clinician-1",
            audit_event_id="audit-1",
        )
    )

    finding = result.blockers[0]

    assert result.passed is False
    assert finding.code == "minimum_necessary"
    assert finding.severity == ComplianceSeverity.BLOCKER


def test_non_us_minimum_necessary_violation_is_warning():
    result = ComplianceEngine().evaluate(
        ComplianceContext(
            country="UK",
            purpose="Care coordination",
            patient_identifiers=["uk_nhs_number"],
            lawful_basis="direct care",
            encrypted=True,
            requested_fields=["diagnosis", "medications", "full_record"],
            necessary_fields=["diagnosis", "medications"],
            actor_id="clinician-1",
            audit_event_id="audit-1",
        )
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.warnings[0].code == "minimum_necessary"


def test_data_residency_mismatch_is_warning():
    result = ComplianceEngine().evaluate(
        ComplianceContext(
            country="AUS",
            purpose="Care",
            patient_identifiers=["australia_ihi"],
            consent_present=True,
            encrypted=True,
            data_residency_region="us-east-1",
            actor_id="doctor-1",
            audit_event_id="audit-1",
        )
    )

    assert result.passed is True
    assert result.warnings[0].code == "data_residency_mismatch"


def test_unsupported_country_identifier_is_blocked():
    result = ComplianceEngine().evaluate(
        ComplianceContext(
            country="AUS",
            purpose="Dental review",
            patient_identifiers=["us_mrn"],
            consent_present=True,
            encrypted=True,
            data_residency_region="ap-southeast-2",
            actor_id="dentist-1",
            audit_event_id="audit-1",
        )
    )

    assert result.passed is False
    assert result.blockers[0].code == "unsupported_patient_identifier"


def test_encryption_is_blocker_for_every_major_country():
    for country, identifier in [
        ("IND", "india_abha_address"),
        ("AUS", "australia_ihi"),
        ("USA", "us_mrn"),
        ("GBR", "uk_nhs_number"),
    ]:
        result = ComplianceEngine().evaluate(
            ComplianceContext(
                country=country,
                purpose="Care",
                patient_identifiers=[identifier],
                consent_present=True,
                encrypted=False,
                actor_id="clinician-1",
                audit_event_id="audit-1",
            )
        )

        assert "encryption_required" in {finding.code for finding in result.blockers}


def test_get_policy_uses_country_aliases_and_global_fallback():
    assert get_policy("UK").country == "GBR"
    assert get_policy("Australia").country == "AUS"
    assert get_policy("BR").country == "BR"
    assert get_policy("BR").frameworks == ["FHIR", "Local healthcare privacy law"]


def test_major_country_policies_have_sources_and_identifier_rules():
    for country in ["IND", "AUS", "USA", "GBR"]:
        policy = get_policy(country)

        assert policy.source_urls
        assert policy.required_identifier_types
        assert policy.encryption_required is True
