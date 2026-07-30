"""Gupshup WhatsApp provider."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.schemas import (
    InboundMessage,
    MessageType,
    SendResult,
    TemplateMessage,
)


class GupshupProvider(WhatsAppProvider):
    """Gupshup REST API adapter."""

    def __init__(
        self,
        api_key: str,
        source_number: str,
        *,
        app_name: str = "Krama",
        base_url: str = "https://api.gupshup.io",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.source_number = source_number
        self.app_name = app_name
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def send_text(self, to: str, text: str) -> SendResult:
        response = await self._client.post(
            self._url("/sm/api/v1/msg"),
            headers={"apikey": self.api_key},
            data={
                "channel": "whatsapp",
                "source": self.source_number,
                "destination": to,
                "src.name": self.app_name,
                "message": json.dumps({"type": "text", "text": text}),
            },
        )
        return _result_from_response(response)

    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        response = await self._client.post(
            self._url("/sm/api/v1/template/msg"),
            headers={"apikey": self.api_key},
            data={
                "channel": "whatsapp",
                "source": self.source_number,
                "destination": to,
                "src.name": self.app_name,
                "template": template.model_dump_json(),
            },
        )
        return _result_from_response(response)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def parse_webhook(self, payload: dict) -> InboundMessage:
        message = payload.get("payload", payload)
        sender = str(message.get("sender", {}).get("phone") or message.get("source", ""))
        content = message.get("payload", message)
        text = str(content.get("text") or message.get("text") or "")
        message_type = _message_type(str(message.get("type", "text")).lower())
        timestamp = _parse_timestamp(message.get("timestamp"))
        return InboundMessage(
            sender=sender,
            text=text,
            timestamp=timestamp,
            message_type=message_type,
            raw=payload,
        )


def _result_from_response(response: httpx.Response) -> SendResult:
    response.raise_for_status()
    payload = response.json()
    return SendResult(
        message_id=str(payload.get("messageId") or payload.get("id", "")),
        status=str(payload.get("status", "submitted")),
        raw=payload,
    )


def _parse_timestamp(value: object) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def _message_type(value: str) -> MessageType:
    try:
        return MessageType(value)
    except ValueError:
        return MessageType.UNKNOWN
