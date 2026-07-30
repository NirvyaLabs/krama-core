"""FHIR Composition resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import (
    SNOMED_SYSTEM,
    FHIRDict,
    coding,
    make_id,
    now_iso,
    reference,
)


class FHIRComposition(BaseModel):
    title: str = Field(min_length=1)
    code: str = Field(min_length=1)
    display: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    author_ref: str = Field(min_length=1)
    encounter_ref: str = Field(min_length=1)
    sections: list[FHIRDict]
    custodian_ref: str | None = None
    date: str = Field(default_factory=now_iso)
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        resource = {
            "resourceType": "Composition",
            "id": self.id,
            "status": "final",
            "type": {
                "coding": [coding(SNOMED_SYSTEM, self.code, self.display)],
                "text": self.display,
            },
            "title": self.title,
            "date": self.date,
            "author": [reference(self.author_ref)],
            "subject": reference(self.patient_ref),
            "encounter": reference(self.encounter_ref),
            "section": self.sections,
        }
        if self.custodian_ref:
            resource["custodian"] = reference(self.custodian_ref)
        return resource
