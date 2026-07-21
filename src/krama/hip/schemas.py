"""HIP Milestone 2 data models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DiscoveryStatus(str, Enum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class CareContextStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class CareContext(BaseModel):
    reference: str = Field(min_length=1)
    display: str = Field(min_length=1)
    patient_abha: str = Field(min_length=1)
    status: CareContextStatus = CareContextStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("patient_abha")
    @classmethod
    def normalize_patient_abha(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("patient_abha must be an ABHA address")
        return normalized


class DiscoveryRequest(BaseModel):
    request_id: str = Field(min_length=1)
    transaction_id: str = Field(min_length=1)
    patient_abha: str = Field(min_length=1)
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator("patient_abha")
    @classmethod
    def normalize_patient_abha(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("patient_abha must be an ABHA address")
        return normalized


class DiscoveryAcknowledgement(BaseModel):
    request_id: str
    status: DiscoveryStatus = DiscoveryStatus.ACKNOWLEDGED
    queued: bool = True


class DiscoveryMatch(BaseModel):
    patient_abha: str
    care_contexts: list[CareContext] = Field(default_factory=list)


class LinkResult(BaseModel):
    patient_abha: str
    care_context_reference: str
    linked: bool
    message: str = ""


class PublishResult(BaseModel):
    patient_abha: str
    care_context_reference: str
    notified: bool
    message: str = ""
