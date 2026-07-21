"""Receive and decrypt HIU health data payloads."""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any

from krama.crypto import AESGCMCipher, ECDHKeyExchange
from krama.exceptions import EncryptionError, FHIRValidationError
from krama.hiu.schemas import EncryptedHealthData, ReceivedHealthData


class DataReceiver:
    """Decrypt encrypted health data from HIPs and parse FHIR bundles."""

    def receive_data(self, encrypted_data: EncryptedHealthData) -> ReceivedHealthData:
        key = self._derive_key(encrypted_data)
        plaintext = AESGCMCipher.decrypt(
            ciphertext=self._b64decode(encrypted_data.ciphertext, "ciphertext"),
            key=key,
            nonce=self._b64decode(encrypted_data.nonce, "nonce"),
            associated_data=self._optional_b64decode(encrypted_data.associated_data),
        )
        payload = self._parse_json(plaintext)
        bundle = payload.get("bundle", payload)
        self._validate_bundle(bundle)
        return ReceivedHealthData(bundle=bundle, raw=payload)

    def _derive_key(self, encrypted_data: EncryptedHealthData) -> bytes:
        shared_secret = ECDHKeyExchange.derive_shared_secret(
            our_private=self._b64decode(
                encrypted_data.receiver_private_key,
                "receiver_private_key",
            ),
            their_public=self._b64decode(
                encrypted_data.sender_public_key,
                "sender_public_key",
            ),
        )
        return AESGCMCipher.derive_key(
            shared_secret,
            salt=self._optional_b64decode(encrypted_data.salt),
        )

    def _parse_json(self, plaintext: bytes) -> dict[str, Any]:
        try:
            payload = json.loads(plaintext.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EncryptionError("decrypted payload is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise EncryptionError("decrypted payload must be a JSON object")
        return payload

    def _validate_bundle(self, bundle: Any) -> None:
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            raise FHIRValidationError("decrypted payload must contain a FHIR Bundle")

    def _b64decode(self, value: str, field_name: str) -> bytes:
        try:
            return base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise EncryptionError(f"{field_name} must be valid base64") from exc

    def _optional_b64decode(self, value: str | None) -> bytes | None:
        if value is None:
            return None
        return self._b64decode(value, "associated data")
