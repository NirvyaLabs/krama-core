"""Outbound WhatsApp dispatcher."""

from __future__ import annotations

from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.schemas import SendResult, TemplateMessage


class WhatsAppSender:
    """Send outbound WhatsApp messages through the configured provider."""

    def __init__(self, provider: WhatsAppProvider) -> None:
        self._provider = provider

    async def send_text(self, to: str, text: str) -> SendResult:
        return await self._provider.send_text(to, text)

    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        return await self._provider.send_template(to, template)
