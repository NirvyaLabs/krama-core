"""AiSensy WhatsApp provider."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from krama.whatsapp.providers.base import WhatsAppProvider
from krama.whatsapp.schemas import InboundMessage, MessageType, SendResult, TemplateMessage


class AiSensyProvider(WhatsAppProvider):
    """AiSensy REST API adapter."""

    def __init__(
        self,
        api_key: str,
        *,
        campaign_name: str = "default",
        base_url: str = "https://backend.aisensy.com",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.campaign_name = campaign_name
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def send_text(self, to: str, text: str) -> SendResult:
        response = await self._client.post(
            self._url("/campaign/t1/api/v2"),
            json={
                "apiKey": self.api_key,
                "campaignName": self.campaign_name,
                "destination": to,
                "userName": to,
                "templateParams": [text],
            },
        )
        return _result_from_response(response)

    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        response = await self._client.post(
            self._url("/campaign/t1/api/v2"),
            json={
                "apiKey": self.api_key,
                "campaignName": template.template_name,
                "destination": to,
                "userName": to,
                "templateParams": list(template.params.values()),
                "languageCode": template.language,
            },
        )
        return _result_from_response(response)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def parse_webhook(self, payload: dict) -> InboundMessage:
        message = payload.get("message", payload)
        sender = str(
            message.get("from")
            or payload.get("phone")
            or payload.get("waId")
            or payload.get("sender", "")
        )
        text = str(message.get("text") or payload.get("text") or "")
        timestamp = _parse_timestamp(message.get("timestamp") or payload.get("timestamp"))
        return InboundMessage(
            sender=sender,
            text=text,
            timestamp=timestamp,
            message_type=MessageType.TEXT if text else MessageType.UNKNOWN,
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
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)
