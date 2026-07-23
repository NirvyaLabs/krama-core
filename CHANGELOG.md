# Changelog

All notable changes to Krama Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-alpha.3] - 2026-07-23

### Added

- Universal adaptive clinical template builder for country-neutral encounter
  workflows
- `UniversalTemplateContext` and `create_universal_template()` helpers
- `TemplateRegistry.universal(country)` convenience method
- Compliance engine with country policy metadata, blockers, warnings, source
  URLs, and a legal/governance disclaimer
- Compliance rule packs for India, Australia, US, UK, and global fallback
- `KramaClient.compliance` facade for workflow checks
- Tests for adaptive template country defaults, custom country contexts,
  compliance blockers, warnings, minimum-necessary behavior, data residency, and
  country alias handling
- Global adaptability/security matrix tests proving every built-in clinical
  domain template can be paired with every major country compliance policy
- Unsupported country identifier blocking and encryption-required checks across
  India, Australia, US, and UK
- README architecture update for country identifiers, domain templates, and
  compliance guardrails
- Dependency upper bounds for `httpx`, `pydantic`, and `pydantic-settings` to
  avoid prerelease/dev major-version installs

## [1.0.0-alpha.2] - 2026-07-23

### Added

- Country-aware `PatientIdentifier` model for FHIR Patient resources
- Backward-compatible `FHIRPatient(abha_id=...)` support plus global
  `FHIRPatient(identifiers=[...])` support
- Identifier helpers for India ABHA, Australia IHI/MRN, US MRN/MBI, UK NHS
  Number/MRN, and custom FHIR identifier systems
- Assigner-scoped local MRN URN generation to avoid collisions across hospitals
- UK adapter metadata stub with NHS identifier preferences, UK GDPR/Data
  Protection Act compliance metadata, and `eu-west-2` residency
- `get_supported_patient_identifiers()` metadata on country adapters

## [1.0.0-alpha] - 2026-07-21

### Added

- Gateway resilience package with exponential retry, circuit breaker state
  machine, and health checks
- Retry behavior limited to timeout and 5xx failures; 4xx gateway responses are
  never retried
- WhatsApp package with provider abstraction, AiSensy, Gupshup, and Meta Cloud
  API adapters
- WhatsApp outbound sender, provider-neutral inbound webhook normalization, and
  named template validation/rendering with `{{placeholders}}`
- AI package with LLM provider abstraction, Gemini and Groq adapters, priority
  router failover, SOAP improvement suggestions, encounter summaries, ICD-10
  suggestions, drug interaction checks, and urgency triage
- Safety disclaimer embedded in AI clinical outputs and result models
- Country adapter package with India ABDM adapter plus Australia and US metadata
  stubs
- `KramaClient.adapter(country="IND")`, `KramaClient.gateway_health`, optional
  `KramaClient.whatsapp`, and optional `KramaClient.ai`
- Optional extras: `krama-core[ai]` and `krama-core[whatsapp]`
- Tests for retry behavior, circuit breaker transitions, health checks,
  WhatsApp provider parsing/sending, template rendering, AI router failover,
  clinical AI helpers, and country adapter selection/delegation

## [0.5.0] - 2026-07-21

### Added

- Clinical domain template models: `ClinicalTemplate` and `TemplateSection`
- `TemplateRegistry` with built-in loading, custom registration, lookup, and
  domain/template listing
- Built-in templates for 12 clinical domains: allopathy, dentistry, ayurveda,
  homeopathy, surgery, pediatrics, ophthalmology, OB-GYN, psychiatry,
  dermatology, orthopedics, and ENT
- Surgery templates for pre-op assessment, operative note, and post-op follow-up
- OB-GYN templates for antenatal and postnatal visits
- Template structure validator and tests for built-in parsing, missing templates,
  custom registration, and domain coverage

## [0.4.0] - 2026-07-20

### Added

- HIP Milestone 2 clients for discovery callbacks, care-context CRUD,
  care-context link/unlink, and FHIR bundle publishing
- Discovery callback queue pattern: handlers acknowledge immediately and defer
  processing/response work to async workers
- HIU Milestone 3 clients for consent request/status/revoke events and health
  data requests
- HIU encrypted data receiver that uses Krama crypto helpers to derive keys,
  decrypt AES-GCM payloads, parse JSON, and validate FHIR Bundle payloads
- Mock-only tests covering HIP and HIU gateway flows without real network calls

## [0.3.0] - 2026-07-20

### Added

- FHIR R4 resource builders for Patient, Practitioner, Organization, Encounter,
  Condition, Observation, MedicationRequest, DiagnosticReport,
  AllergyIntolerance, Procedure, and Composition
- Fluent `OPConsultBuilder` and `PrescriptionBuilder` document composition APIs
- ECDH key exchange helpers using X25519
- AES-256-GCM encryption/decryption helpers with HKDF-SHA256 key derivation
- 100% test coverage for the crypto module, including encrypt/decrypt roundtrip,
  tamper rejection, and invalid key/nonce handling

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
