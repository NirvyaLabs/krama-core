import asyncio

import httpx
import pytest

from krama.exceptions import ABDMGatewayError, CircuitOpenError
from krama.gateway import (
    CircuitBreaker,
    CircuitState,
    GatewayHealthClient,
    RetryConfig,
    retry_gateway_call,
)


def run(coro):
    return asyncio.run(coro)


def test_retry_retries_5xx_and_timeout_then_succeeds():
    calls = 0
    sleeps = []

    async def sleep(delay):
        sleeps.append(delay)

    @retry_gateway_call(RetryConfig(max_retries=3, base_delay=0.5), sleep=sleep)
    async def gateway_call():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ABDMGatewayError(503, "temporary")
        if calls == 2:
            raise httpx.TimeoutException("slow")
        return {"ok": True}

    assert run(gateway_call()) == {"ok": True}
    assert calls == 3
    assert sleeps == [0.5, 1.0]


def test_retry_does_not_retry_4xx():
    calls = 0

    @retry_gateway_call(RetryConfig(max_retries=3), sleep=lambda _delay: _noop())
    async def gateway_call():
        nonlocal calls
        calls += 1
        raise ABDMGatewayError(400, "bad request")

    with pytest.raises(ABDMGatewayError):
        run(gateway_call())

    assert calls == 1


async def _noop():
    return None


def test_circuit_breaker_state_transitions():
    now = 100.0
    breaker = CircuitBreaker(clock=lambda: now)

    async def fail():
        raise RuntimeError("gateway down")

    for _ in range(5):
        with pytest.raises(RuntimeError):
            run(breaker.execute(fail))

    assert breaker.state == CircuitState.OPEN

    async def succeed():
        return "ok"

    with pytest.raises(CircuitOpenError):
        run(breaker.execute(succeed))

    now += 31
    assert run(breaker.execute(succeed)) == "ok"
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


def test_circuit_breaker_reopens_when_half_open_call_fails():
    now = 100.0
    breaker = CircuitBreaker(clock=lambda: now)
    breaker.state = CircuitState.OPEN
    breaker.opened_at = now

    async def fail():
        raise RuntimeError("still down")

    now += 31
    with pytest.raises(RuntimeError):
        run(breaker.execute(fail))

    assert breaker.state == CircuitState.OPEN
    assert breaker.opened_at == now


def test_gateway_health_check_connected_and_disconnected():
    class HealthyHttp:
        async def get(self, path, **kwargs):
            assert path == "/v1/health"
            assert kwargs["auth_required"] is False
            return {"ok": True}

    class DownHttp:
        async def get(self, path, **kwargs):
            raise RuntimeError("offline")

    healthy = GatewayHealthClient(HealthyHttp())
    status = run(healthy.check())

    assert status.connected is True
    assert status.latency is not None
    assert status.last_successful_call is not None

    down = GatewayHealthClient(DownHttp())
    down.last_successful_call = status.last_successful_call
    failed = run(down.check())

    assert failed.connected is False
    assert failed.last_successful_call == status.last_successful_call
    assert "offline" in failed.error
