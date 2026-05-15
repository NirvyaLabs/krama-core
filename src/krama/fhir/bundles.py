"""FHIR R4 document bundle builders for ABDM care contexts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from html import escape
from typing import Any

from pydantic import BaseModel, Field, field_validator


FHIRResource = dict[str, Any]

VALID_GENDERS = {"male", "female", "other", "unknown"}

ABHA_SYSTEM = "https://healthid.abdm.gov.in"
PRACTITIONER_SYSTEM = "https://doctor.ndhm.gov.in"
FACILITY_SYSTEM = "https://facility.abdm.gov.in"
SNOMED_SYSTEM = "http://snomed.info/sct"
ACT_CODE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
BUNDLE_ID_SYSTEM = "https://krama.dev/bundle-id"


class PatientInfo(BaseModel):
    """Patient details needed to create ABDM/FHIR records."""

    name: str = Field(description="Patient's full name")
    abha_address: str = Field(description="Patient's ABHA address, e.g. name@abdm")
    gender: str = Field(description="FHIR gender: male, female, other, or unknown")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        gender = value.lower().strip()
        if gender not in VALID_GENDERS:
            allowed = ", ".join(sorted(VALID_GENDERS))
            raise ValueError(f"gender must be one of {allowed}, got '{gender}'")
        return gender


class PractitionerInfo(BaseModel):
    """Healthcare practitioner details."""

    name: str = Field(description="Practitioner's full name")
    identifier: str = Field(description="Practitioner's registration identifier")


class OrganizationInfo(BaseModel):
    """Healthcare facility details."""

    name: str = Field(description="Facility name")
    hfr_id: str = Field(description="Health Facility Registry ID")


class DiagnosisInfo(BaseModel):
    """Diagnosis details with SNOMED CT coding."""

    description: str = Field(description="Human-readable diagnosis")
    snomed_code: str = Field(description="SNOMED CT code")
    clinical_notes: str = Field(default="", description="Optional clinical notes")


class MedicationInfo(BaseModel):
    """Medication details for a prescription or discharge summary."""

    name: str = Field(description="Medication name")
    dosage: str = Field(description="Dosage instructions")
    snomed_code: str = Field(default="", description="Optional SNOMED CT code")


def _make_uuid() -> str:
    return f"urn:uuid:{uuid.uuid4()}"


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _narrative_div(text: str) -> str:
    return f"<div xmlns='http://www.w3.org/1999/xhtml'>{escape(text)}</div>"


def _build_patient_resource(patient: PatientInfo) -> FHIRResource:
    return {
        "resourceType": "Patient",
        "name": [{"text": patient.name}],
        "identifier": [{"system": ABHA_SYSTEM, "value": patient.abha_address}],
        "gender": patient.gender,
        "birthDate": patient.date_of_birth,
    }


def _build_practitioner_resource(practitioner: PractitionerInfo) -> FHIRResource:
    return {
        "resourceType": "Practitioner",
        "name": [{"text": practitioner.name}],
        "identifier": [
            {"system": PRACTITIONER_SYSTEM, "value": practitioner.identifier}
        ],
    }


def _build_organization_resource(org: OrganizationInfo) -> FHIRResource:
    return {
        "resourceType": "Organization",
        "name": org.name,
        "identifier": [{"system": FACILITY_SYSTEM, "value": org.hfr_id}],
    }


def _build_encounter_resource(
    patient_ref: str,
    practitioner_ref: str,
    organization_ref: str,
    start_date: str,
    encounter_class: str = "AMB",
) -> FHIRResource:
    class_display = {
        "AMB": "ambulatory",
        "IMP": "inpatient encounter",
        "EMER": "emergency",
    }.get(encounter_class, encounter_class)

    return {
        "resourceType": "Encounter",
        "status": "finished",
        "class": {
            "system": ACT_CODE_SYSTEM,
            "code": encounter_class,
            "display": class_display,
        },
        "subject": {"reference": patient_ref},
        "participant": [{"individual": {"reference": practitioner_ref}}],
        "serviceProvider": {"reference": organization_ref},
        "period": {"start": start_date},
    }


def _build_condition_resource(
    diagnosis: DiagnosisInfo,
    patient_ref: str,
) -> FHIRResource:
    return {
        "resourceType": "Condition",
        "code": {
            "coding": [
                {
                    "system": SNOMED_SYSTEM,
                    "code": diagnosis.snomed_code,
                    "display": diagnosis.description,
                }
            ],
            "text": diagnosis.description,
        },
        "subject": {"reference": patient_ref},
    }


def _build_medication_request_resource(
    medication: MedicationInfo,
    patient_ref: str,
    practitioner_ref: str,
    encounter_ref: str,
) -> FHIRResource:
    medication_code: FHIRResource = {"text": medication.name}
    if medication.snomed_code:
        medication_code["coding"] = [
            {
                "system": SNOMED_SYSTEM,
                "code": medication.snomed_code,
                "display": medication.name,
            }
        ]

    return {
        "resourceType": "MedicationRequest",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": medication_code,
        "subject": {"reference": patient_ref},
        "requester": {"reference": practitioner_ref},
        "encounter": {"reference": encounter_ref},
        "dosageInstruction": [{"text": medication.dosage}],
    }


def _build_composition(
    title: str,
    code: str,
    display: str,
    patient_ref: str,
    practitioner_ref: str,
    organization_ref: str,
    encounter_ref: str,
    sections: list[FHIRResource],
) -> FHIRResource:
    return {
        "resourceType": "Composition",
        "status": "final",
        "type": {
            "coding": [{"system": SNOMED_SYSTEM, "code": code, "display": display}]
        },
        "title": title,
        "date": _make_timestamp(),
        "author": [{"reference": practitioner_ref}],
        "subject": {"reference": patient_ref},
        "encounter": {"reference": encounter_ref},
        "custodian": {"reference": organization_ref},
        "section": sections,
    }


def _wrap_as_bundle_entry(resource: FHIRResource, full_url: str) -> FHIRResource:
    return {"fullUrl": full_url, "resource": resource}


def _assemble_document_bundle(entries: list[FHIRResource]) -> FHIRResource:
    return {
        "resourceType": "Bundle",
        "type": "document",
        "timestamp": _make_timestamp(),
        "identifier": {"system": BUNDLE_ID_SYSTEM, "value": str(uuid.uuid4())},
        "entry": entries,
    }


def _build_medication_entries(
    medications: list[MedicationInfo],
    patient_ref: str,
    practitioner_ref: str,
    encounter_ref: str,
) -> tuple[list[FHIRResource], list[FHIRResource]]:
    entries = []
    references = []

    for medication in medications:
        medication_id = _make_uuid()
        medication_resource = _build_medication_request_resource(
            medication=medication,
            patient_ref=patient_ref,
            practitioner_ref=practitioner_ref,
            encounter_ref=encounter_ref,
        )
        entries.append(_wrap_as_bundle_entry(medication_resource, medication_id))
        references.append({"reference": medication_id})

    return entries, references


def create_op_consult_bundle(
    patient: PatientInfo,
    practitioner: PractitionerInfo,
    organization: OrganizationInfo,
    diagnosis: DiagnosisInfo,
    encounter_date: str,
    medications: list[MedicationInfo] | None = None,
) -> FHIRResource:
    """Create an ABDM OPConsult document bundle."""
    composition_id = _make_uuid()
    patient_id = _make_uuid()
    practitioner_id = _make_uuid()
    organization_id = _make_uuid()
    encounter_id = _make_uuid()
    condition_id = _make_uuid()

    encounter = _build_encounter_resource(
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        start_date=encounter_date,
    )
    condition = _build_condition_resource(diagnosis, patient_id)

    clinical_text = diagnosis.clinical_notes or diagnosis.description
    sections = [
        {
            "title": "Chief Complaint",
            "text": {"status": "generated", "div": _narrative_div(clinical_text)},
            "entry": [{"reference": condition_id}],
        }
    ]

    medication_entries: list[FHIRResource] = []
    if medications:
        medication_entries, medication_refs = _build_medication_entries(
            medications=medications,
            patient_ref=patient_id,
            practitioner_ref=practitioner_id,
            encounter_ref=encounter_id,
        )
        sections.append({"title": "Medications", "entry": medication_refs})

    composition = _build_composition(
        title="OP Consultation Record",
        code="371530004",
        display="Clinical consultation report",
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        encounter_ref=encounter_id,
        sections=sections,
    )

    entries = [
        _wrap_as_bundle_entry(composition, composition_id),
        _wrap_as_bundle_entry(_build_patient_resource(patient), patient_id),
        _wrap_as_bundle_entry(
            _build_practitioner_resource(practitioner), practitioner_id
        ),
        _wrap_as_bundle_entry(_build_organization_resource(organization), organization_id),
        _wrap_as_bundle_entry(encounter, encounter_id),
        _wrap_as_bundle_entry(condition, condition_id),
        *medication_entries,
    ]
    return _assemble_document_bundle(entries)


def create_prescription_bundle(
    patient: PatientInfo,
    practitioner: PractitionerInfo,
    organization: OrganizationInfo,
    medications: list[MedicationInfo],
    encounter_date: str,
    diagnosis: DiagnosisInfo | None = None,
) -> FHIRResource:
    """Create an ABDM Prescription document bundle."""
    if not medications:
        raise ValueError("A prescription must contain at least one medication.")

    composition_id = _make_uuid()
    patient_id = _make_uuid()
    practitioner_id = _make_uuid()
    organization_id = _make_uuid()
    encounter_id = _make_uuid()

    encounter = _build_encounter_resource(
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        start_date=encounter_date,
    )
    medication_entries, medication_refs = _build_medication_entries(
        medications=medications,
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        encounter_ref=encounter_id,
    )

    sections = [{"title": "Prescription", "entry": medication_refs}]
    diagnosis_entries: list[FHIRResource] = []
    if diagnosis:
        condition_id = _make_uuid()
        condition = _build_condition_resource(diagnosis, patient_id)
        diagnosis_entries.append(_wrap_as_bundle_entry(condition, condition_id))
        sections.insert(0, {"title": "Diagnosis", "entry": [{"reference": condition_id}]})

    composition = _build_composition(
        title="Prescription Record",
        code="440545006",
        display="Prescription record",
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        encounter_ref=encounter_id,
        sections=sections,
    )

    entries = [
        _wrap_as_bundle_entry(composition, composition_id),
        _wrap_as_bundle_entry(_build_patient_resource(patient), patient_id),
        _wrap_as_bundle_entry(
            _build_practitioner_resource(practitioner), practitioner_id
        ),
        _wrap_as_bundle_entry(_build_organization_resource(organization), organization_id),
        _wrap_as_bundle_entry(encounter, encounter_id),
        *diagnosis_entries,
        *medication_entries,
    ]
    return _assemble_document_bundle(entries)


def create_discharge_summary_bundle(
    patient: PatientInfo,
    practitioner: PractitionerInfo,
    organization: OrganizationInfo,
    diagnoses: list[DiagnosisInfo],
    medications: list[MedicationInfo],
    admission_date: str,
    discharge_date: str,
    discharge_summary_text: str,
) -> FHIRResource:
    """Create an ABDM Discharge Summary document bundle."""
    if not diagnoses:
        raise ValueError("A discharge summary must include at least one diagnosis.")

    composition_id = _make_uuid()
    patient_id = _make_uuid()
    practitioner_id = _make_uuid()
    organization_id = _make_uuid()
    encounter_id = _make_uuid()

    encounter = _build_encounter_resource(
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        start_date=admission_date,
        encounter_class="IMP",
    )
    encounter["period"]["end"] = discharge_date

    sections = [
        {
            "title": "Discharge Summary",
            "text": {
                "status": "generated",
                "div": _narrative_div(discharge_summary_text),
            },
        }
    ]

    diagnosis_entries = []
    diagnosis_refs = []
    for diagnosis in diagnoses:
        condition_id = _make_uuid()
        condition = _build_condition_resource(diagnosis, patient_id)
        diagnosis_entries.append(_wrap_as_bundle_entry(condition, condition_id))
        diagnosis_refs.append({"reference": condition_id})
    sections.append({"title": "Diagnoses", "entry": diagnosis_refs})

    medication_entries: list[FHIRResource] = []
    if medications:
        medication_entries, medication_refs = _build_medication_entries(
            medications=medications,
            patient_ref=patient_id,
            practitioner_ref=practitioner_id,
            encounter_ref=encounter_id,
        )
        sections.append({"title": "Discharge Medications", "entry": medication_refs})

    composition = _build_composition(
        title="Discharge Summary",
        code="373942005",
        display="Discharge summary",
        patient_ref=patient_id,
        practitioner_ref=practitioner_id,
        organization_ref=organization_id,
        encounter_ref=encounter_id,
        sections=sections,
    )

    entries = [
        _wrap_as_bundle_entry(composition, composition_id),
        _wrap_as_bundle_entry(_build_patient_resource(patient), patient_id),
        _wrap_as_bundle_entry(
            _build_practitioner_resource(practitioner), practitioner_id
        ),
        _wrap_as_bundle_entry(_build_organization_resource(organization), organization_id),
        _wrap_as_bundle_entry(encounter, encounter_id),
        *diagnosis_entries,
        *medication_entries,
    ]
    return _assemble_document_bundle(entries)
