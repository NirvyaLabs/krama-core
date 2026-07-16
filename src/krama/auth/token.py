"""ABDM OAuth token management."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Protocol

from pydantic import SecretStr

from krama.exceptions import AuthenticationError


class TokenHttpClient(Protocol):
    async def post(self, path: str, **kwargs) -> dict: ...


Clock = Callable[[], float]


class ABDMTokenManager:
    """Fetch and cache ABDM access tokens with concurrent refresh protection."""

    def __init__(
        self,
        http_client: TokenHttpClient,
        client_id: str,
        client_secret: SecretStr,
        *,
        clock: Clock = time.time,
        refresh_margin_seconds: int = 60,
    ) -> None:
        self._http = http_client
        self._client_id = client_id
        self._client_secret = client_secret
        self._clock = clock
        self._refresh_margin_seconds = refresh_margin_seconds
        self._token: str | None = None
        self._expires_at = 0.0
        self._refresh_lock = asyncio.Lock()

    async def get_token(self) -> str:
        if self._has_valid_token():
            return self._token or ""

        async with self._refresh_lock:
            if not self._has_valid_token():
                await self._fetch_token()

        return self._token or ""

    def clear(self) -> None:
        self._token = None
        self._expires_at = 0.0

    def _has_valid_token(self) -> bool:
        return bool(
            self._token
            and self._clock() < (self._expires_at - self._refresh_margin_seconds)
        )

    async def _fetch_token(self) -> None:
        response = await self._http.post(
            "/gateway/v0.5/sessions",
            auth_required=False,
            json={
                "clientId": self._client_id,
                "clientSecret": self._client_secret.get_secret_value(),
            },
        )

        token = response.get("accessToken")
        if not isinstance(token, str) or not token:
            raise AuthenticationError("ABDM token response did not include accessToken")

        expires_in = response.get("expiresIn", 1200)
        if not isinstance(expires_in, (int, float)) or expires_in <= 0:
            raise AuthenticationError("ABDM token response included invalid expiresIn")

        self._token = token
        self._expires_at = self._clock() + float(expires_in)
