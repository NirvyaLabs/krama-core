import asyncio

import httpx
import pytest
from pydantic import ValidationError as PydanticValidationError

import krama
from krama import KramaClient
from krama.adapters import IndiaAdapter
from krama.abha.client import ABHAClient
from krama.abha.schemas import ABHAProfile, normalize_aadhaar, normalize_mobile
from krama.auth import ABDMTokenManager
from krama.config import KramaConfig
from krama.exceptions import ABDMGatewayError, AuthenticationError, ValidationError
from krama.utils.http import ABDMHttpClient


def run(coro):
    return asyncio.run(coro)


def test_config_rejects_insecure_remote_base_url():
    with pytest.raises(PydanticValidationError, match="https"):
        KramaConfig(
            client_id="client",
            client_secret="secret",
            base_url="http://dev.abdm.gov.in",
        )


def test_config_allows_local_http_for_tests():
    config = KramaConfig(
        client_id="client",
        client_secret="super-secret-value",
        base_url="http://localhost:8080",
    )

    assert config.base_url == "http://localhost:8080"
    assert "super-secret-value" not in repr(config)


def test_http_client_injects_auth_header_and_retries_5xx():
    seen_headers = []

    async def token_provider():
        return "access-token"

    async def no_sleep(_delay):
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.append(request.headers)
        if len(seen_headers) == 1:
            return httpx.Response(503, json={"message": "temporary"})
        return httpx.Response(200, json={"ok": True})

    config = KramaConfig(
        client_id="client",
        client_secret="secret",
        base_url="https://abdm.example",
        max_retries=1,
    )
    client = ABDMHttpClient(
        config,
        token_provider=token_provider,
        transport=httpx.MockTransport(handler),
        sleep=no_sleep,
    )

    try:
        response = run(client.get("/v1/status"))
    finally:
        run(client.close())

    assert response == {"ok": True}
    assert len(seen_headers) == 2
    assert seen_headers[0]["authorization"] == "Bearer access-token"


def test_http_client_redacts_secret_from_gateway_errors():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"message": "bad client secret: super-secret"},
            headers={"x-request-id": "req-123"},
        )

    config = KramaConfig(
        client_id="client",
        client_secret="super-secret",
        base_url="https://abdm.example",
        max_retries=0,
    )
    client = ABDMHttpClient(
        config,
        token_provider=lambda: _token("token"),
        transport=httpx.MockTransport(handler),
    )

    try:
        with pytest.raises(ABDMGatewayError) as exc_info:
            run(client.get("/v1/status"))
    finally:
        run(client.close())

    message = str(exc_info.value)
    assert "super-secret" not in message
    assert "[REDACTED]" in message
    assert exc_info.value.request_id == "req-123"


async def _token(value: str) -> str:
    return value


class FakeTokenHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def post(self, path: str, **kwargs):
        self.calls.append((path, kwargs))
        return self.responses.pop(0)


def test_token_manager_caches_until_refresh_margin():
    now = 1_000.0
    http = FakeTokenHttp(
        [
            {"accessToken": "first", "expiresIn": 300},
            {"accessToken": "second", "expiresIn": 300},
        ]
    )
    manager = ABDMTokenManager(
        http,
        client_id="client",
        client_secret=KramaConfig(
            client_id="client",
            client_secret="secret",
        ).client_secret,
        clock=lambda: now,
    )

    assert run(manager.get_token()) == "first"
    assert run(manager.get_token()) == "first"
    assert len(http.calls) == 1

    now = 1_250.0
    assert run(manager.get_token()) == "second"
    assert len(http.calls) == 2
    assert http.calls[0][1]["json"]["clientSecret"] == "secret"


def test_token_manager_rejects_malformed_token_response():
    http = FakeTokenHttp([{"expiresIn": 300}])
    manager = ABDMTokenManager(
        http,
        client_id="client",
        client_secret=KramaConfig(
            client_id="client",
            client_secret="secret",
        ).client_secret,
    )

    with pytest.raises(AuthenticationError):
        run(manager.get_token())


def test_abha_validators_normalize_common_inputs():
    assert normalize_aadhaar("1234 5678 9012") == "123456789012"
    assert normalize_mobile("+91 98765 43210") == "9876543210"


def test_abha_client_validates_before_sending_request():
    class NoCallHttp:
        async def post(self, path: str, **kwargs):
            raise AssertionError("request should not be sent")

    client = ABHAClient(NoCallHttp())

    with pytest.raises(ValueError, match="Aadhaar"):
        run(client.create_via_aadhaar("123"))


def test_abha_client_parses_profile_response():
    class ProfileHttp:
        async def post(self, path: str, **kwargs):
            assert path == "/v1/registration/mobile/verifyOTP"
            assert kwargs["json"] == {"txnId": "txn-1", "otp": "123456"}
            return {
                "abhaNumber": "12-3456-7890-1234",
                "abhaAddress": "Ravi.Kumar@ABDM",
                "name": "Ravi Kumar",
                "dateOfBirth": "1990-05-15",
                "gender": "M",
            }

    profile = run(ABHAClient(ProfileHttp()).verify_mobile_otp("txn-1", "123456"))

    assert isinstance(profile, ABHAProfile)
    assert profile.abha_address == "ravi.kumar@abdm"
    assert profile.abha_number == "12-3456-7890-1234"


def test_abha_client_rejects_bad_health_id_search():
    class NoCallHttp:
        async def post(self, path: str, **kwargs):
            raise AssertionError("request should not be sent")

    with pytest.raises(ValidationError, match="ABHA address"):
        run(ABHAClient(NoCallHttp()).search_by_health_id("not-an-address"))


def test_krama_client_exposes_abha_and_closes_cleanly():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    client = KramaClient(
        client_id="client",
        client_secret="secret",
        base_url="https://abdm.example",
        transport=httpx.MockTransport(handler),
    )

    try:
        assert client.abha is not None
        assert client.fhir.op_consult() is not None
        assert client.hip is not None
        assert client.hiu is not None
        assert isinstance(client.adapter("IND"), IndiaAdapter)
        assert client.compliance is not None
        assert client.gateway_health is not None
        assert client.whatsapp is None
        assert client.ai is None
        assert client.config.client_secret.get_secret_value() == "secret"
    finally:
        run(client.close())


def test_package_version_is_alpha():
    assert krama.__version__ == "1.0.0a4"
