"""WhatsApp data models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class InboundMessage(BaseModel):
    sender: str = Field(min_length=1)
    text: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_type: MessageType = MessageType.TEXT
    raw: dict = Field(default_factory=dict)


class SendResult(BaseModel):
    message_id: str = ""
    status: str = Field(default="submitted", min_length=1)
    raw: dict = Field(default_factory=dict)


class TemplateMessage(BaseModel):
    template_name: str = Field(min_length=1)
    params: dict[str, str] = Field(default_factory=dict)
    language: str = "en"

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        return value.strip() or "en"
