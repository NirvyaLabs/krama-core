"""Meta WhatsApp Cloud API provider."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.schemas import (
    InboundMessage,
    MessageType,
    SendResult,
    TemplateMessage,
)


class MetaDirectProvider(WhatsAppProvider):
    """Direct Meta Cloud API adapter."""

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        *,
        api_version: str = "v20.0",
        base_url: str = "https://graph.facebook.com",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def send_text(self, to: str, text: str) -> SendResult:
        response = await self._client.post(
            self._url(f"/{self.api_version}/{self.phone_number_id}/messages"),
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
        )
        return _result_from_response(response)

    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        response = await self._client.post(
            self._url(f"/{self.api_version}/{self.phone_number_id}/messages"),
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template.template_name,
                    "language": {"code": template.language},
                    "components": _template_components(template),
                },
            },
        )
        return _result_from_response(response)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def parse_webhook(self, payload: dict) -> InboundMessage:
        value = (
            payload.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
        )
        message = (value.get("messages") or [{}])[0]
        message_type = _message_type(str(message.get("type", "unknown")).lower())
        text = ""
        if message_type == MessageType.TEXT:
            text = str(message.get("text", {}).get("body", ""))
        sender = str(message.get("from", ""))
        timestamp = _parse_timestamp(message.get("timestamp"))
        return InboundMessage(
            sender=sender,
            text=text,
            timestamp=timestamp,
            message_type=message_type,
            raw=payload,
        )


def _template_components(template: TemplateMessage) -> list[dict]:
    values = [{"type": "text", "text": value} for value in template.params.values()]
    if not values:
        return []
    return [{"type": "body", "parameters": values}]


def _result_from_response(response: httpx.Response) -> SendResult:
    response.raise_for_status()
    payload = response.json()
    messages = payload.get("messages") or [{}]
    return SendResult(
        message_id=str(messages[0].get("id") or payload.get("id", "")),
        status=str(payload.get("status", "submitted")),
        raw=payload,
    )


def _parse_timestamp(value: object) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def _message_type(value: str) -> MessageType:
    try:
        return MessageType(value)
    except ValueError:
        return MessageType.UNKNOWN
