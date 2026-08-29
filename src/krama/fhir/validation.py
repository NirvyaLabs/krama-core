"""Lightweight validation for FHIR document bundles."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from krama.exceptions import FHIRValidationError


def _reference_values(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        reference = value.get("reference")
        if reference is not None:
            yield reference
        for nested in value.values():
            yield from _reference_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _reference_values(nested)


def validate_fhir_bundle(bundle: Any) -> None:
    """Validate common structural rules for a FHIR R4 document Bundle.

    This intentionally does not replace a full FHIR profile validator. It
    catches malformed bundles and broken local references before publication.
    """
    if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
        raise FHIRValidationError("FHIR payload must be a Bundle")
    if bundle.get("type") != "document":
        raise FHIRValidationError("FHIR Bundle.type must be document")

    entries = bundle.get("entry")
    if not isinstance(entries, list) or not entries:
        raise FHIRValidationError("FHIR document Bundle.entry must be non-empty")

    resources: list[dict[str, Any]] = []
    full_urls: set[str] = set()
    resource_ids: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise FHIRValidationError(f"FHIR Bundle.entry[{index}] must be an object")

        full_url = entry.get("fullUrl")
        if not isinstance(full_url, str) or not full_url.strip():
            raise FHIRValidationError(
                f"FHIR Bundle.entry[{index}].fullUrl must be a non-empty string"
            )
        if full_url in full_urls:
            raise FHIRValidationError(f"duplicate FHIR Bundle.entry fullUrl: {full_url}")
        full_urls.add(full_url)

        resource = entry.get("resource")
        if not isinstance(resource, dict):
            raise FHIRValidationError(
                f"FHIR Bundle.entry[{index}].resource must be an object"
            )
        resource_type = resource.get("resourceType")
        if not isinstance(resource_type, str) or not resource_type.strip():
            raise FHIRValidationError(
                f"FHIR Bundle.entry[{index}].resource.resourceType is required"
            )
        resource_id = resource.get("id")
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise FHIRValidationError(
                f"FHIR Bundle.entry[{index}].resource.id is required"
            )
        if resource_id in resource_ids:
            raise FHIRValidationError(f"duplicate FHIR resource id: {resource_id}")

        resources.append(resource)
        resource_ids.add(resource_id)

    if resources[0]["resourceType"] != "Composition":
        raise FHIRValidationError(
            "FHIR document Bundle must start with Composition"
        )

    for resource in resources:
        for reference in _reference_values(resource):
            if not isinstance(reference, str) or not reference.strip():
                raise FHIRValidationError("FHIR references must be non-empty strings")
            if reference.startswith("urn:uuid:") and reference not in full_urls:
                raise FHIRValidationError(
                    f"FHIR internal reference does not match a Bundle entry: {reference}"
                )
            if reference in resource_ids and not reference.startswith("urn:uuid:"):
                raise FHIRValidationError(
                    "FHIR internal references must use urn:uuid: URLs"
                )

