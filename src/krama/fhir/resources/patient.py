"""FHIR Patient resource builder."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from krama.fhir.resources.base import FHIRDict, make_id
from krama.fhir.resources.identifiers import PatientIdentifier


class FHIRPatient(BaseModel):
    abha_id: str | None = Field(default=None, min_length=1)
    identifiers: list[PatientIdentifier] = Field(default_factory=list)
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

    @model_validator(mode="after")
    def require_identifier(self) -> FHIRPatient:
        if not self.abha_id and not self.identifiers:
            raise ValueError("FHIRPatient requires abha_id or identifiers")
        return self

    def to_fhir(self) -> FHIRDict:
        identifiers = list(self.identifiers)
        if self.abha_id:
            identifiers.insert(0, PatientIdentifier.india_abha_address(self.abha_id))

        return {
            "resourceType": "Patient",
            "id": self.id,
            "meta": {
                "profile": [
                    "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"
                ]
            },
            "identifier": [identifier.to_fhir() for identifier in identifiers],
            "name": [{"text": self.name}],
            "gender": self.gender,
            "birthDate": self.birth_date,
        }
