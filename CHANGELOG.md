# Changelog

All notable changes to Krama Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-16

### Added

- `KramaClient` async SDK entry point
- Secure `KramaConfig` with environment variable support, secret redaction,
  timeout limits, retry limits, and HTTPS-by-default URL validation
- `ABDMHttpClient` with bearer-token injection, bounded retries, JSON response
  validation, safe error messages, and client-secret redaction
- `ABDMTokenManager` with cached token refresh and async lock protection
- ABHA Milestone 1 helpers for Aadhaar/mobile OTP initiation, OTP verification,
  ABHA lookup, health ID search, and profile fetch
- ABHA schemas and validators for Aadhaar, mobile, OTP, ABHA number, ABHA address,
  and profile gender values
- Focused tests for config security, HTTP retries, token caching, error redaction,
  and ABHA validation

## [0.1.0] - 2026-05-16

### Added

- FHIR R4 bundle generation for three ABDM care contexts:
  - `create_op_consult_bundle()` — outpatient consultation records
  - `create_prescription_bundle()` — prescription records
  - `create_discharge_summary_bundle()` — inpatient discharge summaries
- Pydantic input models: `PatientInfo`, `PractitionerInfo`, `OrganizationInfo`,
  `DiagnosisInfo`, `MedicationInfo`
- 22 tests covering all bundle types, FHIR structure, and edge cases
- Example usage script (`examples/basic_usage.py`)
- MIT license
- CI pipeline with tests on Python 3.10/3.11/3.12, ruff, bandit, pip-audit
