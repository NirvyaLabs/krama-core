import pytest

from krama.fhir.resources import (
    FHIRAllergyIntolerance,
    FHIRComposition,
    FHIRCondition,
    FHIRDiagnosticReport,
    FHIREncounter,
    FHIRMedicationRequest,
    FHIRObservation,
    FHIROrganization,
    FHIRPatient,
    FHIRPractitioner,
    FHIRProcedure,
)
from krama.fhir.resources.base import bundle_entry, coding, make_urn, reference


def test_base_helpers_build_fhir_shapes():
    assert make_urn("abc") == "urn:uuid:abc"
    assert coding("system", "code", "display") == {
        "system": "system",
        "code": "code",
        "display": "display",
    }
    assert reference("urn:uuid:abc") == {"reference": "urn:uuid:abc"}
    assert bundle_entry({"id": "abc", "resourceType": "Patient"}) == {
        "fullUrl": "urn:uuid:abc",
        "resource": {"id": "abc", "resourceType": "Patient"},
    }


def test_patient_resource_uses_abha_identifier_and_normalizes_gender():
    patient = FHIRPatient(
        id="patient-1",
        abha_id="ravi.kumar@abdm",
        name="Ravi Kumar",
        gender="MALE",
        birth_date="1990-05-15",
    ).to_fhir()

    assert patient["resourceType"] == "Patient"
    assert patient["id"] == "patient-1"
    assert patient["identifier"][0]["value"] == "ravi.kumar@abdm"
    assert patient["gender"] == "male"


def test_patient_rejects_invalid_gender():
    with pytest.raises(ValueError, match="gender"):
        FHIRPatient(
            abha_id="ravi.kumar@abdm",
            name="Ravi Kumar",
            gender="bad",
            birth_date="1990-05-15",
        )


def test_practitioner_and_organization_resources():
    practitioner = FHIRPractitioner(
        id="prac-1",
        identifier="DOC-123",
        name="Dr. Priya",
    ).to_fhir()
    organization = FHIROrganization(
        id="org-1",
        hfr_id="IN0410000123",
        name="District Hospital",
    ).to_fhir()

    assert practitioner["resourceType"] == "Practitioner"
    assert practitioner["identifier"][0]["value"] == "DOC-123"
    assert organization["resourceType"] == "Organization"
    assert organization["identifier"][0]["value"] == "IN0410000123"


def test_encounter_resource_with_and_without_organization():
    base = FHIREncounter(
        id="enc-1",
        patient_ref="urn:uuid:p",
        practitioner_ref="urn:uuid:dr",
        start_date="2026-07-20",
    ).to_fhir()
    inpatient = FHIREncounter(
        id="enc-2",
        patient_ref="urn:uuid:p",
        practitioner_ref="urn:uuid:dr",
        organization_ref="urn:uuid:org",
        start_date="2026-07-20",
        encounter_class="IMP",
    ).to_fhir()

    assert "serviceProvider" not in base
    assert inpatient["class"]["display"] == "inpatient encounter"
    assert inpatient["serviceProvider"]["reference"] == "urn:uuid:org"


def test_condition_resource_with_and_without_snomed():
    coded = FHIRCondition(
        id="cond-1",
        description="Essential hypertension",
        snomed_code="59621000",
        patient_ref="urn:uuid:p",
    ).to_fhir()
    uncoded = FHIRCondition(
        id="cond-2",
        description="Headache",
        patient_ref="urn:uuid:p",
    ).to_fhir()

    assert coded["code"]["coding"][0]["code"] == "59621000"
    assert uncoded["code"] == {"text": "Headache"}


def test_observation_value_variants():
    numeric = FHIRObservation(
        code="8480-6",
        display="Systolic blood pressure",
        value=130,
        unit="mmHg",
        patient_ref="urn:uuid:p",
    ).to_fhir()
    boolean = FHIRObservation(
        code="preg",
        display="Pregnant",
        value=False,
        patient_ref="urn:uuid:p",
    ).to_fhir()
    text = FHIRObservation(
        code="note",
        display="Note",
        value="stable",
        patient_ref="urn:uuid:p",
    ).to_fhir()

    assert numeric["valueQuantity"] == {"value": 130, "unit": "mmHg"}
    assert boolean["valueBoolean"] is False
    assert text["valueString"] == "stable"


def test_medication_request_resource_with_and_without_snomed():
    coded = FHIRMedicationRequest(
        name="Amlodipine",
        dosage="5mg daily",
        snomed_code="386864001",
        patient_ref="urn:uuid:p",
        requester_ref="urn:uuid:dr",
        encounter_ref="urn:uuid:enc",
    ).to_fhir()
    uncoded = FHIRMedicationRequest(
        name="ORS",
        dosage="as needed",
        patient_ref="urn:uuid:p",
        requester_ref="urn:uuid:dr",
    ).to_fhir()

    assert coded["medicationCodeableConcept"]["coding"][0]["code"] == "386864001"
    assert coded["encounter"]["reference"] == "urn:uuid:enc"
    assert uncoded["medicationCodeableConcept"] == {"text": "ORS"}
    assert "encounter" not in uncoded


def test_diagnostic_report_allergy_and_procedure_resources():
    report = FHIRDiagnosticReport(
        code="58410-2",
        display="CBC panel",
        patient_ref="urn:uuid:p",
        result_refs=["urn:uuid:obs"],
    ).to_fhir()
    allergy = FHIRAllergyIntolerance(
        substance="Penicillin",
        snomed_code="91936005",
        reaction="Rash",
        patient_ref="urn:uuid:p",
    ).to_fhir()
    allergy_minimal = FHIRAllergyIntolerance(
        substance="Dust",
        patient_ref="urn:uuid:p",
    ).to_fhir()
    procedure = FHIRProcedure(
        code="80146002",
        display="Appendectomy",
        patient_ref="urn:uuid:p",
        performed_date="2026-07-20",
    ).to_fhir()

    assert report["result"] == [{"reference": "urn:uuid:obs"}]
    assert allergy["reaction"] == [{"description": "Rash"}]
    assert allergy_minimal["code"] == {"text": "Dust"}
    assert "reaction" not in allergy_minimal
    assert procedure["performedDateTime"] == "2026-07-20"


def test_composition_resource_with_and_without_custodian():
    with_custodian = FHIRComposition(
        id="comp-1",
        title="OP Consultation Record",
        code="371530004",
        display="Clinical consultation report",
        patient_ref="urn:uuid:p",
        author_ref="urn:uuid:dr",
        encounter_ref="urn:uuid:enc",
        custodian_ref="urn:uuid:org",
        sections=[{"title": "Chief Complaints"}],
    ).to_fhir()
    without_custodian = FHIRComposition(
        id="comp-2",
        title="Prescription Record",
        code="440545006",
        display="Prescription record",
        patient_ref="urn:uuid:p",
        author_ref="urn:uuid:dr",
        encounter_ref="urn:uuid:enc",
        sections=[],
    ).to_fhir()

    assert with_custodian["custodian"]["reference"] == "urn:uuid:org"
    assert without_custodian["section"] == []
    assert "custodian" not in without_custodian
