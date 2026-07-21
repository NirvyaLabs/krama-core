"""Circuit breaker for gateway-facing operations."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import ParamSpec, TypeVar

from krama.exceptions import CircuitOpenError


P = ParamSpec("P")
T = TypeVar("T")
Clock = Callable[[], float]


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Reject calls after repeated failures, then probe after a cooldown."""

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        clock: Clock = time.monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be positive")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._clock = clock
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.opened_at: float | None = None

    async def execute(self, func: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
        self._move_to_half_open_if_ready()
        if self.state == CircuitState.OPEN:
            raise CircuitOpenError("gateway circuit is open")

        try:
            result = await func(*args, **kwargs)
        except Exception:
            self.record_failure()
            raise

        self.record_success()
        return result

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = self._clock()

    def _move_to_half_open_if_ready(self) -> None:
        if self.state != CircuitState.OPEN or self.opened_at is None:
            return
        if self._clock() - self.opened_at >= self.recovery_timeout:
            self.state = CircuitState.HALF_OPEN
