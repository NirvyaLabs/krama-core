"""Abstract WhatsApp provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from krama.whatsapp.schemas import InboundMessage, SendResult, TemplateMessage


class WhatsAppProvider(ABC):
    """Provider-neutral WhatsApp interface."""

    @abstractmethod
    async def send_text(self, to: str, text: str) -> SendResult:
        """Send a plain text WhatsApp message."""

    @abstractmethod
    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        """Send a provider-approved WhatsApp template message."""

    @abstractmethod
    def parse_webhook(self, payload: dict) -> InboundMessage:
        """Normalize an inbound webhook payload."""
