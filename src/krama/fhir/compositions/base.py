"""Shared document bundle builder helpers."""

from __future__ import annotations

import uuid
from html import escape
from typing import Any

from krama.fhir.resources.base import FHIRDict, bundle_entry, make_urn, now_iso

BUNDLE_ID_SYSTEM = "https://krama.dev/bundle-id"


def narrative(text: str) -> FHIRDict:
    return {
        "status": "generated",
        "div": f"<div xmlns='http://www.w3.org/1999/xhtml'>{escape(text)}</div>",
    }


def section(title: str, refs: list[str], text: str = "") -> FHIRDict:
    result: dict[str, Any] = {
        "title": title,
        "entry": [{"reference": resource_ref} for resource_ref in refs],
    }
    if text:
        result["text"] = narrative(text)
    return result


def assemble_document_bundle(resources: list[FHIRDict]) -> FHIRDict:
    if not resources or resources[0].get("resourceType") != "Composition":
        raise ValueError("FHIR document bundles must start with Composition")
    return {
        "resourceType": "Bundle",
        "type": "document",
        "timestamp": now_iso(),
        "identifier": {"system": BUNDLE_ID_SYSTEM, "value": str(uuid.uuid4())},
        "entry": [bundle_entry(resource) for resource in resources],
    }


def ref_for(resource: FHIRDict) -> str:
    return make_urn(resource["id"])
