"""OPConsultRecord document builder."""

from __future__ import annotations

from krama.exceptions import FHIRValidationError
from krama.fhir.compositions.base import assemble_document_bundle, ref_for, section
from krama.fhir.resources import (
    FHIRAllergyIntolerance,
    FHIRComposition,
    FHIRCondition,
    FHIREncounter,
    FHIRMedicationRequest,
    FHIRObservation,
    FHIROrganization,
    FHIRPatient,
    FHIRPractitioner,
    FHIRProcedure,
)
from krama.fhir.resources.base import FHIRDict


class OPConsultBuilder:
    """Builder for ABDM OPConsultRecord FHIR document bundles."""

    def __init__(self) -> None:
        self._patient: FHIRPatient | None = None
        self._practitioner: FHIRPractitioner | None = None
        self._organization: FHIROrganization | None = None
        self._encounter_date: str | None = None
        self._conditions: list[FHIRCondition] = []
        self._observations: list[FHIRObservation] = []
        self._medications: list[tuple[str, str, str]] = []
        self._allergies: list[tuple[str, str, str]] = []
        self._procedures: list[tuple[str, str, str | None]] = []

    def set_patient(self, patient: FHIRPatient) -> "OPConsultBuilder":
        self._patient = patient
        return self

    def set_practitioner(
        self, practitioner: FHIRPractitioner
    ) -> "OPConsultBuilder":
        self._practitioner = practitioner
        return self

    def set_organization(self, organization: FHIROrganization) -> "OPConsultBuilder":
        self._organization = organization
        return self

    def set_encounter(self, encounter_date: str) -> "OPConsultBuilder":
        self._encounter_date = encounter_date
        return self

    def add_chief_complaint(
        self,
        description: str,
        *,
        snomed_code: str = "",
    ) -> "OPConsultBuilder":
        self._conditions.append(
            FHIRCondition(
                description=description,
                snomed_code=snomed_code,
                patient_ref="pending",
            )
        )
        return self

    def add_observation(
        self,
        code: str,
        display: str,
        value: str | int | float | bool,
        *,
        unit: str = "",
    ) -> "OPConsultBuilder":
        self._observations.append(
            FHIRObservation(
                code=code,
                display=display,
                value=value,
                unit=unit,
                patient_ref="pending",
            )
        )
        return self

    def add_medication(
        self,
        name: str,
        dosage: str,
        *,
        snomed_code: str = "",
    ) -> "OPConsultBuilder":
        self._medications.append((name, dosage, snomed_code))
        return self

    def add_allergy(
        self,
        substance: str,
        *,
        reaction: str = "",
        snomed_code: str = "",
    ) -> "OPConsultBuilder":
        self._allergies.append((substance, reaction, snomed_code))
        return self

    def add_procedure(
        self,
        code: str,
        display: str,
        *,
        performed_date: str | None = None,
    ) -> "OPConsultBuilder":
        self._procedures.append((code, display, performed_date))
        return self

    def build(self) -> FHIRDict:
        patient, practitioner, organization, encounter_date = self._required()

        patient_resource = patient.to_fhir()
        practitioner_resource = practitioner.to_fhir()
        organization_resource = organization.to_fhir()

        encounter = FHIREncounter(
            patient_ref=ref_for(patient_resource),
            practitioner_ref=ref_for(practitioner_resource),
            organization_ref=ref_for(organization_resource),
            start_date=encounter_date,
        )
        encounter_resource = encounter.to_fhir()

        condition_resources = [
            condition.model_copy(
                update={"patient_ref": ref_for(patient_resource)}
            ).to_fhir()
            for condition in self._conditions
        ]
        observation_resources = [
            observation.model_copy(
                update={"patient_ref": ref_for(patient_resource)}
            ).to_fhir()
            for observation in self._observations
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
        allergy_resources = [
            FHIRAllergyIntolerance(
                substance=substance,
                reaction=reaction,
                snomed_code=snomed_code,
                patient_ref=ref_for(patient_resource),
            ).to_fhir()
            for substance, reaction, snomed_code in self._allergies
        ]
        procedure_resources = [
            FHIRProcedure(
                code=code,
                display=display,
                performed_date=performed_date,
                patient_ref=ref_for(patient_resource),
            ).to_fhir()
            for code, display, performed_date in self._procedures
        ]

        composition = FHIRComposition(
            title="OP Consultation Record",
            code="371530004",
            display="Clinical consultation report",
            patient_ref=ref_for(patient_resource),
            author_ref=ref_for(practitioner_resource),
            encounter_ref=ref_for(encounter_resource),
            custodian_ref=ref_for(organization_resource),
            sections=self._sections(
                condition_resources,
                allergy_resources,
                medication_resources,
                observation_resources,
                procedure_resources,
            ),
        ).to_fhir()

        return assemble_document_bundle(
            [
                composition,
                patient_resource,
                practitioner_resource,
                organization_resource,
                encounter_resource,
                *condition_resources,
                *allergy_resources,
                *medication_resources,
                *observation_resources,
                *procedure_resources,
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
        if not self._conditions:
            missing.append("chief_complaint")
        if missing:
            raise FHIRValidationError(f"Missing required OPConsult fields: {missing}")
        return (
            self._patient,
            self._practitioner,
            self._organization,
            self._encounter_date,
        )

    def _sections(
        self,
        conditions: list[FHIRDict],
        allergies: list[FHIRDict],
        medications: list[FHIRDict],
        observations: list[FHIRDict],
        procedures: list[FHIRDict],
    ) -> list[FHIRDict]:
        sections = [
            section("Chief Complaints", [ref_for(resource) for resource in conditions])
        ]
        if allergies:
            sections.append(section("Allergies", [ref_for(r) for r in allergies]))
        if medications:
            sections.append(section("Medications", [ref_for(r) for r in medications]))
        if observations:
            sections.append(section("Observations", [ref_for(r) for r in observations]))
        if procedures:
            sections.append(section("Procedures", [ref_for(r) for r in procedures]))
        return sections
