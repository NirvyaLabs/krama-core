"""HIU health data request operations."""

from __future__ import annotations

from krama.hiu.consent import HIUHttpClient
from krama.hiu.schemas import DataRequest, DataRequestResult


class DataRequester:
    """Request health data using an approved consent artifact."""

    def __init__(self, http_client: HIUHttpClient) -> None:
        self._http = http_client

    async def request_data(self, request: DataRequest) -> DataRequestResult:
        response = await self._http.post(
            "/v1/hiu/health-information/request",
            json=request.model_dump(mode="json", exclude_none=True),
        )
        return DataRequestResult(
            request_id=str(response.get("request_id") or response.get("requestId", "")),
            transaction_id=str(
                response.get("transaction_id") or response.get("transactionId", "")
            ),
            status=str(response.get("status", "REQUESTED")),
        )
