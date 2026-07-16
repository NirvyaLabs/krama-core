"""ABHA data models and validation helpers."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ABHAInitResult(BaseModel):
    transaction_id: str = Field(min_length=1)
    message: str = ""


class ABHAProfile(BaseModel):
    abha_number: str
    abha_address: str
    name: str = Field(min_length=1)
    date_of_birth: date
    gender: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    state: str | None = None
    district: str | None = None
    photo: str | None = None

    @field_validator("abha_number")
    @classmethod
    def validate_abha_number(cls, value: str) -> str:
        cleaned = normalize_abha_number(value)
        if len(cleaned) != 14:
            raise ValueError("ABHA number must contain exactly 14 digits")
        return value

    @field_validator("abha_address")
    @classmethod
    def validate_abha_address(cls, value: str) -> str:
        if "@" not in value or len(value) > 255:
            raise ValueError("ABHA address must look like name@provider")
        return value.lower().strip()

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        gender = value.upper().strip()
        if gender not in {"M", "F", "O", "U"}:
            raise ValueError("gender must be one of M, F, O, U")
        return gender


def normalize_aadhaar(value: str) -> str:
    cleaned = value.replace(" ", "").replace("-", "")
    if not cleaned.isdigit() or len(cleaned) != 12:
        raise ValueError("Aadhaar must contain exactly 12 digits")
    return cleaned


def normalize_mobile(value: str) -> str:
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not cleaned.isdigit() or len(cleaned) != 10 or cleaned[0] not in "6789":
        raise ValueError("Indian mobile number must contain 10 digits")
    return cleaned


def normalize_otp(value: str) -> str:
    cleaned = value.strip().replace(" ", "")
    if not cleaned.isdigit() or not 4 <= len(cleaned) <= 8:
        raise ValueError("OTP must contain 4 to 8 digits")
    return cleaned


def normalize_abha_number(value: str) -> str:
    cleaned = value.replace(" ", "").replace("-", "")
    if not cleaned.isdigit() or len(cleaned) != 14:
        raise ValueError("ABHA number must contain exactly 14 digits")
    return cleaned


def profile_from_gateway(payload: dict[str, Any]) -> ABHAProfile:
    return ABHAProfile(
        abha_number=str(payload.get("abhaNumber") or payload.get("healthIdNumber", "")),
        abha_address=str(payload.get("abhaAddress") or payload.get("healthId", "")),
        name=str(payload.get("name", "")),
        date_of_birth=payload.get("dateOfBirth") or payload.get("dob"),
        gender=str(payload.get("gender", "U")),
        phone=payload.get("phone") or payload.get("mobile"),
        email=payload.get("email"),
        address=payload.get("address"),
        state=payload.get("state"),
        district=payload.get("district"),
        photo=payload.get("photo"),
    )
