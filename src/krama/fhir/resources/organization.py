"""FHIR Organization resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FACILITY_SYSTEM, FHIRDict, make_id


class FHIROrganization(BaseModel):
    hfr_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        return {
            "resourceType": "Organization",
            "id": self.id,
            "meta": {
                "profile": [
                    "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Organization"
                ]
            },
            "identifier": [{"system": FACILITY_SYSTEM, "value": self.hfr_id}],
            "name": self.name,
        }
