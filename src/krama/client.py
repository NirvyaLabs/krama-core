"""Main Krama SDK client."""

from __future__ import annotations

from pydantic import SecretStr

from krama.abha import ABHAClient
from krama.adapters import (
    AustraliaAdapter,
    CountryAdapter,
    IndiaAdapter,
    UKAdapter,
    USAdapter,
)
from krama.ai import AIAssistant
from krama.ai.providers.router import LLMRouter
from krama.auth import ABDMTokenManager
from krama.compliance import ComplianceEngine
from krama.config import KramaConfig
from krama.exceptions import ConfigurationError
from krama.gateway import GatewayHealthClient
from krama.hip import HIPClient
from krama.hiu import HIUClient
from krama.templates import TemplateRegistry
from krama.utils.http import ABDMHttpClient
from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.sender import WhatsAppSender


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
        whatsapp_provider = kwargs.pop("whatsapp_provider", None)
        ai_router = kwargs.pop("ai_router", None)
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
        self.hip = HIPClient(self.http)
        self.hiu = HIUClient(self.http)
        self.templates = TemplateRegistry()
        self.compliance = ComplianceEngine()
        self.gateway_health = GatewayHealthClient(self.http)
        self.whatsapp = _build_whatsapp(whatsapp_provider)
        self.ai = _build_ai(ai_router)

    def adapter(self, country: str = "IND") -> CountryAdapter:
        code = country.strip().upper()
        if code in {"IND", "IN", "INDIA"}:
            return IndiaAdapter(abha=self.abha, hip=self.hip, hiu=self.hiu)
        if code in {"AUS", "AU", "AUSTRALIA"}:
            return AustraliaAdapter()
        if code in {"USA", "US", "UNITED_STATES", "UNITED STATES"}:
            return USAdapter()
        if code in {"GBR", "GB", "UK", "UNITED_KINGDOM", "UNITED KINGDOM"}:
            return UKAdapter()
        raise ConfigurationError(f"Unsupported country adapter: {country}")

    async def close(self) -> None:
        await self.http.close()

    async def __aenter__(self) -> "KramaClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


async def _default_sleep(delay: float) -> None:
    import asyncio

    await asyncio.sleep(delay)


def _build_whatsapp(provider: WhatsAppProvider | None) -> WhatsAppSender | None:
    if provider is None:
        return None
    return WhatsAppSender(provider)


def _build_ai(router: LLMRouter | None) -> AIAssistant | None:
    if router is None:
        return None
    return AIAssistant(router)


__all__ = ["KramaClient"]
