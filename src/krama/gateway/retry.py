"""Retry helpers for ABDM Gateway calls."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import httpx
from pydantic import BaseModel, Field

from krama.exceptions import ABDMGatewayError


P = ParamSpec("P")
T = TypeVar("T")
SleepFunc = Callable[[float], Awaitable[None]]


class RetryConfig(BaseModel):
    """Exponential backoff settings for gateway calls."""

    max_retries: int = Field(default=3, ge=0, le=10)
    base_delay: float = Field(default=1.0, ge=0)
    max_delay: float = Field(default=30.0, gt=0)
    exponential_base: float = Field(default=2.0, gt=1.0)

    def delay_for_attempt(self, attempt: int) -> float:
        delay = self.base_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)


def retry_gateway_call(
    config: RetryConfig | None = None,
    *,
    sleep: SleepFunc = asyncio.sleep,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Wrap an async gateway call with retry for 5xx responses and timeouts."""

    retry_config = config or RetryConfig()

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error: Exception | None = None
            attempts = retry_config.max_retries + 1

            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if not _should_retry(exc):
                        raise
                    last_error = exc
                    if attempt == attempts - 1:
                        raise
                    await sleep(retry_config.delay_for_attempt(attempt))

            if last_error is not None:
                raise last_error
            raise RuntimeError("retry loop exited without result")

        return wrapper

    return decorator


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, ABDMGatewayError):
        return exc.status_code >= 500
    return isinstance(exc, (TimeoutError, httpx.TimeoutException))
