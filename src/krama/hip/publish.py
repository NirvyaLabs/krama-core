"""HIP FHIR bundle publishing."""

from __future__ import annotations

from krama.exceptions import FHIRValidationError
from krama.fhir.resources.base import ABHA_SYSTEM
from krama.hip.care_context import CareContextClient, HIPHttpClient
from krama.hip.linking import HIPLinkingClient
from krama.hip.schemas import CareContext, PublishResult


class HIPPublisher:
    """Publish health records as a Health Information Provider."""

    def __init__(
        self,
        http_client: HIPHttpClient,
        *,
        care_contexts: CareContextClient | None = None,
        linking: HIPLinkingClient | None = None,
    ) -> None:
        self._http = http_client
        self._care_contexts = care_contexts or CareContextClient(http_client)
        self._linking = linking or HIPLinkingClient(http_client)

    async def publish(
        self,
        patient_abha: str,
        bundle: dict,
        care_context_reference: str,
        care_context_display: str,
    ) -> PublishResult:
        self._validate_bundle(bundle)
        care_context = CareContext(
            patient_abha=patient_abha,
            reference=care_context_reference,
            display=care_context_display,
        )
        await self._care_contexts.create(care_context)
        await self._linking.link(care_context)
        response = await self._http.post(
            "/v1/hip/health-information/notify",
            json={
                "patient_abha": care_context.patient_abha,
                "care_context_reference": care_context.reference,
                "care_context_display": care_context.display,
                "bundle": bundle,
            },
        )
        return PublishResult(
            patient_abha=care_context.patient_abha,
            care_context_reference=care_context.reference,
            notified=bool(response.get("notified", True)),
            message=str(response.get("message", "")),
        )

    def _validate_bundle(self, bundle: dict) -> None:
        if bundle.get("resourceType") != "Bundle":
            raise FHIRValidationError("FHIR payload must be a Bundle")
        if bundle.get("type") != "document":
            raise FHIRValidationError("FHIR Bundle.type must be document")
        entries = bundle.get("entry")
        if not isinstance(entries, list) or not entries:
            raise FHIRValidationError("FHIR Bundle.entry must be non-empty")
        first_resource = entries[0].get("resource") if isinstance(entries[0], dict) else {}
        if first_resource.get("resourceType") != "Composition":
            raise FHIRValidationError("FHIR document Bundle must start with Composition")


class HIPClient:
    """Facade for HIP Milestone 2 operations."""

    def __init__(self, http_client: HIPHttpClient) -> None:
        self.care_contexts = CareContextClient(http_client)
        self.linking = HIPLinkingClient(http_client)
        self.publisher = HIPPublisher(
            http_client,
            care_contexts=self.care_contexts,
            linking=self.linking,
        )

    async def publish(
        self,
        patient_abha: str | dict | None = None,
        bundle: dict | None = None,
        care_context_reference: str | None = None,
        care_context_display: str | None = None,
    ) -> PublishResult:
        if isinstance(patient_abha, dict) and bundle is None:
            bundle = patient_abha
            patient_abha = None
        if bundle is None:
            raise FHIRValidationError("FHIR bundle is required for HIP publish")

        resolved_patient_abha = patient_abha or _patient_abha_from_bundle(bundle)
        resolved_reference = care_context_reference or _care_context_reference(bundle)
        resolved_display = care_context_display or _care_context_display(bundle)

        return await self.publisher.publish(
            patient_abha=resolved_patient_abha,
            bundle=bundle,
            care_context_reference=resolved_reference,
            care_context_display=resolved_display,
        )


def _patient_abha_from_bundle(bundle: dict) -> str:
    for resource in _bundle_resources(bundle):
        if resource.get("resourceType") != "Patient":
            continue
        for identifier in resource.get("identifier", []):
            if not isinstance(identifier, dict):
                continue
            value = str(identifier.get("value", "")).strip()
            system = str(identifier.get("system", "")).strip()
            if value and (system == ABHA_SYSTEM or value.lower().endswith("@abdm")):
                return value
    raise FHIRValidationError(
        "patient_abha is required when the bundle has no ABHA Patient identifier"
    )


def _care_context_reference(bundle: dict) -> str:
    identifier = bundle.get("identifier")
    if isinstance(identifier, dict) and identifier.get("value"):
        return str(identifier["value"])
    if bundle.get("id"):
        return str(bundle["id"])
    return "krama-care-context"


def _care_context_display(bundle: dict) -> str:
    for resource in _bundle_resources(bundle):
        if resource.get("resourceType") == "Composition" and resource.get("title"):
            return str(resource["title"])
    return "Health record"


def _bundle_resources(bundle: dict) -> list[dict]:
    resources = []
    for entry in bundle.get("entry", []):
        if isinstance(entry, dict) and isinstance(entry.get("resource"), dict):
            resources.append(entry["resource"])
    return resources
