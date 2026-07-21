"""FHIR Patient resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from krama.fhir.resources.base import ABHA_SYSTEM, FHIRDict, make_id


class FHIRPatient(BaseModel):
    abha_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    gender: str
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    id: str = Field(default_factory=make_id)

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        gender = value.lower().strip()
        if gender not in {"male", "female", "other", "unknown"}:
            raise ValueError("gender must be male, female, other, or unknown")
        return gender

    def to_fhir(self) -> FHIRDict:
        return {
            "resourceType": "Patient",
            "id": self.id,
            "meta": {
                "profile": [
                    "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"
                ]
            },
            "identifier": [{"system": ABHA_SYSTEM, "value": self.abha_id}],
            "name": [{"text": self.name}],
            "gender": self.gender,
            "birthDate": self.birth_date,
        }
