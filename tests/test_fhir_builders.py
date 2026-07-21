import pytest

from krama.exceptions import FHIRValidationError
from krama.fhir import OPConsultBuilder, PrescriptionBuilder
from krama.fhir.compositions.base import assemble_document_bundle, narrative, section
from krama.fhir.resources import FHIROrganization, FHIRPatient, FHIRPractitioner


def patient():
    return FHIRPatient(
        id="patient-1",
        abha_id="ravi.kumar@abdm",
        name="Ravi Kumar",
        gender="male",
        birth_date="1990-05-15",
    )


def practitioner():
    return FHIRPractitioner(
        id="practitioner-1",
        identifier="DOC-12345",
        name="Dr. Priya Sharma",
    )


def organization():
    return FHIROrganization(
        id="org-1",
        hfr_id="IN0410000123",
        name="District Hospital Guntur",
    )


def resource_types(bundle: dict) -> list[str]:
    return [entry["resource"]["resourceType"] for entry in bundle["entry"]]


def test_composition_base_helpers_escape_narrative_and_require_composition_first():
    assert "&lt;script&gt;" in narrative("<script>")["div"]
    assert section("Notes", ["urn:uuid:a"], "plain")["entry"] == [
        {"reference": "urn:uuid:a"}
    ]
    with pytest.raises(ValueError, match="Composition"):
        assemble_document_bundle([{"id": "p", "resourceType": "Patient"}])


def test_op_consult_builder_builds_complete_document_bundle():
    bundle = (
        OPConsultBuilder()
        .set_patient(patient())
        .set_practitioner(practitioner())
        .set_organization(organization())
        .set_encounter("2026-07-20")
        .add_chief_complaint("Essential hypertension", snomed_code="59621000")
        .add_observation("8480-6", "Systolic blood pressure", 130, unit="mmHg")
        .add_medication("Amlodipine", "5mg daily", snomed_code="386864001")
        .add_allergy("Penicillin", reaction="Rash", snomed_code="91936005")
        .add_procedure("80146002", "Appendectomy", performed_date="2026-07-20")
        .build()
    )

    types = resource_types(bundle)
    assert bundle["type"] == "document"
    assert types[0] == "Composition"
    assert "Patient" in types
    assert "Condition" in types
    assert "Observation" in types
    assert "MedicationRequest" in types
    assert "AllergyIntolerance" in types
    assert "Procedure" in types

    composition = bundle["entry"][0]["resource"]
    assert [section["title"] for section in composition["section"]] == [
        "Chief Complaints",
        "Allergies",
        "Medications",
        "Observations",
        "Procedures",
    ]


def test_op_consult_builder_requires_core_fields():
    with pytest.raises(FHIRValidationError, match="chief_complaint"):
        (
            OPConsultBuilder()
            .set_patient(patient())
            .set_practitioner(practitioner())
            .set_organization(organization())
            .set_encounter("2026-07-20")
            .build()
        )


def test_prescription_builder_builds_document_bundle_with_diagnosis():
    bundle = (
        PrescriptionBuilder()
        .set_patient(patient())
        .set_practitioner(practitioner())
        .set_organization(organization())
        .set_encounter("2026-07-20")
        .add_diagnosis("Essential hypertension", snomed_code="59621000")
        .add_medication("Amlodipine", "5mg daily", snomed_code="386864001")
        .add_medication("Metformin", "500mg twice daily")
        .build()
    )

    assert resource_types(bundle).count("MedicationRequest") == 2
    assert "Condition" in resource_types(bundle)
    assert bundle["entry"][0]["resource"]["type"]["coding"][0]["code"] == "440545006"


def test_prescription_builder_requires_medication():
    with pytest.raises(FHIRValidationError, match="medication"):
        (
            PrescriptionBuilder()
            .set_patient(patient())
            .set_practitioner(practitioner())
            .set_organization(organization())
            .set_encounter("2026-07-20")
            .build()
        )
