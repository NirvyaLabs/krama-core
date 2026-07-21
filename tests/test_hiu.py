import asyncio
import base64
import json

import pytest

from krama.crypto import AESGCMCipher, ECDHKeyExchange
from krama.exceptions import EncryptionError, FHIRValidationError
from krama.hiu import (
    ConsentManager,
    ConsentRequest,
    ConsentState,
    DataReceiver,
    DataRequest,
    DataRequester,
    EncryptedHealthData,
    HIUClient,
)


def run(coro):
    return asyncio.run(coro)


class FakeHTTP:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    async def get(self, path: str, **kwargs):
        self.calls.append(("GET", path, kwargs))
        return self._next_response()

    async def post(self, path: str, **kwargs):
        self.calls.append(("POST", path, kwargs))
        return self._next_response()

    def _next_response(self):
        if self.responses:
            return self.responses.pop(0)
        return {}


def sample_consent_request():
    return ConsentRequest(
        patient_abha="RAVI.KUMAR@ABDM",
        purpose="Care management",
        hiu_id="nirvya-hiu",
        date_range_from="2026-01-01",
        date_range_to="2026-12-31",
    )


def sample_bundle():
    return {
        "resourceType": "Bundle",
        "type": "document",
        "entry": [{"resource": {"resourceType": "Composition"}}],
    }


def b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def encrypted_payload(payload: dict, associated_data: bytes | None = None):
    sender_private, sender_public = ECDHKeyExchange.generate_key_pair()
    receiver_private, receiver_public = ECDHKeyExchange.generate_key_pair()
    sender_secret = ECDHKeyExchange.derive_shared_secret(
        sender_private,
        receiver_public,
    )
    key = AESGCMCipher.derive_key(sender_secret)
    ciphertext, nonce = AESGCMCipher.encrypt(
        json.dumps(payload).encode("utf-8"),
        key,
        associated_data=associated_data,
    )
    return EncryptedHealthData(
        ciphertext=b64(ciphertext),
        nonce=b64(nonce),
        sender_public_key=b64(sender_public),
        receiver_private_key=b64(receiver_private),
        associated_data=b64(associated_data) if associated_data else None,
    )


def test_consent_request_normalizes_patient_abha_and_rejects_bad_address():
    request = sample_consent_request()

    assert request.patient_abha == "ravi.kumar@abdm"

    with pytest.raises(ValueError, match="ABHA"):
        ConsentRequest(
            patient_abha="bad",
            purpose="Care",
            hiu_id="hiu",
            date_range_from="2026-01-01",
            date_range_to="2026-12-31",
        )


def test_consent_manager_request_check_revoke_and_events():
    http = FakeHTTP(
        [
            {
                "consentId": "consent-1",
                "patient_abha": "ravi.kumar@abdm",
                "status": "REQUESTED",
            },
            {
                "consent_id": "consent-1",
                "patient_abha": "ravi.kumar@abdm",
                "status": "GRANTED",
            },
            {
                "consent_id": "consent-1",
                "patient_abha": "ravi.kumar@abdm",
                "status": "REVOKED",
            },
        ]
    )
    manager = ConsentManager(http)

    requested = run(manager.request_consent(sample_consent_request()))
    granted = run(manager.check_status("consent-1"))
    revoked = run(manager.revoke("consent-1"))
    expired = manager.handle_expire(
        {"consent_id": "consent-1", "patient_abha": "ravi.kumar@abdm"}
    )

    assert requested.status == ConsentState.REQUESTED
    assert granted.status == ConsentState.GRANTED
    assert revoked.status == ConsentState.REVOKED
    assert expired.status == ConsentState.EXPIRED
    assert [call[1] for call in http.calls] == [
        "/v1/hiu/consents/request",
        "/v1/hiu/consents/consent-1",
        "/v1/hiu/consents/consent-1/revoke",
    ]


def test_consent_manager_handles_grant_and_revoke_payloads():
    manager = ConsentManager(FakeHTTP())

    granted = manager.handle_grant(
        {
            "consentId": "consent-1",
            "patient_abha": "ravi.kumar@abdm",
        }
    )
    revoked = manager.handle_revoke(
        {
            "consent_id": "consent-1",
            "patient_abha": "ravi.kumar@abdm",
        }
    )

    assert granted.status == ConsentState.GRANTED
    assert revoked.status == ConsentState.REVOKED


def test_data_requester_requests_health_data():
    http = FakeHTTP(
        [
            {
                "requestId": "req-1",
                "transactionId": "txn-1",
                "status": "REQUESTED",
            }
        ]
    )

    result = run(DataRequester(http).request_data(DataRequest(consent_id="consent-1")))

    assert result.request_id == "req-1"
    assert result.transaction_id == "txn-1"
    assert http.calls[0][1] == "/v1/hiu/health-information/request"
    assert http.calls[0][2]["json"] == {"consent_id": "consent-1"}


def test_data_receiver_decrypts_bundle_payload_roundtrip():
    encrypted = encrypted_payload({"bundle": sample_bundle()}, associated_data=b"aad")

    received = DataReceiver().receive_data(encrypted)

    assert received.bundle["resourceType"] == "Bundle"
    assert received.raw["bundle"]["type"] == "document"


def test_data_receiver_accepts_bundle_as_top_level_payload():
    encrypted = encrypted_payload(sample_bundle())

    received = DataReceiver().receive_data(encrypted)

    assert received.bundle["entry"][0]["resource"]["resourceType"] == "Composition"


def test_data_receiver_rejects_bad_base64():
    encrypted = encrypted_payload(sample_bundle())
    broken = encrypted.model_copy(update={"ciphertext": "not base64!!"})

    with pytest.raises(EncryptionError, match="ciphertext"):
        DataReceiver().receive_data(broken)


def test_data_receiver_rejects_non_json_plaintext():
    sender_private, sender_public = ECDHKeyExchange.generate_key_pair()
    receiver_private, receiver_public = ECDHKeyExchange.generate_key_pair()
    secret = ECDHKeyExchange.derive_shared_secret(sender_private, receiver_public)
    key = AESGCMCipher.derive_key(secret)
    ciphertext, nonce = AESGCMCipher.encrypt(b"not-json", key)

    encrypted = EncryptedHealthData(
        ciphertext=b64(ciphertext),
        nonce=b64(nonce),
        sender_public_key=b64(sender_public),
        receiver_private_key=b64(receiver_private),
    )

    with pytest.raises(EncryptionError, match="valid JSON"):
        DataReceiver().receive_data(encrypted)


def test_data_receiver_rejects_decrypted_non_bundle_payload():
    encrypted = encrypted_payload({"resourceType": "Patient"})

    with pytest.raises(FHIRValidationError, match="FHIR Bundle"):
        DataReceiver().receive_data(encrypted)


def test_hiu_client_facade_exposes_modules():
    client = HIUClient(FakeHTTP())

    assert isinstance(client.consents, ConsentManager)
    assert isinstance(client.data_requests, DataRequester)
    assert isinstance(client.data_receiver, DataReceiver)
