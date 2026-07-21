"""FHIR Encounter resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import ACT_CODE_SYSTEM, FHIRDict, make_id, reference


class FHIREncounter(BaseModel):
    patient_ref: str = Field(min_length=1)
    practitioner_ref: str = Field(min_length=1)
    start_date: str = Field(min_length=1)
    organization_ref: str | None = None
    encounter_class: str = "AMB"
    status: str = "finished"
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        display = {
            "AMB": "ambulatory",
            "IMP": "inpatient encounter",
            "EMER": "emergency",
        }.get(self.encounter_class, self.encounter_class)

        resource = {
            "resourceType": "Encounter",
            "id": self.id,
            "status": self.status,
            "class": {
                "system": ACT_CODE_SYSTEM,
                "code": self.encounter_class,
                "display": display,
            },
            "subject": reference(self.patient_ref),
            "participant": [{"individual": reference(self.practitioner_ref)}],
            "period": {"start": self.start_date},
        }
        if self.organization_ref:
            resource["serviceProvider"] = reference(self.organization_ref)
        return resource
