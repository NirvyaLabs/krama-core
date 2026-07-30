import json

import pytest
from pydantic import ValidationError as PydanticValidationError

from krama.fhir.bundles import (
    DiagnosisInfo,
    MedicationInfo,
    OrganizationInfo,
    PatientInfo,
    PractitionerInfo,
    create_discharge_summary_bundle,
    create_op_consult_bundle,
    create_prescription_bundle,
)


@pytest.fixture
def sample_patient():
    return PatientInfo(
        name="Ravi Kumar",
        abha_address="ravi.kumar@abdm",
        gender="male",
        date_of_birth="1990-05-15",
    )


@pytest.fixture
def sample_practitioner():
    return PractitionerInfo(
        name="Dr. Priya Sharma",
        identifier="DOC-AP-12345",
    )


@pytest.fixture
def sample_organization():
    return OrganizationInfo(
        name="District Hospital Guntur",
        hfr_id="IN0410000123",
    )


@pytest.fixture
def sample_diagnosis():
    return DiagnosisInfo(
        description="Essential hypertension",
        snomed_code="59621000",
        clinical_notes="Patient presents with elevated BP 150/95. Advising lifestyle changes.",
    )


@pytest.fixture
def sample_medications():
    return [
        MedicationInfo(
            name="Amlodipine",
            dosage="5mg once daily in the morning",
            snomed_code="386864001",
        ),
        MedicationInfo(
            name="Metformin",
            dosage="500mg twice daily with meals",
            snomed_code="109081006",
        ),
    ]


def _resource_types(bundle: dict) -> list[str]:
    return [entry["resource"]["resourceType"] for entry in bundle["entry"]]


def _find_entry(bundle: dict, resource_type: str) -> dict:
    return next(
        entry
        for entry in bundle["entry"]
        if entry["resource"]["resourceType"] == resource_type
    )


class TestOPConsultBundle:
    def test_returns_valid_bundle_structure(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "document"
        assert "timestamp" in bundle
        assert "identifier" in bundle
        assert len(bundle["entry"]) == 6

    def test_composition_is_first_entry(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert bundle["entry"][0]["resource"]["resourceType"] == "Composition"

    def test_contains_required_resources(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert set(_resource_types(bundle)) == {
            "Composition",
            "Patient",
            "Practitioner",
            "Organization",
            "Encounter",
            "Condition",
        }

    def test_patient_has_abha_identifier(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        patient = _find_entry(bundle, "Patient")["resource"]
        assert patient["identifier"][0] == {
            "system": "https://healthid.abdm.gov.in",
            "value": "ravi.kumar@abdm",
        }

    def test_encounter_references_patient(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        patient_ref = _find_entry(bundle, "Patient")["fullUrl"]
        encounter = _find_entry(bundle, "Encounter")["resource"]
        assert encounter["subject"]["reference"] == patient_ref

    def test_encounter_references_organization(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        organization_ref = _find_entry(bundle, "Organization")["fullUrl"]
        encounter = _find_entry(bundle, "Encounter")["resource"]
        assert encounter["serviceProvider"]["reference"] == organization_ref

    def test_with_medications(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_diagnosis,
        sample_medications,
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
            medications=sample_medications,
        )

        assert _resource_types(bundle).count("MedicationRequest") == 2

    def test_without_medications(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert "MedicationRequest" not in _resource_types(bundle)

    def test_bundle_is_json_serializable(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert json.loads(json.dumps(bundle))["resourceType"] == "Bundle"

    def test_each_entry_has_uuid_full_url(
        self, sample_patient, sample_practitioner, sample_organization, sample_diagnosis
    ):
        bundle = create_op_consult_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnosis=sample_diagnosis,
            encounter_date="2026-05-06",
        )

        assert all(entry["fullUrl"].startswith("urn:uuid:") for entry in bundle["entry"])


class TestPrescriptionBundle:
    def test_basic_prescription(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_medications,
    ):
        bundle = create_prescription_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            medications=sample_medications,
            encounter_date="2026-05-06",
        )

        assert _resource_types(bundle).count("MedicationRequest") == 2

    def test_prescription_with_diagnosis(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_medications,
        sample_diagnosis,
    ):
        bundle = create_prescription_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            medications=sample_medications,
            encounter_date="2026-05-06",
            diagnosis=sample_diagnosis,
        )

        assert "Condition" in _resource_types(bundle)

    def test_empty_medications_raises_error(
        self, sample_patient, sample_practitioner, sample_organization
    ):
        with pytest.raises(ValueError, match="at least one medication"):
            create_prescription_bundle(
                patient=sample_patient,
                practitioner=sample_practitioner,
                organization=sample_organization,
                medications=[],
                encounter_date="2026-05-06",
            )

    def test_composition_type_is_prescription(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_medications,
    ):
        bundle = create_prescription_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            medications=sample_medications,
            encounter_date="2026-05-06",
        )

        composition = bundle["entry"][0]["resource"]
        assert composition["type"]["coding"][0]["code"] == "440545006"


class TestDischargeSummaryBundle:
    def test_basic_discharge_summary(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_diagnosis,
        sample_medications,
    ):
        bundle = create_discharge_summary_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnoses=[sample_diagnosis],
            medications=sample_medications,
            admission_date="2026-04-28",
            discharge_date="2026-05-05",
            discharge_summary_text="Patient discharged in stable condition.",
        )

        assert "Condition" in _resource_types(bundle)
        assert "MedicationRequest" in _resource_types(bundle)

    def test_encounter_is_inpatient(
        self,
        sample_patient,
        sample_practitioner,
        sample_organization,
        sample_diagnosis,
    ):
        bundle = create_discharge_summary_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnoses=[sample_diagnosis],
            medications=[],
            admission_date="2026-04-28",
            discharge_date="2026-05-05",
            discharge_summary_text="Discharged in stable condition.",
        )

        encounter = _find_entry(bundle, "Encounter")["resource"]
        assert encounter["class"]["code"] == "IMP"
        assert encounter["period"] == {
            "start": "2026-04-28",
            "end": "2026-05-05",
        }

    def test_empty_diagnoses_raises_error(
        self, sample_patient, sample_practitioner, sample_organization
    ):
        with pytest.raises(ValueError, match="at least one diagnosis"):
            create_discharge_summary_bundle(
                patient=sample_patient,
                practitioner=sample_practitioner,
                organization=sample_organization,
                diagnoses=[],
                medications=[],
                admission_date="2026-04-28",
                discharge_date="2026-05-05",
                discharge_summary_text="N/A",
            )

    def test_multiple_diagnoses(
        self, sample_patient, sample_practitioner, sample_organization
    ):
        diagnoses = [
            DiagnosisInfo(
                description="Essential hypertension",
                snomed_code="59621000",
            ),
            DiagnosisInfo(
                description="Type 2 diabetes mellitus",
                snomed_code="44054006",
            ),
            DiagnosisInfo(
                description="Acute kidney injury",
                snomed_code="14669001",
            ),
        ]

        bundle = create_discharge_summary_bundle(
            patient=sample_patient,
            practitioner=sample_practitioner,
            organization=sample_organization,
            diagnoses=diagnoses,
            medications=[],
            admission_date="2026-04-20",
            discharge_date="2026-05-05",
            discharge_summary_text="Complex multi-system management.",
        )

        assert _resource_types(bundle).count("Condition") == 3


class TestInputValidation:
    def test_gender_normalization(self):
        patient = PatientInfo(
            name="Test",
            abha_address="test@abdm",
            gender="MALE",
            date_of_birth="2000-01-01",
        )

        assert patient.gender == "male"

    def test_gender_with_whitespace(self):
        patient = PatientInfo(
            name="Test",
            abha_address="test@abdm",
            gender="  Female  ",
            date_of_birth="2000-01-01",
        )

        assert patient.gender == "female"

    def test_invalid_gender_raises_error(self):
        with pytest.raises(ValueError, match="gender must be one of"):
            PatientInfo(
                name="Test",
                abha_address="test@abdm",
                gender="invalid",
                date_of_birth="2000-01-01",
            )

    def test_missing_required_field_raises_error(self):
        with pytest.raises(PydanticValidationError):
            PatientInfo(
                name="Test",
                gender="male",
                date_of_birth="2000-01-01",
            )
