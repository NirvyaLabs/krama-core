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
    PatientIdentifier,
    PatientIdentifierType,
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


def test_patient_resource_supports_global_identifier_list_without_abha():
    patient = FHIRPatient(
        id="patient-au-1",
        identifiers=[
            PatientIdentifier.australia_ihi("8003608166690503"),
            PatientIdentifier.australia_mrn("MRN-123", assigner="Royal Melbourne"),
        ],
        name="Amelia Brown",
        gender="female",
        birth_date="1988-04-12",
    ).to_fhir()

    assert patient["identifier"][0] == {
        "system": "http://ns.electronichealth.net.au/id/hi/ihi/1.0",
        "value": "8003608166690503",
    }
    assert patient["identifier"][1]["system"] == (
        "urn:krama:identifier:au:mrn:royal-melbourne"
    )
    assert patient["identifier"][1]["assigner"] == {"display": "Royal Melbourne"}


def test_patient_identifier_supports_india_us_uk_and_custom_systems():
    identifiers = [
        PatientIdentifier.india_abha("12-3456-7890-1234"),
        PatientIdentifier.us_mrn("MRN-9", assigner="Mass General"),
        PatientIdentifier(value="1EG4-TE5-MK73", type=PatientIdentifierType.US_MBI),
        PatientIdentifier.uk_nhs_number("9000000009"),
        PatientIdentifier.uk_mrn("MRN-UK-1", assigner="Guy's and St Thomas'"),
        PatientIdentifier(
            value="LOCAL-1",
            type=PatientIdentifierType.CUSTOM,
            system="https://hospital.example/fhir/Id/patient",
        ),
    ]

    systems = [identifier.to_fhir()["system"] for identifier in identifiers]

    assert systems[0] == "https://healthid.abdm.gov.in"
    assert systems[1] == "urn:krama:identifier:us:mrn:mass-general"
    assert systems[2] == "http://hl7.org/fhir/sid/us-mbi"
    assert systems[3] == "https://fhir.nhs.uk/Id/nhs-number"
    assert systems[4] == "urn:krama:identifier:uk:mrn:guy-s-and-st-thomas"
    assert systems[5] == "https://hospital.example/fhir/Id/patient"


def test_patient_identifier_requires_system_or_assigner_for_local_ids():
    with pytest.raises(ValueError, match="local MRN"):
        PatientIdentifier(value="MRN-1", type=PatientIdentifierType.LOCAL_MRN)

    with pytest.raises(ValueError, match="custom"):
        PatientIdentifier(value="patient-1")


def test_patient_requires_at_least_one_identifier():
    with pytest.raises(ValueError, match="abha_id or identifiers"):
        FHIRPatient(
            name="No Identifier",
            gender="unknown",
            birth_date="1990-01-01",
        )


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
