"""FHIR Practitioner resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FHIRDict, PRACTITIONER_SYSTEM, make_id


class FHIRPractitioner(BaseModel):
    identifier: str = Field(min_length=1)
    name: str = Field(min_length=1)
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        return {
            "resourceType": "Practitioner",
            "id": self.id,
            "meta": {
                "profile": [
                    "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Practitioner"
                ]
            },
            "identifier": [{"system": PRACTITIONER_SYSTEM, "value": self.identifier}],
            "name": [{"text": self.name}],
        }
