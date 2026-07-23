from krama.compliance import ComplianceContext, ComplianceEngine, get_policy
from krama.fhir.resources import FHIRPatient, PatientIdentifier
from krama.templates import TemplateRegistry


def test_every_clinical_specialisation_can_use_every_major_country_policy():
    registry = TemplateRegistry()
    templates = registry.list_templates()
    engine = ComplianceEngine()

    for template in templates:
        for country in ["IND", "AUS", "USA", "GBR"]:
            policy = get_policy(country)
            result = engine.evaluate(
                ComplianceContext(
                    country=country,
                    purpose=f"{template.name} care workflow",
                    patient_identifiers=[policy.required_identifier_types[0]],
                    consent_present=True,
                    encrypted=True,
                    data_residency_region=policy.data_residency_region,
                    requested_fields=["diagnosis", "medications"],
                    necessary_fields=["diagnosis", "medications"],
                    actor_id="clinician-1",
                    audit_event_id="audit-1",
                )
            )

            assert result.blockers == [], f"{template.domain} failed for {country}"


def test_universal_template_compliance_section_tracks_country_requirements():
    registry = TemplateRegistry()

    for country in ["IND", "AUS", "USA", "GBR"]:
        template = registry.universal(country)
        compliance_section = next(
            section for section in template.sections if section.id == "compliance"
        )

        assert template.metadata["identifier_types"]
        assert template.metadata["data_residency_region"] == get_policy(
            country
        ).data_residency_region
        assert any("minimum necessary" in item.lower() for item in compliance_section.items)
        assert any("encrypted" in item.lower() for item in compliance_section.items)


def test_identifier_system_generation_does_not_embed_patient_mrn_value():
    identifier = PatientIdentifier.australia_mrn(
        "PATIENT-SECRET-MRN-123",
        assigner="Royal Melbourne Hospital",
    )

    fhir_identifier = identifier.to_fhir()

    assert fhir_identifier["value"] == "PATIENT-SECRET-MRN-123"
    assert "PATIENT-SECRET-MRN-123" not in fhir_identifier["system"]
    assert fhir_identifier["system"] == (
        "urn:krama:identifier:au:mrn:royal-melbourne-hospital"
    )


def test_patient_can_carry_speciality_local_mrns_without_abha():
    patient = FHIRPatient(
        identifiers=[
            PatientIdentifier.us_mrn("DENT-123", assigner="Smile Dental Boston"),
            PatientIdentifier.us_mrn("EYE-456", assigner="Retina Clinic Boston"),
        ],
        name="Jordan Smith",
        gender="unknown",
        birth_date="1975-09-20",
    ).to_fhir()

    systems = [identifier["system"] for identifier in patient["identifier"]]

    assert systems == [
        "urn:krama:identifier:us:mrn:smile-dental-boston",
        "urn:krama:identifier:us:mrn:retina-clinic-boston",
    ]
    assert patient["identifier"][0]["value"] == "DENT-123"
    assert patient["identifier"][1]["value"] == "EYE-456"
