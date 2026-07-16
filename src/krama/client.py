"""Main Krama SDK client."""

from __future__ import annotations

from pydantic import SecretStr

from krama.abha import ABHAClient
from krama.auth import ABDMTokenManager
from krama.config import KramaConfig
from krama.utils.http import ABDMHttpClient


class KramaClient:
    """Async SDK entry point for ABDM integrations."""

    def __init__(
        self,
        client_id: str,
        client_secret: str | SecretStr,
        **kwargs,
    ) -> None:
        transport = kwargs.pop("transport", None)
        sleep = kwargs.pop("sleep", None)
        secret = (
            client_secret
            if isinstance(client_secret, SecretStr)
            else SecretStr(client_secret)
        )

        self.config = KramaConfig(
            client_id=client_id,
            client_secret=secret,
            **kwargs,
        )
        self.http = ABDMHttpClient(
            self.config,
            transport=transport,
            sleep=sleep or _default_sleep,
        )
        self.tokens = ABDMTokenManager(
            self.http,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
        )
        self.http.set_token_provider(self.tokens.get_token)

        self.abha = ABHAClient(self.http)

    async def close(self) -> None:
        await self.http.close()

    async def __aenter__(self) -> "KramaClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


async def _default_sleep(delay: float) -> None:
    import asyncio

    await asyncio.sleep(delay)


__all__ = ["KramaClient"]
