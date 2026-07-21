import asyncio

import httpx
import pytest

from krama.exceptions import TemplateNotFoundError, ValidationError
from krama.whatsapp import (
    TemplateMessage,
    WhatsAppSender,
    WhatsAppTemplate,
    WhatsAppTemplateStore,
    WhatsAppWebhookHandler,
)
from krama.whatsapp.providers import AiSensyProvider, GupshupProvider, MetaDirectProvider
from krama.whatsapp.schemas import MessageType, SendResult


def run(coro):
    return asyncio.run(coro)


class FakeProvider:
    async def send_text(self, to: str, text: str) -> SendResult:
        return SendResult(message_id=f"text-{to}", status="sent")

    async def send_template(self, to: str, template: TemplateMessage) -> SendResult:
        return SendResult(message_id=f"{template.template_name}-{to}", status="sent")

    def parse_webhook(self, payload: dict):
        raise NotImplementedError


def test_sender_routes_to_configured_provider():
    sender = WhatsAppSender(FakeProvider())

    text_result = run(sender.send_text("919876543210", "Hello"))
    template_result = run(
        sender.send_template(
            "919876543210",
            TemplateMessage(template_name="appointment", params={"name": "Ravi"}),
        )
    )

    assert text_result.message_id == "text-919876543210"
    assert template_result.message_id == "appointment-919876543210"


def test_aisensy_send_with_mocked_http():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(200, json={"messageId": "msg-1", "status": "sent"})

    provider = AiSensyProvider(
        "key",
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = run(provider.send_text("919876543210", "Hello"))

    assert result.message_id == "msg-1"
    assert seen["path"] == "/campaign/t1/api/v2"


def test_webhook_parsing_for_all_providers():
    aisensy = AiSensyProvider("key")
    gupshup = GupshupProvider("key", "917000000000")
    meta = MetaDirectProvider("token", "phone-id")

    parsed_aisensy = WhatsAppWebhookHandler(aisensy).handle(
        {"message": {"from": "919876543210", "text": "Hi", "timestamp": "1700000000"}}
    )
    parsed_gupshup = WhatsAppWebhookHandler(gupshup).handle(
        {
            "payload": {
                "sender": {"phone": "919876543211"},
                "type": "text",
                "payload": {"text": "Hello"},
                "timestamp": 1700000000000,
            }
        }
    )
    parsed_meta = WhatsAppWebhookHandler(meta).handle(
        {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "919876543212",
                                        "type": "text",
                                        "text": {"body": "Namaste"},
                                        "timestamp": "1700000000",
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    )

    assert parsed_aisensy.sender == "919876543210"
    assert parsed_aisensy.text == "Hi"
    assert parsed_gupshup.sender == "919876543211"
    assert parsed_gupshup.text == "Hello"
    assert parsed_meta.sender == "919876543212"
    assert parsed_meta.message_type == MessageType.TEXT


def test_template_rendering_and_validation():
    store = WhatsAppTemplateStore(
        [
            WhatsAppTemplate(
                name="appointment",
                body="Hello {{name}}, your visit is on {{date}}.",
            )
        ]
    )

    rendered = store.render("appointment", {"name": "Ravi", "date": "Monday"})

    assert rendered == "Hello Ravi, your visit is on Monday."
    assert store.list_templates() == ["appointment"]
    with pytest.raises(ValidationError, match="Missing"):
        store.render("appointment", {"name": "Ravi"})
    with pytest.raises(TemplateNotFoundError):
        store.get("missing")
