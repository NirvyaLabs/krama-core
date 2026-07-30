"""FHIR MedicationRequest resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import (
    SNOMED_SYSTEM,
    FHIRDict,
    coding,
    make_id,
    reference,
)


class FHIRMedicationRequest(BaseModel):
    name: str = Field(min_length=1)
    dosage: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    requester_ref: str = Field(min_length=1)
    encounter_ref: str | None = None
    snomed_code: str = ""
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        medication: FHIRDict = {"text": self.name}
        if self.snomed_code:
            medication["coding"] = [coding(SNOMED_SYSTEM, self.snomed_code, self.name)]

        resource = {
            "resourceType": "MedicationRequest",
            "id": self.id,
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": medication,
            "subject": reference(self.patient_ref),
            "requester": reference(self.requester_ref),
            "dosageInstruction": [{"text": self.dosage}],
        }
        if self.encounter_ref:
            resource["encounter"] = reference(self.encounter_ref)
        return resource
