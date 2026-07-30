"""Async HTTP client used by Krama SDK modules."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from krama.config import KramaConfig
from krama.exceptions import ABDMGatewayError, KramaError

TokenProvider = Callable[[], Awaitable[str]]
SleepFunc = Callable[[float], Awaitable[None]]


class ABDMHttpClient:
    """Small async ABDM Gateway client with auth injection and retry."""

    _ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    def __init__(
        self,
        config: KramaConfig,
        *,
        token_provider: TokenProvider | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: SleepFunc = asyncio.sleep,
    ) -> None:
        self.config = config
        self._token_provider = token_provider
        self._sleep = sleep
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            transport=transport,
        )

    def set_token_provider(self, token_provider: TokenProvider | None) -> None:
        self._token_provider = token_provider

    async def close(self) -> None:
        await self._client.aclose()

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("POST", path, **kwargs)

    async def request(
        self,
        method: str,
        path: str,
        *,
        auth_required: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        method = method.upper()
        if method not in self._ALLOWED_METHODS:
            raise ValueError(f"Unsupported HTTP method: {method}")
        if "://" in path or not path.startswith("/"):
            raise ValueError("path must be a relative absolute path, e.g. /v1/status")

        headers = dict(kwargs.pop("headers", {}) or {})
        if auth_required:
            if self._token_provider is None:
                raise KramaError("authenticated request requires a token provider")
            headers["Authorization"] = f"Bearer {await self._token_provider()}"

        attempts = self.config.max_retries + 1
        for attempt in range(attempts):
            try:
                response = await self._client.request(
                    method,
                    path,
                    headers=headers,
                    **kwargs,
                )
            except httpx.TransportError as exc:
                if attempt == attempts - 1:
                    raise KramaError("ABDM Gateway transport error") from exc
                await self._sleep(self._retry_delay(attempt))
                continue

            if response.status_code >= 500 and attempt < attempts - 1:
                await self._sleep(self._retry_delay(attempt))
                continue

            return self._parse_response(response)

        raise KramaError("ABDM Gateway request failed after retries")

    def _retry_delay(self, attempt: int) -> float:
        return self.config.retry_base_delay * (2**attempt)

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        request_id = response.headers.get("x-request-id", "")
        if response.status_code >= 400:
            raise ABDMGatewayError(
                status_code=response.status_code,
                message=self._safe_error_message(response),
                request_id=request_id,
            )

        if response.status_code == 204 or not response.content:
            return {}

        try:
            parsed = response.json()
        except ValueError as exc:
            raise KramaError("ABDM Gateway returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise KramaError("ABDM Gateway returned non-object JSON")
        return parsed

    def _safe_error_message(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.reason_phrase or "request failed"

        if isinstance(payload, dict):
            for key in ("message", "error", "error_description"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return self._redact(value[:300])
        return response.reason_phrase or "request failed"

    def _redact(self, message: str) -> str:
        secret = self.config.client_secret.get_secret_value()
        if secret:
            return message.replace(secret, "[REDACTED]")
        return message
