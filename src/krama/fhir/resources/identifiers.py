"""Patient identifier helpers for country-aware FHIR resources."""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from krama.fhir.resources.base import ABHA_SYSTEM, FHIRDict


class PatientIdentifierType(str, Enum):
    """Known patient identifier types supported by Krama."""

    INDIA_ABHA = "india_abha"
    INDIA_ABHA_ADDRESS = "india_abha_address"
    AUSTRALIA_IHI = "australia_ihi"
    AUSTRALIA_MRN = "australia_mrn"
    AUSTRALIA_MEDICARE = "australia_medicare"
    US_MRN = "us_mrn"
    US_MBI = "us_mbi"
    UK_NHS_NUMBER = "uk_nhs_number"
    UK_MRN = "uk_mrn"
    LOCAL_MRN = "local_mrn"
    CUSTOM = "custom"


NATIONAL_IDENTIFIER_SYSTEMS: dict[PatientIdentifierType, str] = {
    PatientIdentifierType.INDIA_ABHA: ABHA_SYSTEM,
    PatientIdentifierType.INDIA_ABHA_ADDRESS: ABHA_SYSTEM,
    PatientIdentifierType.AUSTRALIA_IHI: (
        "http://ns.electronichealth.net.au/id/hi/ihi/1.0"
    ),
    PatientIdentifierType.AUSTRALIA_MEDICARE: (
        "http://ns.electronichealth.net.au/id/medicare-number"
    ),
    PatientIdentifierType.US_MBI: "http://hl7.org/fhir/sid/us-mbi",
    PatientIdentifierType.UK_NHS_NUMBER: "https://fhir.nhs.uk/Id/nhs-number",
}


class PatientIdentifier(BaseModel):
    """FHIR Patient.identifier with country-aware defaults."""

    value: str = Field(min_length=1)
    type: PatientIdentifierType = PatientIdentifierType.CUSTOM
    system: str | None = None
    country: str | None = None
    assigner: str | None = None
    display: str | None = None

    @field_validator("value", "system", "country", "assigner", "display")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def resolve_system(self) -> PatientIdentifier:
        if self.system:
            return self

        default_system = NATIONAL_IDENTIFIER_SYSTEMS.get(self.type)
        if default_system:
            self.system = default_system
            return self

        if self.type in _LOCAL_IDENTIFIER_TYPES:
            if not self.assigner:
                raise ValueError("local MRN identifiers require system or assigner")
            self.system = _local_mrn_system(self.country, self.assigner)
            return self

        raise ValueError("custom identifiers require system")

    def to_fhir(self) -> FHIRDict:
        identifier: FHIRDict = {"system": self.system, "value": self.value}
        if self.display:
            identifier["type"] = {"text": self.display}
        if self.assigner:
            identifier["assigner"] = {"display": self.assigner}
        return identifier

    @classmethod
    def india_abha(cls, value: str) -> PatientIdentifier:
        return cls(value=value, type=PatientIdentifierType.INDIA_ABHA)

    @classmethod
    def india_abha_address(cls, value: str) -> PatientIdentifier:
        return cls(value=value, type=PatientIdentifierType.INDIA_ABHA_ADDRESS)

    @classmethod
    def australia_ihi(cls, value: str) -> PatientIdentifier:
        return cls(value=value, type=PatientIdentifierType.AUSTRALIA_IHI)

    @classmethod
    def australia_mrn(cls, value: str, assigner: str) -> PatientIdentifier:
        return cls(
            value=value,
            type=PatientIdentifierType.AUSTRALIA_MRN,
            country="AU",
            assigner=assigner,
            display="Medical Record Number",
        )

    @classmethod
    def us_mrn(cls, value: str, assigner: str) -> PatientIdentifier:
        return cls(
            value=value,
            type=PatientIdentifierType.US_MRN,
            country="US",
            assigner=assigner,
            display="Medical Record Number",
        )

    @classmethod
    def uk_nhs_number(cls, value: str) -> PatientIdentifier:
        return cls(value=value, type=PatientIdentifierType.UK_NHS_NUMBER)

    @classmethod
    def uk_mrn(cls, value: str, assigner: str) -> PatientIdentifier:
        return cls(
            value=value,
            type=PatientIdentifierType.UK_MRN,
            country="UK",
            assigner=assigner,
            display="Medical Record Number",
        )


_LOCAL_IDENTIFIER_TYPES = {
    PatientIdentifierType.AUSTRALIA_MRN,
    PatientIdentifierType.US_MRN,
    PatientIdentifierType.UK_MRN,
    PatientIdentifierType.LOCAL_MRN,
}


def _local_mrn_system(country: str | None, assigner: str) -> str:
    country_part = _slug(country or "global")
    assigner_part = _slug(assigner)
    return f"urn:krama:identifier:{country_part}:mrn:{assigner_part}"


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "unknown"
