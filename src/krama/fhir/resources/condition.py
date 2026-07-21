"""FHIR Condition resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FHIRDict, SNOMED_SYSTEM, coding, make_id, reference


class FHIRCondition(BaseModel):
    description: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    snomed_code: str = Field(default="")
    clinical_status: str = "active"
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        code = {"text": self.description}
        if self.snomed_code:
            code["coding"] = [coding(SNOMED_SYSTEM, self.snomed_code, self.description)]

        return {
            "resourceType": "Condition",
            "id": self.id,
            "clinicalStatus": {
                "coding": [
                    coding(
                        "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        self.clinical_status,
                        self.clinical_status,
                    )
                ]
            },
            "code": code,
            "subject": reference(self.patient_ref),
        }
