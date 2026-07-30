<p align="center">
  <img src="https://img.shields.io/pypi/v/krama-core?style=flat-square&color=0A6847" alt="PyPI version" />
  <img src="https://img.shields.io/pypi/pyversions/krama-core?style=flat-square" alt="Python versions" />
  <img src="https://github.com/NirvyaLabs/krama-core/actions/workflows/ci.yml/badge.svg" alt="CI" />
  <img src="https://img.shields.io/badge/license-MIT-0A6847?style=flat-square" alt="MIT license" />
</p>

<h1 align="center">Krama Core</h1>

<p align="center">
  <strong>Python-first FHIR, compliance, and healthcare integration toolkit.</strong>
  <br />
  Starting with India's ABDM. Architected for country-adaptive healthcare.
</p>

<p align="center">
  <em>Krama means order, sequence, or method. Krama Core brings order to health data workflows.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/krama-core/">PyPI</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#clinical-templates">Clinical Templates</a> ·
  <a href="#country-adapters">Country Adapters</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

Krama Core helps developers build secure healthcare integrations across
jurisdictions. It includes ABDM-compliant FHIR R4 bundles for India, generic FHIR
builders, HIP/HIU flows, encryption, clinical templates, gateway resilience,
WhatsApp messaging, AI-assisted clinical workflow helpers, global patient
identifiers, and country-aware compliance guardrails.

The architecture is intentionally layered:

- Clinical domains define **what care is documented**: general medicine,
  dentistry, ophthalmology, pediatrics, psychiatry, surgery, Ayurveda, and more.
- Country adapters define **how care is identified, protected, coded, and
  exchanged**: ABHA in India, IHI/MRN in Australia, MRN/MBI in the US, NHS
  Number/MRN in the UK, and local/custom identifiers elsewhere.
- Compliance policies define **what must be checked before processing data**:
  purpose, consent or lawful basis, encryption, residency, auditability, and
  minimum-necessary sharing.

This keeps Krama India-ready without making it India-only.

## Why Krama Core?

Healthcare interoperability is difficult because the hard parts stack on top of
each other:

- FHIR resources must be shaped correctly.
- ABDM callbacks have strict response patterns.
- Consent and care-context flows need reliable async handling.
- Health data exchange needs encryption and tamper detection.
- Different countries use different identifiers, coding systems, privacy laws,
  residency expectations, and network integrations.

Krama Core gives Python teams a single SDK surface for these layers.

```text
Clinical input
    -> template or builder
    -> FHIR resources
    -> FHIR document bundle
    -> compliance check
    -> encryption if needed
    -> gateway / HIP / HIU / country adapter
```

## Installation

```bash
pip install --pre krama-core
```

Optional integrations:

```bash
pip install --pre "krama-core[ai]"
pip install --pre "krama-core[whatsapp]"
```

Requirements:

- Python 3.10+
- Pydantic v2
- `httpx`
- `cryptography`

For local development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

### India ABDM Bundle

```python
import json

from krama.fhir import create_op_consult_bundle
from krama.fhir.bundles import (
    DiagnosisInfo,
    OrganizationInfo,
    PatientInfo,
    PractitionerInfo,
)

bundle = create_op_consult_bundle(
    patient=PatientInfo(
        name="Ravi Kumar",
        abha_address="ravi.kumar@abdm",
        gender="male",
        date_of_birth="1990-05-15",
    ),
    practitioner=PractitionerInfo(
        name="Dr. Priya Sharma",
        identifier="DOC-12345",
    ),
    organization=OrganizationInfo(
        name="District Hospital Guntur",
        hfr_id="IN0410000123",
    ),
    diagnosis=DiagnosisInfo(
        description="Essential hypertension",
        snomed_code="59621000",
        clinical_notes="BP 150/95, prescribed amlodipine 5mg",
    ),
    encounter_date="2026-05-06",
)

print(json.dumps(bundle, indent=2))
```

### SDK Facade

For application code, `KramaClient` exposes the core modules from one place:

```python
from krama import KramaClient
from krama.fhir.resources import FHIROrganization, FHIRPatient, FHIRPractitioner

krama = KramaClient(client_id="client-id", client_secret="client-secret")

bundle = (
    krama.fhir.op_consult()
    .set_patient(
        FHIRPatient(
            abha_id="ravi.kumar@abdm",
            name="Ravi Kumar",
            gender="male",
            birth_date="1990-05-15",
        )
    )
    .set_practitioner(FHIRPractitioner(identifier="DOC-12345", name="Dr. Sharma"))
    .set_organization(FHIROrganization(hfr_id="IN0410000123", name="Nirvya Clinic"))
    .set_encounter("2026-07-30")
    .add_chief_complaint("Diabetes follow-up", snomed_code="44054006")
    .build()
)

await krama.hip.publish(bundle)
```

### Global Patient Identity

```python
from krama.fhir.resources import FHIRPatient, PatientIdentifier

australia_patient = FHIRPatient(
    identifiers=[
        PatientIdentifier.australia_ihi("8003608166690503"),
        PatientIdentifier.australia_mrn("MRN-123", assigner="Royal Melbourne"),
    ],
    name="Amelia Brown",
    gender="female",
    birth_date="1988-04-12",
)

us_patient = FHIRPatient(
    identifiers=[
        PatientIdentifier.us_mrn("DENT-456", assigner="Smile Dental Boston"),
    ],
    name="Jordan Smith",
    gender="unknown",
    birth_date="1975-09-20",
)
```

### Country Compliance Check

```python
from krama.compliance import ComplianceContext, ComplianceEngine

result = ComplianceEngine().evaluate(
    ComplianceContext(
        country="AUS",
        purpose="Dental review",
        patient_identifiers=["australia_ihi"],
        consent_present=True,
        encrypted=True,
        data_residency_region="ap-southeast-2",
        requested_fields=["diagnosis", "medications"],
        necessary_fields=["diagnosis", "medications"],
        actor_id="dentist-1",
        audit_event_id="audit-1",
    )
)

assert result.passed
```

## Features

### ABDM Foundation

Krama Core includes SDK modules for ABDM-style workflows:

| Milestone | Module | What it covers |
| --- | --- | --- |
| M1 Identity | `krama.abha` | ABHA client and identity schemas |
| M2 HIP | `krama.hip` | Discovery, care contexts, linking, publishing |
| M3 HIU | `krama.hiu` | Consent, data requests, encrypted data receive/decrypt |

HIP discovery follows the required fast-response pattern:

```text
receive callback
    -> immediately acknowledge
    -> queue async processing
    -> worker responds through gateway API
```

Unit tests use mock transports only. CI does not call real ABDM gateways.

### FHIR R4 Bundle Builder

Krama supports both simple convenience functions and richer resource builders.

Convenience bundle functions:

- `create_op_consult_bundle()`
- `create_prescription_bundle()`
- `create_discharge_summary_bundle()`

Fluent builders:

- `OPConsultBuilder`
- `PrescriptionBuilder`

Reusable FHIR resources:

- `FHIRPatient`
- `FHIRPractitioner`
- `FHIROrganization`
- `FHIREncounter`
- `FHIRCondition`
- `FHIRObservation`
- `FHIRMedicationRequest`
- `FHIRDiagnosticReport`
- `FHIRAllergyIntolerance`
- `FHIRProcedure`
- `FHIRComposition`

Example:

```python
from krama.fhir import OPConsultBuilder
from krama.fhir.resources import FHIROrganization, FHIRPatient, FHIRPractitioner

bundle = (
    OPConsultBuilder()
    .set_patient(
        FHIRPatient(
            abha_id="ravi.kumar@abdm",
            name="Ravi Kumar",
            gender="male",
            birth_date="1990-05-15",
        )
    )
    .set_practitioner(
        FHIRPractitioner(identifier="DOC-12345", name="Dr. Priya Sharma")
    )
    .set_organization(
        FHIROrganization(hfr_id="IN0410000123", name="District Hospital Guntur")
    )
    .set_encounter("2026-05-06")
    .add_chief_complaint("Essential hypertension", snomed_code="59621000")
    .add_observation("8480-6", "Systolic blood pressure", 130, unit="mmHg")
    .add_medication("Amlodipine", "5mg daily", snomed_code="386864001")
    .build()
)
```

### Patient Identifiers

Patients can be identified by ABHA for India, national identifiers where a
country has one, or local medical record numbers scoped to the assigning
hospital/system.

Supported identifier helpers include:

- India: `india_abha()`, `india_abha_address()`
- Australia: `australia_ihi()`, `australia_mrn()`, `australia_medicare()`
- US: `us_mrn()`, `us_mbi()`
- UK: `uk_nhs_number()`, `uk_mrn()`
- General: `local_mrn()`, `custom()`

```python
from krama.fhir.resources import FHIRPatient, PatientIdentifier

uk_patient = FHIRPatient(
    identifiers=[
        PatientIdentifier.uk_nhs_number("9000000009"),
        PatientIdentifier.uk_mrn("MRN-UK-1", assigner="Guy's and St Thomas'"),
    ],
    name="Ava Taylor",
    gender="female",
    birth_date="1992-11-03",
)
```

Local MRNs must include either a FHIR `system` URI or an `assigner`; Krama derives
a stable local URN from the assigner to reduce collisions across hospitals.

### Encryption

Krama Core includes ECDH and AES-GCM helpers for secure health data transfer
flows:

```python
from krama.crypto import AESGCMCipher, ECDHKeyExchange

sender_private, sender_public = ECDHKeyExchange.generate_key_pair()
receiver_private, receiver_public = ECDHKeyExchange.generate_key_pair()

sender_secret = ECDHKeyExchange.derive_shared_secret(
    sender_private,
    receiver_public,
)
receiver_secret = ECDHKeyExchange.derive_shared_secret(
    receiver_private,
    sender_public,
)

sender_key = AESGCMCipher.derive_key(sender_secret)
receiver_key = AESGCMCipher.derive_key(receiver_secret)

ciphertext, nonce = AESGCMCipher.encrypt(b"clinical payload", sender_key)
plaintext = AESGCMCipher.decrypt(ciphertext, receiver_key, nonce)

assert plaintext == b"clinical payload"
```

AES-GCM provides authenticated encryption: if ciphertext or authentication data
is tampered with, decryption fails.

### Gateway Resilience

Gateway calls can be wrapped with retry, circuit breaker, and health checks:

```python
from krama.gateway import CircuitBreaker, RetryConfig, retry_gateway_call

breaker = CircuitBreaker()


@retry_gateway_call(RetryConfig(max_retries=3))
async def notify_gateway():
    return await krama.http.post("/v1/hip/health-information/notify", json={})


result = await breaker.execute(notify_gateway)
health = await krama.gateway_health.check()
print(health.connected, health.latency, health.last_successful_call)
```

Retries are limited to timeouts and 5xx responses. 4xx gateway responses are
treated as client errors and are not retried.

### Clinical Templates

Krama Core ships clinical form templates across 12 medical domains, so one SDK
can support allopathy, dentistry, Ayurveda, homeopathy, surgery, pediatrics,
ophthalmology, OB-GYN, psychiatry, dermatology, orthopedics, and ENT.

```python
from krama.templates import TemplateRegistry

registry = TemplateRegistry()

template = registry.get("ayurveda", "prakriti_assessment")
print(template.name)
print([section.label for section in template.sections])

for domain in registry.list_domains():
    print(domain)
```

Built-in domains:

| Domain | Example structure |
| --- | --- |
| General medicine | SOAP note |
| Dentistry | Dental chart, FDI notation, procedures |
| Ayurveda | Prakriti, Vikriti, Nadi Pariksha, Ashtavidha Pariksha |
| Homeopathy | Case taking, modalities, miasmatic analysis, repertorisation |
| Surgery | Pre-op, operative note, post-op follow-up |
| Pediatrics | Growth-adjusted SOAP, immunization review, dosing flags |
| Ophthalmology | Visual acuity, IOP, fundus, refraction, slit lamp |
| OB-GYN | Antenatal and postnatal workflows |
| Psychiatry | Mental Status Exam, risk assessment, treatment plan |
| Dermatology | Lesion morphology, distribution, skin exam |
| Orthopedics | MSK exam, ROM, special tests, imaging review |
| ENT | Ear, nose, throat exam, audiometry, endoscopy findings |

Custom templates can be registered with the same Pydantic models:

```python
from krama.templates import ClinicalTemplate, TemplateRegistry, TemplateSection

registry = TemplateRegistry()
registry.register(
    ClinicalTemplate(
        domain="allopathy",
        encounter_type="followup",
        name="Follow-up Visit",
        description="Short follow-up visit template",
        sections=[
            TemplateSection(
                id="interval_history",
                label="Interval History",
                type="textarea",
                required=True,
            )
        ],
        vitals=["bp", "weight"],
        coding_system="icd10",
        prescription_type="standard",
    )
)
```

### Universal Adaptive Template

For global products, Krama includes one robust template that adapts by country.
It keeps the same clinical shape everywhere while changing identifier guidance,
coding system, compliance frameworks, and residency metadata per jurisdiction:

```python
from krama.templates import UniversalTemplateContext, create_universal_template

template = create_universal_template(UniversalTemplateContext(country="AU"))

print(template.jurisdiction)  # AUS
print(template.coding_system)  # icd10_am
print(template.metadata["identifier_types"])
```

Supported defaults are included for India, Australia, US, and UK. Unknown
countries fall back to a conservative global template using local/custom
identifiers.

### Compliance Engine

Krama includes a conservative compliance guardrail engine. It does not replace
legal review, but it gives product teams a common way to block unsafe workflows
and surface warnings before records are signed, shared, published, or requested.

```python
from krama.compliance import ComplianceContext

result = krama.compliance.evaluate(
    ComplianceContext(
        country="US",
        purpose="Referral",
        patient_identifiers=["us_mrn"],
        lawful_basis="treatment",
        encrypted=True,
        requested_fields=["diagnosis", "medications"],
        necessary_fields=["diagnosis", "medications"],
        actor_id="clinician-1",
        audit_event_id="audit-1",
    )
)

if not result.passed:
    print(result.blockers)
```

The first rule packs cover India, Australia, US, and UK. They check for patient
identity, supported identifier type, purpose of use, consent or lawful basis,
encryption, data residency, minimum-necessary data sharing, and auditability.

The compliance engine is a software guardrail, not legal advice. Production
teams should still complete legal, security, privacy, and clinical governance
review for each deployment.

### Country Adapters

Country adapters give the SDK a stable surface for national health networks:

```python
adapter = krama.adapter("IND")

identity = await adapter.verify_patient_identity(
    {"abha_number": "12345678901234"}
)
transaction_id = await adapter.publish_health_record(bundle)
consent = await adapter.request_consent("ravi.kumar@abdm", "Care management")

print(adapter.get_coding_system())
print(adapter.get_drug_formulary())
print(adapter.get_data_residency_region())
print(adapter.get_supported_patient_identifiers())
```

India delegates to Krama ABHA, HIP, and HIU modules. Australia, UK, and US
adapters currently expose metadata and identifier preferences, and raise
`NotImplementedError` for network operations until their national integrations
are added.

| Country | Preferred patient identifiers | Coding | Residency |
| --- | --- | --- | --- |
| India | ABHA, ABHA address, local MRN | ICD-10 | `ap-south-1` |
| Australia | IHI, local MRN, Medicare | ICD-10-AM | `ap-southeast-2` |
| US | MRN, MBI, local MRN | ICD-10-CM | `us-east-1` |
| UK | NHS Number, local MRN | ICD-10 | `eu-west-2` |

### WhatsApp

The WhatsApp module normalizes inbound messages and routes outbound sends
through a configured provider:

```python
from krama.whatsapp import TemplateMessage, WhatsAppSender
from krama.whatsapp.providers import MetaDirectProvider

provider = MetaDirectProvider(
    access_token="meta-token",
    phone_number_id="phone-number-id",
)
sender = WhatsAppSender(provider)

await sender.send_text("919876543210", "Your appointment is confirmed.")
await sender.send_template(
    "919876543210",
    TemplateMessage(
        template_name="appointment_reminder",
        params={"name": "Ravi", "date": "6 May"},
        language="en",
    ),
)
```

Supported providers: AiSensy, Gupshup, and Meta WhatsApp Cloud API. Webhooks are
parsed into one `InboundMessage` schema regardless of provider.

### AI

Clinical AI helpers are optional and provider-routed. All clinical outputs carry
the same safety rule: AI output is a suggestion only and requires physician
review.

```python
from krama.ai import AIAssistant
from krama.ai.providers import GeminiProvider, GroqProvider, LLMRouter

router = LLMRouter(
    [
        GeminiProvider(api_key="gemini-key"),
        GroqProvider(api_key="groq-key"),
    ]
)
ai = AIAssistant(router)

suggestions = await ai.clinical_nlp.suggest_soap_improvement(
    "assessment",
    "Essential hypertension",
)
codes = await ai.icd_coder.suggest_codes("Essential hypertension")
triage = await ai.triage.classify_urgency("fever for three days")
drug_check = ai.drug_checker.check_interactions(
    medications=["Warfarin", "Aspirin"],
    patient_allergies=[],
)
```

The router tries providers in priority order and automatically fails over when a
provider errors or returns an empty response.

## Framework Agnostic

Krama Core can be used from any Python framework or from standalone async
scripts.

FastAPI:

```python
from fastapi import FastAPI
from krama import KramaClient

app = FastAPI()
krama = KramaClient(client_id="client-id", client_secret="client-secret")


@app.post("/health")
async def health():
    result = await krama.gateway_health.check()
    return {"connected": result.connected}
```

Standalone:

```python
import asyncio

from krama import KramaClient


async def main():
    async with KramaClient(
        client_id="client-id",
        client_secret="client-secret",
    ) as krama:
        print(krama.adapter("IND").get_coding_system())


asyncio.run(main())
```

## Architecture

```text
src/krama/
├── auth/          # ABDM token management
├── abha/          # M1 identity client and schemas
├── hip/           # M2 Health Information Provider flows
├── hiu/           # M3 Health Information User flows
├── gateway/       # Retry, circuit breaker, health checks
├── fhir/          # FHIR R4 resources and composition builders
├── crypto/        # ECDH X25519 and AES-GCM helpers
├── templates/     # Clinical templates and universal adaptive template
├── compliance/    # Country-aware compliance guardrails
├── adapters/      # India, Australia, US, and UK adapter surfaces
├── ai/            # Clinical NLP, ICD coding, drug checks, triage
├── whatsapp/      # Multi-provider WhatsApp messaging
└── utils/         # HTTP helpers
```

## Learning The Codebase

If you are new to Krama Core, start with the learning guide:

[docs/KRAMA_LEARNING_GUIDE.md](docs/KRAMA_LEARNING_GUIDE.md)

It explains the architecture, what each module does, how FHIR, crypto, HIP/HIU,
templates, adapters, and compliance connect, and which files to read first.

## Development

Run the checks:

```bash
pytest -v --cov=krama
ruff check src/ tests/ examples/
bandit -r src/ -ll
pip-audit
python examples/basic_usage.py
```

Build and validate package artifacts:

```bash
python -m build
twine check dist/*
```

## Contributing

We welcome contributions from developers, healthcare professionals, and
translators worldwide.

Good places to start:

- FHIR validators
- new clinical templates
- test coverage improvements
- Flask and FastAPI examples
- documentation improvements
- Telugu and other language translations
- country adapter metadata and implementation work

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and PR guidelines.

Good first issues are labeled on the
[Issues page](https://github.com/NirvyaLabs/krama-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

## Status

`1.0.0-alpha.4`. The SDK now covers the planned core layers, but provider-specific
integrations and national adapters will keep evolving before a stable `1.0.0`.

## Roadmap

- Local mock ABDM gateway for offline development
- FHIR R4 bundle validator
- FastAPI and Flask integration examples
- Additional national adapters
- More country-specific compliance policy packs
- Additional clinical domains and translations

## Part Of Nirvya Labs

Krama Core is the open-source foundation for Nirvya Labs healthcare tooling:
secure clinical data infrastructure for doctors, care teams, and patient-facing
products.

## License

MIT. See [LICENSE](LICENSE).
