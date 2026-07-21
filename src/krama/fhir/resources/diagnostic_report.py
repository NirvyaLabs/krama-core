"""FHIR DiagnosticReport resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FHIRDict, LOINC_SYSTEM, coding, make_id, reference


class FHIRDiagnosticReport(BaseModel):
    code: str = Field(min_length=1)
    display: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    result_refs: list[str] = Field(default_factory=list)
    status: str = "final"
    system: str = LOINC_SYSTEM
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        return {
            "resourceType": "DiagnosticReport",
            "id": self.id,
            "status": self.status,
            "code": {"coding": [coding(self.system, self.code, self.display)]},
            "subject": reference(self.patient_ref),
            "result": [reference(result_ref) for result_ref in self.result_refs],
        }
