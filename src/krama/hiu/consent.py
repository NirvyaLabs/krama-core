"""HIU consent management."""

from __future__ import annotations

from typing import Protocol

from krama.hiu.schemas import ConsentRecord, ConsentRequest, ConsentState


class HIUHttpClient(Protocol):
    async def get(self, path: str, **kwargs) -> dict: ...
    async def post(self, path: str, **kwargs) -> dict: ...


class ConsentManager:
    """Request, inspect, and update patient consent state."""

    def __init__(self, http_client: HIUHttpClient) -> None:
        self._http = http_client

    async def request_consent(self, request: ConsentRequest) -> ConsentRecord:
        response = await self._http.post(
            "/v1/hiu/consents/request",
            json=request.model_dump(mode="json"),
        )
        return self._record_from_response(response, request.patient_abha)

    async def check_status(self, consent_id: str) -> ConsentRecord:
        response = await self._http.get(f"/v1/hiu/consents/{consent_id}")
        return self._record_from_response(response, response.get("patient_abha", ""))

    async def revoke(self, consent_id: str) -> ConsentRecord:
        response = await self._http.post(
            f"/v1/hiu/consents/{consent_id}/revoke",
            json={},
        )
        return self.handle_revoke(response)

    def handle_grant(self, payload: dict) -> ConsentRecord:
        return self._event_record(payload, ConsentState.GRANTED)

    def handle_revoke(self, payload: dict) -> ConsentRecord:
        return self._event_record(payload, ConsentState.REVOKED)

    def handle_expire(self, payload: dict) -> ConsentRecord:
        return self._event_record(payload, ConsentState.EXPIRED)

    def _record_from_response(
        self,
        response: dict,
        fallback_patient_abha: str,
    ) -> ConsentRecord:
        return ConsentRecord(
            consent_id=str(response.get("consent_id") or response.get("consentId", "")),
            patient_abha=str(response.get("patient_abha") or fallback_patient_abha),
            status=ConsentState(response.get("status", ConsentState.REQUESTED)),
            raw=response,
        )

    def _event_record(self, payload: dict, state: ConsentState) -> ConsentRecord:
        return ConsentRecord(
            consent_id=str(payload.get("consent_id") or payload.get("consentId", "")),
            patient_abha=str(payload.get("patient_abha", "")),
            status=ConsentState(payload.get("status", state)),
            raw=payload,
        )
