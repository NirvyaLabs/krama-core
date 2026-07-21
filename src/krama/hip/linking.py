"""HIP care context linking operations."""

from __future__ import annotations

from krama.hip.care_context import HIPHttpClient
from krama.hip.schemas import CareContext, LinkResult


class HIPLinkingClient:
    """Link and unlink care contexts for a patient."""

    def __init__(self, http_client: HIPHttpClient) -> None:
        self._http = http_client

    async def link(self, care_context: CareContext) -> LinkResult:
        response = await self._http.post(
            "/v1/hip/care-contexts/link",
            json=care_context.model_dump(mode="json"),
        )
        return LinkResult(
            patient_abha=care_context.patient_abha,
            care_context_reference=care_context.reference,
            linked=bool(response.get("linked", True)),
            message=str(response.get("message", "")),
        )

    async def unlink(self, patient_abha: str, care_context_reference: str) -> LinkResult:
        response = await self._http.post(
            "/v1/hip/care-contexts/unlink",
            json={
                "patient_abha": patient_abha.strip().lower(),
                "care_context_reference": care_context_reference,
            },
        )
        return LinkResult(
            patient_abha=patient_abha.strip().lower(),
            care_context_reference=care_context_reference,
            linked=not bool(response.get("unlinked", True)),
            message=str(response.get("message", "")),
        )
