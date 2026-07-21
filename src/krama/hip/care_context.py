"""HIP care context management."""

from __future__ import annotations

from typing import Protocol

from krama.hip.schemas import CareContext


class HIPHttpClient(Protocol):
    async def get(self, path: str, **kwargs) -> dict: ...
    async def post(self, path: str, **kwargs) -> dict: ...
    async def request(self, method: str, path: str, **kwargs) -> dict: ...


class CareContextClient:
    """Create, read, update, and delete HIP care contexts."""

    def __init__(self, http_client: HIPHttpClient) -> None:
        self._http = http_client

    async def create(self, care_context: CareContext) -> CareContext:
        response = await self._http.post(
            "/v1/hip/care-contexts",
            json=care_context.model_dump(mode="json"),
        )
        return self._parse_response(response, care_context)

    async def get(self, reference: str) -> CareContext:
        response = await self._http.get(f"/v1/hip/care-contexts/{reference}")
        return CareContext.model_validate(response)

    async def update(self, care_context: CareContext) -> CareContext:
        response = await self._http.request(
            "PUT",
            f"/v1/hip/care-contexts/{care_context.reference}",
            json=care_context.model_dump(mode="json"),
        )
        return self._parse_response(response, care_context)

    async def delete(self, reference: str) -> bool:
        await self._http.request("DELETE", f"/v1/hip/care-contexts/{reference}")
        return True

    def _parse_response(
        self,
        response: dict,
        fallback: CareContext,
    ) -> CareContext:
        payload = response.get("careContext", response)
        if not payload:
            return fallback
        return CareContext.model_validate(payload)
