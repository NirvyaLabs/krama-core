"""FHIR AllergyIntolerance resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FHIRDict, SNOMED_SYSTEM, coding, make_id, reference


class FHIRAllergyIntolerance(BaseModel):
    substance: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    reaction: str = ""
    snomed_code: str = ""
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        code: FHIRDict = {"text": self.substance}
        if self.snomed_code:
            code["coding"] = [coding(SNOMED_SYSTEM, self.snomed_code, self.substance)]

        resource = {
            "resourceType": "AllergyIntolerance",
            "id": self.id,
            "clinicalStatus": {
                "coding": [
                    coding(
                        "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "active",
                        "Active",
                    )
                ]
            },
            "code": code,
            "patient": reference(self.patient_ref),
        }
        if self.reaction:
            resource["reaction"] = [{"description": self.reaction}]
        return resource
