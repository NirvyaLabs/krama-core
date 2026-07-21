"""Gateway health checks."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Protocol

from pydantic import BaseModel, Field


class GatewayRequestClient(Protocol):
    async def get(self, path: str, **kwargs) -> dict: ...


class GatewayHealthStatus(BaseModel):
    """Current gateway connectivity status."""

    connected: bool
    latency: float | None = Field(default=None, description="Latency in seconds")
    last_successful_call: datetime | None = None
    error: str = ""


class GatewayHealthClient:
    """Check whether the configured gateway is reachable."""

    def __init__(
        self,
        http_client: GatewayRequestClient,
        *,
        health_path: str = "/v1/health",
    ) -> None:
        self._http = http_client
        self.health_path = health_path
        self.last_successful_call: datetime | None = None

    async def check(self) -> GatewayHealthStatus:
        started = time.perf_counter()
        try:
            await self._http.get(self.health_path, auth_required=False)
        except Exception as exc:
            return GatewayHealthStatus(
                connected=False,
                latency=None,
                last_successful_call=self.last_successful_call,
                error=str(exc),
            )

        latency = time.perf_counter() - started
        self.last_successful_call = datetime.now(timezone.utc)
        return GatewayHealthStatus(
            connected=True,
            latency=latency,
            last_successful_call=self.last_successful_call,
        )
