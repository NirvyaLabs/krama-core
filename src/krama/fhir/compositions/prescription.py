"""PrescriptionRecord document builder."""

from __future__ import annotations

from krama.exceptions import FHIRValidationError
from krama.fhir.compositions.base import assemble_document_bundle, ref_for, section
from krama.fhir.resources import (
    FHIRComposition,
    FHIRCondition,
    FHIREncounter,
    FHIRMedicationRequest,
    FHIROrganization,
    FHIRPatient,
    FHIRPractitioner,
)
from krama.fhir.resources.base import FHIRDict


class PrescriptionBuilder:
    """Builder for ABDM PrescriptionRecord FHIR document bundles."""

    def __init__(self) -> None:
        self._patient: FHIRPatient | None = None
        self._practitioner: FHIRPractitioner | None = None
        self._organization: FHIROrganization | None = None
        self._encounter_date: str | None = None
        self._medications: list[tuple[str, str, str]] = []
        self._diagnoses: list[tuple[str, str]] = []

    def set_patient(self, patient: FHIRPatient) -> PrescriptionBuilder:
        self._patient = patient
        return self

    def set_practitioner(
        self, practitioner: FHIRPractitioner
    ) -> PrescriptionBuilder:
        self._practitioner = practitioner
        return self

    def set_organization(
        self, organization: FHIROrganization
    ) -> PrescriptionBuilder:
        self._organization = organization
        return self

    def set_encounter(self, encounter_date: str) -> PrescriptionBuilder:
        self._encounter_date = encounter_date
        return self

    def add_medication(
        self,
        name: str,
        dosage: str,
        *,
        snomed_code: str = "",
    ) -> PrescriptionBuilder:
        self._medications.append((name, dosage, snomed_code))
        return self

    def add_diagnosis(
        self,
        description: str,
        *,
        snomed_code: str = "",
    ) -> PrescriptionBuilder:
        self._diagnoses.append((description, snomed_code))
        return self

    def build(self) -> FHIRDict:
        patient, practitioner, organization, encounter_date = self._required()

        patient_resource = patient.to_fhir()
        practitioner_resource = practitioner.to_fhir()
        organization_resource = organization.to_fhir()
        encounter_resource = FHIREncounter(
            patient_ref=ref_for(patient_resource),
            practitioner_ref=ref_for(practitioner_resource),
            organization_ref=ref_for(organization_resource),
            start_date=encounter_date,
        ).to_fhir()

        diagnosis_resources = [
            FHIRCondition(
                description=description,
                snomed_code=snomed_code,
                patient_ref=ref_for(patient_resource),
            ).to_fhir()
            for description, snomed_code in self._diagnoses
        ]
        medication_resources = [
            FHIRMedicationRequest(
                name=name,
                dosage=dosage,
                snomed_code=snomed_code,
                patient_ref=ref_for(patient_resource),
                requester_ref=ref_for(practitioner_resource),
                encounter_ref=ref_for(encounter_resource),
            ).to_fhir()
            for name, dosage, snomed_code in self._medications
        ]

        sections = []
        if diagnosis_resources:
            sections.append(
                section("Diagnosis", [ref_for(resource) for resource in diagnosis_resources])
            )
        sections.append(
            section("Prescription", [ref_for(resource) for resource in medication_resources])
        )

        composition = FHIRComposition(
            title="Prescription Record",
            code="440545006",
            display="Prescription record",
            patient_ref=ref_for(patient_resource),
            author_ref=ref_for(practitioner_resource),
            encounter_ref=ref_for(encounter_resource),
            custodian_ref=ref_for(organization_resource),
            sections=sections,
        ).to_fhir()

        return assemble_document_bundle(
            [
                composition,
                patient_resource,
                practitioner_resource,
                organization_resource,
                encounter_resource,
                *diagnosis_resources,
                *medication_resources,
            ]
        )

    def _required(
        self,
    ) -> tuple[FHIRPatient, FHIRPractitioner, FHIROrganization, str]:
        missing = []
        if self._patient is None:
            missing.append("patient")
        if self._practitioner is None:
            missing.append("practitioner")
        if self._organization is None:
            missing.append("organization")
        if self._encounter_date is None:
            missing.append("encounter")
        if not self._medications:
            missing.append("medication")
        if missing:
            raise FHIRValidationError(f"Missing required Prescription fields: {missing}")
        return (
            self._patient,
            self._practitioner,
            self._organization,
            self._encounter_date,
        )
