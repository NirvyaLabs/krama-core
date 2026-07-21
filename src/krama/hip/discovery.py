"""HIP discovery callback handling."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from krama.hip.care_context import HIPHttpClient
from krama.hip.schemas import (
    DiscoveryAcknowledgement,
    DiscoveryMatch,
    DiscoveryRequest,
    DiscoveryStatus,
)

DiscoveryProcessor = Callable[[DiscoveryRequest], Awaitable[DiscoveryMatch]]


class DiscoveryHandler:
    """Acknowledge discovery callbacks immediately and process them async."""

    def __init__(
        self,
        http_client: HIPHttpClient,
        processor: DiscoveryProcessor,
        *,
        max_queue_size: int = 1000,
    ) -> None:
        self._http = http_client
        self._processor = processor
        self._queue: asyncio.Queue[DiscoveryRequest] = asyncio.Queue(max_queue_size)
        self._worker: asyncio.Task | None = None
        self._running = False

    async def handle(self, request_body: dict) -> DiscoveryAcknowledgement:
        request = self._parse_request(request_body)
        self._queue.put_nowait(request)
        return DiscoveryAcknowledgement(request_id=request.request_id)

    async def process_next(self) -> DiscoveryStatus:
        request = await self._queue.get()
        try:
            match = await self._processor(request)
            await self._respond(request, match)
            return DiscoveryStatus.PROCESSED
        finally:
            self._queue.task_done()

    async def start_worker(self) -> None:
        if self._worker and not self._worker.done():
            return
        self._running = True
        self._worker = asyncio.create_task(self._run())

    async def stop_worker(self) -> None:
        self._running = False
        if self._worker:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass

    def pending_count(self) -> int:
        return self._queue.qsize()

    async def _run(self) -> None:
        while self._running:
            await self.process_next()

    async def _respond(
        self,
        request: DiscoveryRequest,
        match: DiscoveryMatch,
    ) -> None:
        await self._http.post(
            "/v1/hip/care-contexts/on-discover",
            json={
                "request_id": request.request_id,
                "transaction_id": request.transaction_id,
                "patient_abha": match.patient_abha,
                "care_contexts": [
                    care_context.model_dump(mode="json")
                    for care_context in match.care_contexts
                ],
            },
        )

    def _parse_request(self, request_body: dict) -> DiscoveryRequest:
        patient = request_body.get("patient", {})
        return DiscoveryRequest(
            request_id=str(request_body.get("requestId") or request_body.get("request_id")),
            transaction_id=str(
                request_body.get("transactionId") or request_body.get("transaction_id")
            ),
            patient_abha=str(
                patient.get("id") or request_body.get("patient_abha") or ""
            ),
            raw=request_body,
        )
