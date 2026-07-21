"""Shared helpers for FHIR R4 resource builders."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

FHIRDict = dict[str, Any]

SNOMED_SYSTEM = "http://snomed.info/sct"
LOINC_SYSTEM = "http://loinc.org"
ACT_CODE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
ABHA_SYSTEM = "https://healthid.abdm.gov.in"
PRACTITIONER_SYSTEM = "https://doctor.ndhm.gov.in"
FACILITY_SYSTEM = "https://facility.abdm.gov.in"


def make_id() -> str:
    return str(uuid.uuid4())


def make_urn(resource_id: str) -> str:
    return f"urn:uuid:{resource_id}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def coding(system: str, code: str, display: str) -> FHIRDict:
    return {"system": system, "code": code, "display": display}


def reference(full_url: str) -> FHIRDict:
    return {"reference": full_url}


def bundle_entry(resource: FHIRDict) -> FHIRDict:
    return {"fullUrl": make_urn(resource["id"]), "resource": resource}
