"""HIU Milestone 3 data models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ConsentState(str, Enum):
    REQUESTED = "REQUESTED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class ConsentRequest(BaseModel):
    patient_abha: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    hiu_id: str = Field(min_length=1)
    date_range_from: str = Field(min_length=1)
    date_range_to: str = Field(min_length=1)
    data_types: list[str] = Field(default_factory=lambda: ["OPConsultRecord"])

    @field_validator("patient_abha")
    @classmethod
    def normalize_patient_abha(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("patient_abha must be an ABHA address")
        return normalized


class ConsentRecord(BaseModel):
    consent_id: str = Field(min_length=1)
    patient_abha: str
    status: ConsentState
    raw: dict[str, Any] = Field(default_factory=dict)


class DataRequest(BaseModel):
    consent_id: str = Field(min_length=1)
    transaction_id: str | None = None
    from_date: str | None = None
    to_date: str | None = None


class DataRequestResult(BaseModel):
    request_id: str = Field(min_length=1)
    transaction_id: str = Field(min_length=1)
    status: str = "REQUESTED"


class EncryptedHealthData(BaseModel):
    ciphertext: str = Field(min_length=1)
    nonce: str = Field(min_length=1)
    sender_public_key: str = Field(min_length=1)
    receiver_private_key: str = Field(min_length=1)
    salt: str | None = None
    associated_data: str | None = None


class ReceivedHealthData(BaseModel):
    bundle: dict[str, Any]
    raw: dict[str, Any]
