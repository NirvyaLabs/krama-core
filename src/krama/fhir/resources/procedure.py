"""FHIR Procedure resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import (
    SNOMED_SYSTEM,
    FHIRDict,
    coding,
    make_id,
    reference,
)


class FHIRProcedure(BaseModel):
    code: str = Field(min_length=1)
    display: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    performed_date: str | None = None
    status: str = "completed"
    system: str = SNOMED_SYSTEM
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        resource = {
            "resourceType": "Procedure",
            "id": self.id,
            "status": self.status,
            "code": {"coding": [coding(self.system, self.code, self.display)]},
            "subject": reference(self.patient_ref),
        }
        if self.performed_date:
            resource["performedDateTime"] = self.performed_date
        return resource
