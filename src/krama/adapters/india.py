"""India ABDM country adapter."""

from __future__ import annotations

import inspect
from typing import Any

from krama.adapters.base import (
    ComplianceRules,
    Consent,
    CountryAdapter,
    PatientIdentity,
)
from krama.exceptions import ValidationError
from krama.hiu.schemas import ConsentRequest


class IndiaAdapter(CountryAdapter):
    """India adapter backed by ABHA, HIP, and HIU Krama clients."""

    country_code = "IND"

    def __init__(self, *, abha: Any, hip: Any, hiu: Any) -> None:
        self.abha = abha
        self.hip = hip
        self.hiu = hiu

    async def verify_patient_identity(self, id_data: dict[str, Any]) -> PatientIdentity:
        verifier = getattr(self.abha, "verify", None) or self.abha.verify_abha
        identifier = str(
            id_data.get("abha_number")
            or id_data.get("health_id_number")
            or id_data.get("patient_id")
            or ""
        )
        if not identifier:
            raise ValidationError("India identity verification requires abha_number")

        profile = await verifier(identifier)
        if isinstance(profile, PatientIdentity):
            return profile
        if isinstance(profile, dict):
            raw = profile
            patient_id = str(
                raw.get("abha_number") or raw.get("abhaNumber") or raw.get("patient_id", "")
            )
            display = str(raw.get("name") or raw.get("display", ""))
        else:
            raw = profile.model_dump(mode="json") if hasattr(profile, "model_dump") else {}
            patient_id = str(getattr(profile, "abha_number", "") or raw.get("abha_number", ""))
            display = str(getattr(profile, "name", "") or raw.get("name", ""))
        return PatientIdentity(patient_id=patient_id, display=display, raw=raw)

    async def publish_health_record(self, bundle: dict[str, Any]) -> str:
        publish = self.hip.publish
        if _can_call_with_bundle_only(publish):
            result = await publish(bundle)
        else:
            result = await publish(
                patient_abha=_required(bundle, "patient_abha"),
                bundle=bundle,
                care_context_reference=_required(bundle, "care_context_reference"),
                care_context_display=str(bundle.get("care_context_display", "Health record")),
            )
        return _extract_transaction_id(result)

    async def request_consent(self, patient_id: str, purpose: str) -> Consent:
        manager = getattr(self.hiu, "consent", None) or getattr(self.hiu, "consents", None)
        if manager is None:
            raise ValidationError("HIU consent manager is not configured")

        request = getattr(manager, "request", None) or manager.request_consent
        if _can_call_with_patient_purpose(request):
            result = await request(patient_id, purpose)
        else:
            consent_request = ConsentRequest(
                patient_abha=patient_id,
                purpose=purpose,
                hiu_id="krama-hiu",
                date_range_from="1970-01-01",
                date_range_to="2100-01-01",
            )
            result = await request(consent_request)
        return _extract_consent(result)

    def get_drug_formulary(self) -> str:
        return "indian_pharmacopoeia"

    def get_coding_system(self) -> str:
        return "icd10"

    def get_compliance_rules(self) -> ComplianceRules:
        return ComplianceRules(frameworks=["DPDP Act", "DISHA"])

    def get_data_residency_region(self) -> str:
        return "ap-south-1"

    def get_supported_patient_identifiers(self) -> list[str]:
        return ["india_abha", "india_abha_address", "local_mrn"]


def _can_call_with_bundle_only(func: Any) -> bool:
    parameters = [
        param
        for param in inspect.signature(func).parameters.values()
        if param.default is inspect.Parameter.empty
        and param.kind
        in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
    ]
    return len(parameters) <= 1


def _can_call_with_patient_purpose(func: Any) -> bool:
    parameters = [
        param
        for param in inspect.signature(func).parameters.values()
        if param.default is inspect.Parameter.empty
        and param.kind
        in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
    ]
    return len(parameters) >= 2


def _required(bundle: dict[str, Any], key: str) -> str:
    value = str(bundle.get(key, ""))
    if not value:
        raise ValidationError(f"bundle metadata missing: {key}")
    return value


def _extract_transaction_id(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return str(
            result.get("transaction_id")
            or result.get("transactionId")
            or result.get("request_id")
            or result.get("care_context_reference")
            or ""
        )
    if hasattr(result, "model_dump"):
        return _extract_transaction_id(result.model_dump(mode="json"))
    return str(result)


def _extract_consent(result: Any) -> Consent:
    if isinstance(result, Consent):
        return result
    if isinstance(result, dict):
        raw = result
    elif hasattr(result, "model_dump"):
        raw = result.model_dump(mode="json")
    else:
        raw = {"consent_id": str(result), "status": "REQUESTED"}
    return Consent(
        consent_id=str(raw.get("consent_id") or raw.get("consentId", "")),
        status=str(raw.get("status", "REQUESTED")),
        raw=raw,
    )
