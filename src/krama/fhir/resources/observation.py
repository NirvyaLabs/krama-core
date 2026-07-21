"""FHIR Observation resource builder."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from krama.fhir.resources.base import FHIRDict, LOINC_SYSTEM, coding, make_id, reference


class FHIRObservation(BaseModel):
    code: str = Field(min_length=1)
    display: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    value: str | int | float | bool
    unit: str = ""
    status: str = "final"
    system: str = LOINC_SYSTEM
    id: str = Field(default_factory=make_id)

    def to_fhir(self) -> FHIRDict:
        resource: FHIRDict = {
            "resourceType": "Observation",
            "id": self.id,
            "status": self.status,
            "code": {"coding": [coding(self.system, self.code, self.display)]},
            "subject": reference(self.patient_ref),
        }
        resource.update(self._value_field())
        return resource

    def _value_field(self) -> FHIRDict:
        if isinstance(self.value, bool):
            return {"valueBoolean": self.value}
        if isinstance(self.value, int | float):
            quantity: dict[str, Any] = {"value": self.value}
            if self.unit:
                quantity["unit"] = self.unit
            return {"valueQuantity": quantity}
        return {"valueString": str(self.value)}
