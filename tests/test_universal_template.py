from krama.templates import (
    TemplateRegistry,
    UniversalTemplateContext,
    create_universal_template,
)


def test_universal_template_adapts_to_australia_defaults():
    template = create_universal_template(UniversalTemplateContext(country="AU"))

    assert template.jurisdiction == "AUS"
    assert template.coding_system == "icd10_am"
    assert template.prescription_type == "standard"
    assert template.metadata["identifier_types"] == [
        "australia_ihi",
        "australia_mrn",
        "australia_medicare",
    ]
    assert template.metadata["data_residency_region"] == "ap-southeast-2"
    assert {section.id for section in template.sections} >= {
        "patient_identity",
        "assessment",
        "compliance",
    }


def test_universal_template_adapts_to_india_us_and_uk():
    india = create_universal_template(UniversalTemplateContext(country="IND"))
    us = create_universal_template(UniversalTemplateContext(country="US"))
    uk = create_universal_template(UniversalTemplateContext(country="UK"))

    assert india.metadata["identifier_types"] == [
        "india_abha",
        "india_abha_address",
        "local_mrn",
    ]
    assert us.coding_system == "icd10_cm"
    assert "HIPAA Privacy Rule" in us.metadata["compliance_frameworks"]
    assert uk.jurisdiction == "GBR"
    assert uk.metadata["identifier_types"] == ["uk_nhs_number", "uk_mrn"]


def test_universal_template_allows_custom_country_context():
    template = create_universal_template(
        UniversalTemplateContext(
            country="NZ",
            coding_system="icd10_am",
            identifier_types=["local_mrn", "custom"],
            compliance_frameworks=["Health Information Privacy Code"],
            data_residency_region="ap-southeast-2",
        )
    )

    assert template.jurisdiction == "NZ"
    assert template.metadata["identifier_types"] == ["local_mrn", "custom"]
    assert template.metadata["compliance_frameworks"] == [
        "Health Information Privacy Code"
    ]


def test_registry_can_return_universal_template_without_registering_it():
    template = TemplateRegistry().universal("GB")

    assert template.jurisdiction == "GBR"
    assert template.encounter_type == "adaptive_encounter"
    assert template.domain == "global"
