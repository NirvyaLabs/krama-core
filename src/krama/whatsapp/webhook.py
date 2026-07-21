"""Provider-neutral WhatsApp webhook handling."""

from __future__ import annotations

from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.schemas import InboundMessage


class WhatsAppWebhookHandler:
    """Normalize inbound WhatsApp messages from a configured provider."""

    def __init__(self, provider: WhatsAppProvider) -> None:
        self._provider = provider

    def handle(self, payload: dict) -> InboundMessage:
        return self._provider.parse_webhook(payload)
