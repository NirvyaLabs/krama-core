# Krama Core Learning Guide

This guide is for understanding Krama Core as a product, a Python package, and a
healthcare interoperability SDK. Read it when you want to know what the code is
doing, why each module exists, and how to keep developing it safely.

Krama Core is not just an ABDM bundle generator anymore. It is becoming a
country-adaptive healthcare integration toolkit: FHIR records, patient identity,
consent, encryption, gateway communication, clinical templates, WhatsApp,
AI-assisted workflows, and compliance checks all live under one SDK.

## 1. What Krama Is

Krama Core helps healthcare products produce, exchange, and protect structured
clinical data.

The current SDK focuses on these jobs:

- Build FHIR R4 healthcare records.
- Support ABDM-style flows for India.
- Represent patients using country-specific identifiers.
- Encrypt and decrypt health information.
- Model HIP and HIU workflows.
- Provide clinical templates for multiple specialties.
- Check compliance guardrails before processing health data.
- Add integration layers for WhatsApp, AI providers, and country adapters.

The simplest mental model:

```text
Clinical input
    -> template or builder
    -> FHIR resources
    -> FHIR bundle
    -> compliance check
    -> encryption if needed
    -> gateway / HIP / HIU / country adapter
```

## 2. What You Should Learn First

You do not need to learn everything at once. Learn in this order.

1. Python package basics

   Learn how `src/krama/` becomes the importable package `krama`.

2. Pydantic

   Krama uses Pydantic models to validate input data and keep API shapes clean.
   Most request/response objects, FHIR resources, templates, and compliance
   objects are Pydantic models.

3. FHIR R4 basics

   FHIR is the healthcare data format Krama uses. Focus first on:

   - `Patient`
   - `Practitioner`
   - `Organization`
   - `Encounter`
   - `Condition`
   - `Observation`
   - `MedicationRequest`
   - `Composition`
   - `Bundle`

4. ABDM basics

   ABDM is India's digital health framework. Krama started here, so the older
   convenience APIs are India/ABDM friendly.

5. Async Python

   HIP, HIU, gateway calls, retry, circuit breaker, WhatsApp, and AI providers
   use async patterns.

6. Cryptography basics

   Krama uses ECDH for key exchange and AES-GCM for authenticated encryption.
   The key idea is: encrypt data in a way that also detects tampering.

7. Compliance thinking

   Healthcare software is not only about moving data. It must ask:

   - Why are we processing this data?
   - Did the patient consent, or is there another lawful basis?
   - Are we encrypting data?
   - Are we keeping data in the right region?
   - Are we requesting only what is necessary?
   - Can we audit who did what?

## 3. Repository Map

```text
src/krama/
├── __init__.py              # Public top-level exports and version
├── client.py                # KramaClient entry point
├── config.py                # Runtime configuration
├── exceptions.py            # Shared exception types
├── utils/http.py            # ABDMHttpClient and HTTP helpers
├── auth/                    # Token handling
├── abha/                    # India ABHA client and schemas
├── fhir/                    # FHIR bundle and resource builders
├── crypto/                  # ECDH and AES-GCM encryption
├── hip/                     # Health Information Provider flows
├── hiu/                     # Health Information User flows
├── gateway/                 # Retry, circuit breaker, health checks
├── templates/               # Clinical templates by specialty/domain
├── compliance/              # Country-aware compliance guardrails
├── adapters/                # Country adapter interface and implementations
├── whatsapp/                # WhatsApp providers, templates, webhooks
└── ai/                      # LLM providers and clinical AI helpers
```

Tests mirror the modules:

```text
tests/
├── test_bundles.py
├── test_fhir_resources.py
├── test_fhir_builders.py
├── test_crypto.py
├── test_hip.py
├── test_hiu.py
├── test_gateway.py
├── test_templates.py
├── test_universal_template.py
├── test_compliance.py
├── test_global_adaptability_security.py
├── test_adapters.py
├── test_whatsapp.py
└── test_ai.py
```

## 4. The Main Entry Points

### `krama.__init__`

File:

```text
src/krama/__init__.py
```

This is what users see when they write:

```python
from krama import KramaClient
```

It also exposes important public classes such as identifiers, compliance
objects, templates, and adapters.

When you add a public feature, check whether it should be exported here.

### `KramaClient`

File:

```text
src/krama/client.py
```

`KramaClient` is the high-level SDK object. It collects major modules under one
place so product developers do not need to manually wire everything.

It gives access to things like:

- configuration
- country adapters
- compliance engine
- optional AI module
- optional WhatsApp module

Think of it as the "front desk" of the SDK.

## 5. FHIR Module

Folder:

```text
src/krama/fhir/
```

FHIR is the core data model.

There are two styles in Krama:

1. Simple ABDM bundle functions
2. Rich FHIR builder/resource classes

### Simple bundle functions

File:

```text
src/krama/fhir/bundles.py
```

These are easy APIs:

```python
from krama.fhir import create_op_consult_bundle
```

They return plain Python dictionaries that can be serialized to JSON.

This is good for quick ABDM-compatible bundle creation.

### Resource builders

Folder:

```text
src/krama/fhir/resources/
```

Each file represents a FHIR resource.

Examples:

- `patient.py`
- `practitioner.py`
- `encounter.py`
- `condition.py`
- `observation.py`
- `medication_request.py`
- `diagnostic_report.py`
- `allergy_intolerance.py`
- `procedure.py`
- `composition.py`

Each resource model usually has a method that turns a clean Python model into a
FHIR-shaped dictionary.

### Patient identifiers

File:

```text
src/krama/fhir/resources/identifiers.py
```

This is important for global adaptability.

Krama supports identifiers such as:

- India ABHA ID and ABHA address
- Australia IHI, MRN, Medicare
- US MRN and Medicare Beneficiary Identifier
- UK NHS Number and MRN
- local MRNs
- custom identifiers

The important design idea: a patient's clinical record should not be locked to
ABHA only. ABHA is correct for India, but Australia, the US, the UK, and other
countries need their own identity systems.

## 6. FHIR Compositions

Folder:

```text
src/krama/fhir/compositions/
```

FHIR document bundles usually have a `Composition` first. Composition is like
the table of contents for the document.

Current builders include:

- `OPConsultBuilder`
- `PrescriptionBuilder`

These builders collect resources and assemble a document bundle in the correct
order.

Read this folder after you understand individual resources.

## 7. Crypto Module

Folder:

```text
src/krama/crypto/
```

This module protects health data.

Main files:

- `ecdh.py`
- `aes_gcm.py`

### ECDH

ECDH is used for key exchange. Two parties can derive a shared secret without
sending that secret directly over the network.

### AES-GCM

AES-GCM encrypts data and also verifies integrity. If encrypted data is changed,
decryption should fail.

Security rule: never treat encryption as only "hiding text." For healthcare,
you also need tamper detection, key handling, audit, and consent/compliance
checks around the encryption.

Tests to study:

```text
tests/test_crypto.py
```

Look for:

- encrypt/decrypt roundtrip
- invalid input handling
- tamper/failure behavior

## 8. ABDM, HIP, and HIU

### ABHA

Folder:

```text
src/krama/abha/
```

This module is for India ABHA identity interactions.

### HIP

Folder:

```text
src/krama/hip/
```

HIP means Health Information Provider. In simple terms, this is the system that
holds or publishes patient health records.

Important files:

- `discovery.py`
- `linking.py`
- `publish.py`
- `care_context.py`
- `schemas.py`

Critical concept: ABDM discovery callbacks must respond quickly. The pattern is:

```text
receive callback
    -> immediately acknowledge
    -> put work into async processing
    -> worker processes
    -> respond through gateway API
```

Do not perform heavy work inside the request handler.

### HIU

Folder:

```text
src/krama/hiu/
```

HIU means Health Information User. This is the system requesting and receiving
health data after consent.

Important files:

- `consent.py`
- `data_request.py`
- `data_receive.py`
- `schemas.py`

The key flow:

```text
request consent
    -> check status
    -> request data with approved consent
    -> receive encrypted data
    -> decrypt
    -> parse FHIR bundle
```

## 9. Gateway Resilience

Folder:

```text
src/krama/gateway/
```

Healthcare integrations fail in real life: gateways timeout, APIs have 5xx
errors, and downstream services become unstable. This module keeps Krama from
failing recklessly.

Main files:

- `retry.py`
- `circuit_breaker.py`
- `health.py`

### Retry

Retry is for temporary failures:

- retry 5xx
- retry timeouts
- do not retry 4xx client errors

### Circuit breaker

A circuit breaker protects the system when a dependency is repeatedly failing.

States:

- `CLOSED`: normal
- `OPEN`: failing, reject calls
- `HALF_OPEN`: test one call after cooldown

### Health

Health checks show whether a gateway is connected, what latency looks like, and
when the last successful call happened.

## 10. Clinical Templates

Folder:

```text
src/krama/templates/
```

Templates define what a clinical encounter form should collect.

Core files:

- `base.py`
- `registry.py`
- `universal.py`
- `validators/template_validator.py`

Domain templates:

```text
src/krama/templates/domains/
```

Supported domains include:

- general medicine
- dentistry
- Ayurveda
- homeopathy
- surgery
- pediatrics
- ophthalmology
- OB-GYN
- psychiatry
- dermatology
- orthopedics
- ENT

### Universal template

File:

```text
src/krama/templates/universal.py
```

The universal template is country-adaptive. The aim is one robust encounter
template that can work across countries without breaking.

It adapts:

- patient identifier types
- compliance frameworks
- coding system
- prescription type
- data residency region

The template should be specialty-friendly and country-aware at the same time.

Important mental model:

```text
Specialty answers: what clinical fields do we collect?
Country answers: how must identity, compliance, coding, and exchange work?
```

Dentistry in Australia and dentistry in India can share clinical concepts, but
they may use different identifiers, consent rules, data residency expectations,
and integration pathways.

## 11. Compliance Engine

Folder:

```text
src/krama/compliance/
```

This is one of the most strategically important modules.

Files:

- `models.py`
- `policies.py`
- `engine.py`

### Models

`models.py` defines the data structures:

- `ComplianceContext`
- `ComplianceFinding`
- `ComplianceResult`
- `ComplianceSeverity`

### Policies

`policies.py` defines country rules.

Current policy direction:

- India: DPDP Act, DISHA, ABDM
- Australia: Privacy Act 1988, Australian Privacy Principles
- US: HIPAA Privacy Rule, HIPAA Security Rule
- UK: UK GDPR, Data Protection Act 2018, NHS expectations

### Engine

`engine.py` evaluates a context and returns:

- passed or failed
- blockers
- warnings
- framework information
- disclaimer

Things it checks include:

- patient identifier exists
- identifier is supported for the country
- purpose is present
- consent or lawful basis is present
- encryption is enabled
- data residency matches policy expectations
- minimum necessary principle
- audit actor/event is present

Important: this engine is a guardrail, not legal advice. Real deployments still
need professional compliance review.

## 12. Country Adapters

Folder:

```text
src/krama/adapters/
```

Country adapters let Krama behave differently by jurisdiction without breaking
the core SDK.

Files:

- `base.py`
- `india.py`
- `australia.py`
- `us.py`
- `uk.py`

The interface includes methods like:

- verify patient identity
- publish health record
- request consent
- get drug formulary
- get coding system
- get compliance rules
- get data residency region
- get supported patient identifiers

India is the most concrete adapter today because Krama started with ABDM.
Australia, US, and UK currently provide metadata and raise clear
`NotImplementedError` for integration actions that are not built yet.

This pattern lets Nirvya add country-specific healthcare rails over time, like
how logistics platforms support different regulations per country.

## 13. WhatsApp Module

Folder:

```text
src/krama/whatsapp/
```

This module normalizes WhatsApp messaging across providers.

Providers:

- AiSensy
- Gupshup
- Meta Cloud API

Important files:

- `providers/base.py`
- `providers/aisensy.py`
- `providers/gupshup.py`
- `providers/meta_direct.py`
- `webhook.py`
- `sender.py`
- `templates.py`
- `schemas.py`

The goal is to let a healthcare app send and receive messages without binding
its business logic to one WhatsApp vendor.

## 14. AI Module

Folder:

```text
src/krama/ai/
```

This module contains AI-assisted clinical helpers.

Providers:

- Gemini
- Groq
- router with failover

Clinical helpers:

- SOAP note improvement suggestions
- patient-friendly encounter summaries
- ICD-10 code suggestions
- drug interaction checks
- urgency triage

Safety rule: AI outputs are suggestions only and require physician review.

When working on this module, be extra careful with wording. The SDK should not
pretend the AI is a doctor.

## 15. Configuration and Errors

### Configuration

File:

```text
src/krama/config.py
```

Configuration should be environment-friendly and safe by default.

Never hardcode:

- API keys
- tokens
- patient secrets
- real credentials
- production endpoints unless intentionally configurable

### Errors

File:

```text
src/krama/exceptions.py
```

Use shared exception patterns instead of random `ValueError` or generic
exceptions when the error is part of the public SDK behavior.

Good SDK errors should be:

- predictable
- easy to catch
- clear enough for developers to fix

## 16. Testing Strategy

Tests are in:

```text
tests/
```

Run all tests:

```bash
pytest -v --cov=krama
```

Run only one module:

```bash
pytest -v tests/test_compliance.py
pytest -v tests/test_crypto.py
pytest -v tests/test_fhir_resources.py
```

### What coverage means

Coverage means how much of the source code was executed by tests.

High coverage is useful, but it is not enough. You also need meaningful tests:

- success cases
- invalid input
- missing fields
- security failure paths
- tampered encrypted data
- unsupported country identifiers
- no real network calls in unit tests

### Security test mindset

For healthcare software, always test:

- Does invalid data fail early?
- Does missing consent block processing?
- Does missing encryption block sensitive exchange?
- Does tampered encrypted data fail to decrypt?
- Are 4xx errors not retried?
- Are 5xx errors retried safely?
- Does the circuit breaker stop repeated gateway failures?
- Are country identifiers validated correctly?
- Do tests avoid real patient data and real credentials?

## 17. Local Commands You Should Know

Install locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest -v
pytest -v --cov=krama
```

Run lint:

```bash
ruff check src/ tests/ examples/
```

Run security tools:

```bash
bandit -r src/ -ll
pip-audit
```

Build the package:

```bash
python -m build
twine check dist/*
```

Search code:

```bash
rg "ComplianceEngine" src tests
rg "PatientIdentifier" src tests
rg "OPConsultBuilder" src tests
```

Check current version:

```bash
python -c "import krama; print(krama.__version__)"
```

## 18. Best Order To Read The Code

Read in this order:

1. `README.md`
2. `src/krama/__init__.py`
3. `src/krama/client.py`
4. `src/krama/fhir/bundles.py`
5. `src/krama/fhir/resources/patient.py`
6. `src/krama/fhir/resources/identifiers.py`
7. `src/krama/fhir/resources/base.py`
8. `src/krama/fhir/compositions/op_consult.py`
9. `src/krama/crypto/aes_gcm.py`
10. `src/krama/crypto/ecdh.py`
11. `src/krama/compliance/models.py`
12. `src/krama/compliance/policies.py`
13. `src/krama/compliance/engine.py`
14. `src/krama/templates/base.py`
15. `src/krama/templates/registry.py`
16. `src/krama/templates/universal.py`
17. `src/krama/adapters/base.py`
18. `src/krama/adapters/india.py`
19. `src/krama/hip/discovery.py`
20. `src/krama/hiu/data_receive.py`
21. `src/krama/gateway/retry.py`
22. `src/krama/gateway/circuit_breaker.py`
23. `src/krama/whatsapp/sender.py`
24. `src/krama/ai/providers/router.py`

For each file, read the matching test next. For example, after reading
`src/krama/compliance/engine.py`, read `tests/test_compliance.py`.

## 19. How To Understand A Feature

Use this process for any module:

1. Find the public export.

   Check `src/krama/__init__.py` or the module's own `__init__.py`.

2. Find the model.

   Look for Pydantic classes. These tell you the shape of the data.

3. Find the service/client function.

   This is where behavior happens.

4. Find the tests.

   Tests show expected behavior more directly than comments.

5. Run only those tests.

   Keep the feedback loop small while learning.

6. Break it locally.

   Temporarily pass invalid input or remove a required field in a scratch
   script. Seeing the error teaches you how validation works.

## 20. Small Practice Exercises

Try these in order.

### Exercise 1: Build a patient with a local MRN

Create a `FHIRPatient` with `PatientIdentifier.local_mrn(...)` and print the
FHIR dictionary.

### Exercise 2: Create an Australia compliance check

Use `ComplianceEngine` with:

- country `AUS`
- identifier `australia_ihi`
- consent present
- encryption enabled
- residency `ap-southeast-2`

Then change the residency to `us-east-1` and observe the warning.

### Exercise 3: Try an unsupported identifier

Use country `GBR` with identifier `india_abha`. The compliance engine should
block it.

### Exercise 4: Add a custom template

Create a `ClinicalTemplate` and register it with `TemplateRegistry`.

### Exercise 5: Read a crypto failure test

Look for the test that confirms tampered encrypted data fails. This is the kind
of test security-sensitive modules need.

## 21. How To Add A New Country Later

When adding a country, update these areas:

1. Add country identifiers in `src/krama/fhir/resources/identifiers.py`.
2. Add a country adapter in `src/krama/adapters/`.
3. Add policy metadata in `src/krama/compliance/policies.py`.
4. Add universal template defaults in `src/krama/templates/universal.py`.
5. Add tests in:

   - `tests/test_adapters.py`
   - `tests/test_compliance.py`
   - `tests/test_universal_template.py`
   - `tests/test_global_adaptability_security.py`

6. Update `README.md` and `CHANGELOG.md`.

Do not add country-specific behavior deep inside generic FHIR resources unless
it truly belongs there. Prefer adapters, policies, and identifier models.

## 22. How To Add A New Specialty Later

When adding a specialty:

1. Add a domain module in `src/krama/templates/domains/`.
2. Export it from `src/krama/templates/domains/__init__.py`.
3. Make sure every template parses as `ClinicalTemplate`.
4. Add clinically accurate `TemplateSection` objects.
5. Add tests to confirm registry loading.
6. Think about country adaptation separately.

Specialty is about clinical workflow. Country is about identity, law,
compliance, coding, residency, and integrations.

## 23. Release Checklist

Before PyPI release:

```bash
pytest -v --cov=krama
ruff check src/ tests/ examples/
bandit -r src/ -ll
pip-audit
rm -rf build dist src/krama_core.egg-info
python -m build
twine check dist/*
```

Then upload:

```bash
twine upload dist/*
```

After upload:

```bash
python -m venv /tmp/krama-pypi-test
source /tmp/krama-pypi-test/bin/activate
pip install --pre krama-core==<version>
python -c "from krama import KramaClient; print('installed')"
```

## 24. Product Vision To Keep In Mind

Krama should become for healthcare what a strong regulation-aware platform is
for logistics or finance: the application developer should not hardcode every
country's rules manually.

The future direction:

```text
One SDK
    -> many specialties
    -> many countries
    -> safe identifiers
    -> structured FHIR records
    -> consent-aware exchange
    -> compliance guardrails
    -> secure communication
```

The hard part is not only writing code. The hard part is keeping clean
boundaries:

- FHIR resources should stay healthcare-data focused.
- Clinical templates should stay specialty focused.
- Country adapters should stay jurisdiction focused.
- Compliance policies should stay rule focused.
- Crypto should stay small, tested, and boring.
- AI should stay assistive, not authoritative.

If you keep those boundaries, Krama can grow without becoming fragile.

