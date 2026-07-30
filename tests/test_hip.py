import asyncio

import pytest

from krama.exceptions import FHIRValidationError
from krama.hip import (
    CareContext,
    CareContextClient,
    DiscoveryHandler,
    DiscoveryMatch,
    DiscoveryStatus,
    HIPClient,
    HIPLinkingClient,
    HIPPublisher,
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

    async def request(self, method: str, path: str, **kwargs):
        self.calls.append((method, path, kwargs))
        return self._next_response()

    def _next_response(self):
        if self.responses:
            return self.responses.pop(0)
        return {}


def sample_care_context():
    return CareContext(
        reference="visit-1",
        display="OP consultation",
        patient_abha="RAVI.KUMAR@ABDM",
    )


def sample_bundle():
    return {
        "resourceType": "Bundle",
        "type": "document",
        "entry": [{"resource": {"resourceType": "Composition"}}],
    }


def sample_bundle_with_patient():
    return {
        "resourceType": "Bundle",
        "type": "document",
        "identifier": {"value": "visit-2026-07-30"},
        "entry": [
            {
                "resource": {
                    "resourceType": "Composition",
                    "title": "OP Consultation Record",
                }
            },
            {
                "resource": {
                    "resourceType": "Patient",
                    "identifier": [
                        {
                            "system": "https://healthid.abdm.gov.in",
                            "value": "ravi.kumar@abdm",
                        }
                    ],
                }
            },
        ],
    }


def test_hip_schemas_normalize_abha_and_reject_bad_address():
    assert sample_care_context().patient_abha == "ravi.kumar@abdm"

    with pytest.raises(ValueError, match="ABHA"):
        CareContext(reference="visit-1", display="Visit", patient_abha="bad")


def test_care_context_crud_uses_gateway_client():
    http = FakeHTTP(
        [
            {},
            sample_care_context().model_dump(mode="json"),
            {},
            {},
        ]
    )
    client = CareContextClient(http)

    created = run(client.create(sample_care_context()))
    fetched = run(client.get("visit-1"))
    updated = run(client.update(sample_care_context()))
    deleted = run(client.delete("visit-1"))

    assert created.reference == "visit-1"
    assert fetched.patient_abha == "ravi.kumar@abdm"
    assert updated.display == "OP consultation"
    assert deleted is True
    assert [call[0] for call in http.calls] == ["POST", "GET", "PUT", "DELETE"]


def test_linking_link_and_unlink():
    http = FakeHTTP([{"linked": True, "message": "ok"}, {"unlinked": True}])
    client = HIPLinkingClient(http)

    linked = run(client.link(sample_care_context()))
    unlinked = run(client.unlink("RAVI.KUMAR@ABDM", "visit-1"))

    assert linked.linked is True
    assert linked.message == "ok"
    assert unlinked.linked is False
    assert http.calls[0][1] == "/v1/hip/care-contexts/link"
    assert http.calls[1][1] == "/v1/hip/care-contexts/unlink"


def test_discovery_handler_acknowledges_before_processing():
    http = FakeHTTP([{}])
    processed = []

    async def processor(request):
        processed.append(request.request_id)
        return DiscoveryMatch(
            patient_abha=request.patient_abha,
            care_contexts=[sample_care_context()],
        )

    handler = DiscoveryHandler(http, processor)
    ack = run(
        handler.handle(
            {
                "requestId": "req-1",
                "transactionId": "txn-1",
                "patient": {"id": "ravi.kumar@abdm"},
            }
        )
    )

    assert ack.queued is True
    assert handler.pending_count() == 1
    assert processed == []
    assert http.calls == []

    status = run(handler.process_next())

    assert status == DiscoveryStatus.PROCESSED
    assert processed == ["req-1"]
    assert http.calls[0][1] == "/v1/hip/care-contexts/on-discover"
    payload = http.calls[0][2]["json"]
    assert payload["request_id"] == "req-1"
    assert payload["care_contexts"][0]["reference"] == "visit-1"


def test_discovery_worker_can_start_and_stop():
    http = FakeHTTP([{}])
    started = asyncio.Event()

    async def scenario():
        async def processor(request):
            started.set()
            return DiscoveryMatch(patient_abha=request.patient_abha)

        handler = DiscoveryHandler(http, processor)
        await handler.start_worker()
        await handler.handle(
            {
                "request_id": "req-1",
                "transaction_id": "txn-1",
                "patient_abha": "ravi.kumar@abdm",
            }
        )
        await asyncio.wait_for(started.wait(), timeout=1)
        await handler.stop_worker()
        return handler.pending_count()

    assert run(scenario()) == 0


def test_publisher_validates_creates_links_and_notifies():
    http = FakeHTTP([{}, {"linked": True}, {"notified": True, "message": "sent"}])
    publisher = HIPPublisher(http)

    result = run(
        publisher.publish(
            patient_abha="ravi.kumar@abdm",
            bundle=sample_bundle(),
            care_context_reference="visit-1",
            care_context_display="OP consultation",
        )
    )

    assert result.notified is True
    assert result.message == "sent"
    assert [call[1] for call in http.calls] == [
        "/v1/hip/care-contexts",
        "/v1/hip/care-contexts/link",
        "/v1/hip/health-information/notify",
    ]


def test_publisher_rejects_invalid_bundle_before_gateway_calls():
    http = FakeHTTP()

    with pytest.raises(FHIRValidationError, match="Bundle"):
        run(
            HIPPublisher(http).publish(
                patient_abha="ravi.kumar@abdm",
                bundle={"resourceType": "Patient"},
                care_context_reference="visit-1",
                care_context_display="OP consultation",
            )
        )

    assert http.calls == []


def test_hip_client_facade_publish_delegates():
    http = FakeHTTP([{}, {}, {}])
    client = HIPClient(http)

    result = run(
        client.publish(
            patient_abha="ravi.kumar@abdm",
            bundle=sample_bundle(),
            care_context_reference="visit-1",
            care_context_display="OP consultation",
        )
    )

    assert result.notified is True
    assert http.calls[-1][1] == "/v1/hip/health-information/notify"


def test_hip_client_publish_can_infer_defaults_from_bundle():
    http = FakeHTTP([{}, {"linked": True}, {"notified": True}])
    client = HIPClient(http)

    result = run(client.publish(sample_bundle_with_patient()))

    assert result.notified is True
    assert result.patient_abha == "ravi.kumar@abdm"
    assert result.care_context_reference == "visit-2026-07-30"
    notify_payload = http.calls[-1][2]["json"]
    assert notify_payload["care_context_display"] == "OP Consultation Record"


def test_hip_client_publish_requires_patient_abha_when_bundle_has_no_abha():
    http = FakeHTTP()
    client = HIPClient(http)

    with pytest.raises(FHIRValidationError, match="patient_abha"):
        run(client.publish(sample_bundle()))

    assert http.calls == []
