"""ABHA Milestone 1 client."""

from __future__ import annotations

from typing import Protocol

from krama.abha.schemas import (
    ABHAInitResult,
    ABHAProfile,
    normalize_aadhaar,
    normalize_abha_number,
    normalize_mobile,
    normalize_otp,
    profile_from_gateway,
)
from krama.exceptions import ValidationError


class ABDMRequestClient(Protocol):
    async def get(self, path: str, **kwargs) -> dict: ...
    async def post(self, path: str, **kwargs) -> dict: ...


class ABHAClient:
    """Client for ABHA creation, verification, and profile operations."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def __init__(self, http_client: ABDMRequestClient) -> None:
        self._http = http_client

    async def create_via_aadhaar(self, aadhaar: str) -> ABHAInitResult:
        response = await self._http.post(
            "/v1/registration/aadhaar/generateOtp",
            json={"aadhaar": normalize_aadhaar(aadhaar)},
        )
        return self._init_result(response)

    async def verify_aadhaar_otp(self, transaction_id: str, otp: str) -> ABHAProfile:
        response = await self._http.post(
            "/v1/registration/aadhaar/verifyOTP",
            json={
                "txnId": self._clean_transaction_id(transaction_id),
                "otp": normalize_otp(otp),
            },
        )
        return profile_from_gateway(response)

    async def create_via_mobile(self, mobile: str) -> ABHAInitResult:
        response = await self._http.post(
            "/v1/registration/mobile/generateOtp",
            json={"mobile": normalize_mobile(mobile)},
        )
        return self._init_result(response)

    async def verify_mobile_otp(self, transaction_id: str, otp: str) -> ABHAProfile:
        response = await self._http.post(
            "/v1/registration/mobile/verifyOTP",
            json={
                "txnId": self._clean_transaction_id(transaction_id),
                "otp": normalize_otp(otp),
            },
        )
        return profile_from_gateway(response)

    async def verify_abha(self, abha_number: str) -> ABHAProfile:
        response = await self._http.post(
            "/v1/search/existsByHealthIdNumber",
            json={"healthIdNumber": normalize_abha_number(abha_number)},
        )
        return profile_from_gateway(response)

    async def search_by_health_id(self, abha_address: str) -> ABHAProfile:
        address = abha_address.strip().lower()
        if "@" not in address:
            raise ValidationError("ABHA address must look like name@provider")
        response = await self._http.post(
            "/v1/search/searchByHealthId",
            json={"healthId": address},
        )
        return profile_from_gateway(response)

    async def fetch_profile(self, abha_number: str) -> ABHAProfile:
        response = await self._http.get(
            f"/v1/account/profile/{normalize_abha_number(abha_number)}"
        )
        return profile_from_gateway(response)

    def _init_result(self, response: dict) -> ABHAInitResult:
        return ABHAInitResult(
            transaction_id=str(response.get("txnId") or response.get("transactionId", "")),
            message=str(response.get("message", "")),
        )

    def _clean_transaction_id(self, transaction_id: str) -> str:
        cleaned = transaction_id.strip()
        if not cleaned or len(cleaned) > 128:
            raise ValidationError("transaction_id must be present and under 128 chars")
        return cleaned
