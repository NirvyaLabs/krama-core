"""Country-aware compliance rule evaluation."""

from __future__ import annotations

from krama.compliance.models import (
    ComplianceContext,
    ComplianceFinding,
    ComplianceResult,
    ComplianceSeverity,
)
from krama.compliance.policies import CountryCompliancePolicy, get_policy


class ComplianceEngine:
    """Evaluate healthcare workflow facts against country policy metadata."""

    def __init__(
        self,
        policies: dict[str, CountryCompliancePolicy] | None = None,
    ) -> None:
        self._policies = policies or {}

    def evaluate(self, context: ComplianceContext) -> ComplianceResult:
        policy = self._policy_for(context.country)
        blockers: list[ComplianceFinding] = []
        warnings: list[ComplianceFinding] = []

        self._check_patient_identifier(context, policy, blockers)
        self._check_purpose(context, policy, blockers)
        self._check_consent_or_lawful_basis(context, policy, blockers)
        self._check_encryption(context, policy, blockers)
        self._check_data_residency(context, policy, warnings)
        self._check_minimum_necessary(context, policy, blockers, warnings)
        self._check_auditability(context, policy, warnings)

        return ComplianceResult(
            country=policy.country,
            frameworks=policy.frameworks,
            passed=not blockers,
            blockers=blockers,
            warnings=warnings,
            source_urls=policy.source_urls,
        )

    def _policy_for(self, country: str) -> CountryCompliancePolicy:
        normalized = ComplianceContext(country=country).country
        return self._policies.get(normalized) or get_policy(normalized)

    def _check_patient_identifier(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        blockers: list[ComplianceFinding],
    ) -> None:
        if not context.patient_identifiers:
            blockers.append(
                _finding(
                    "patient_identifier_required",
                    "At least one supported patient identifier is required.",
                    policy,
                    ComplianceSeverity.BLOCKER,
                )
            )
            return

        supported = set(policy.required_identifier_types)
        provided = set(context.patient_identifiers)
        if supported and not supported.intersection(provided):
            blockers.append(
                _finding(
                    "unsupported_patient_identifier",
                    (
                        "Patient identifier type is not supported for this "
                        f"country. Supported: {', '.join(policy.required_identifier_types)}"
                    ),
                    policy,
                    ComplianceSeverity.BLOCKER,
                )
            )

    def _check_purpose(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        blockers: list[ComplianceFinding],
    ) -> None:
        if context.purpose.strip():
            return
        blockers.append(
            _finding(
                "purpose_required",
                "Purpose of use must be recorded before processing health data.",
                policy,
                ComplianceSeverity.BLOCKER,
            )
        )

    def _check_consent_or_lawful_basis(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        blockers: list[ComplianceFinding],
    ) -> None:
        if not policy.consent_or_lawful_basis_required:
            return
        if context.consent_present or context.lawful_basis.strip():
            return
        blockers.append(
            _finding(
                "consent_or_lawful_basis_required",
                "Record patient consent or another lawful basis for processing.",
                policy,
                ComplianceSeverity.BLOCKER,
            )
        )

    def _check_encryption(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        blockers: list[ComplianceFinding],
    ) -> None:
        if not policy.encryption_required or context.encrypted:
            return
        blockers.append(
            _finding(
                "encryption_required",
                "Health data must be encrypted in transport/storage workflows.",
                policy,
                ComplianceSeverity.BLOCKER,
            )
        )

    def _check_data_residency(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        warnings: list[ComplianceFinding],
    ) -> None:
        if not policy.data_residency_region or not context.data_residency_region:
            return
        if context.data_residency_region == policy.data_residency_region:
            return
        warnings.append(
            _finding(
                "data_residency_mismatch",
                (
                    "Configured data residency region does not match the "
                    f"country policy default ({policy.data_residency_region})."
                ),
                policy,
                ComplianceSeverity.WARNING,
            )
        )

    def _check_minimum_necessary(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        blockers: list[ComplianceFinding],
        warnings: list[ComplianceFinding],
    ) -> None:
        if not context.requested_fields or not context.necessary_fields:
            return

        requested = {field.lower() for field in context.requested_fields}
        necessary = {field.lower() for field in context.necessary_fields}
        extra_fields = sorted(requested - necessary)
        if not extra_fields:
            return

        target = (
            blockers
            if policy.minimum_necessary_severity == ComplianceSeverity.BLOCKER
            else warnings
        )
        target.append(
            _finding(
                "minimum_necessary",
                (
                    "Requested fields exceed the stated purpose: "
                    + ", ".join(extra_fields)
                ),
                policy,
                policy.minimum_necessary_severity,
            )
        )

    def _check_auditability(
        self,
        context: ComplianceContext,
        policy: CountryCompliancePolicy,
        warnings: list[ComplianceFinding],
    ) -> None:
        if context.actor_id and context.audit_event_id:
            return
        warnings.append(
            _finding(
                "audit_trail_recommended",
                "Record actor_id and audit_event_id for traceable health data access.",
                policy,
                ComplianceSeverity.WARNING,
            )
        )


def _finding(
    code: str,
    message: str,
    policy: CountryCompliancePolicy,
    severity: ComplianceSeverity,
) -> ComplianceFinding:
    framework = policy.frameworks[0] if policy.frameworks else "Local policy"
    return ComplianceFinding(
        code=code,
        message=message,
        framework=framework,
        severity=severity,
    )
