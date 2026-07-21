# Krama Core

> Python-first ABDM/FHIR bundle generation for Indian healthcare products.

**Built by [Nirvya Labs](https://github.com/NirvyaLabs).**

Krama Core helps developers build secure healthcare integrations: ABDM-compliant
FHIR R4 bundles, HIP/HIU flows, encryption, clinical templates, gateway
resilience, WhatsApp messaging, AI-assisted clinical workflows, and country
adapters. It stays Python-first: Pydantic for input validation, plain Python
dictionaries for FHIR output, and optional extras for provider-specific services.

[![CI](https://github.com/NirvyaLabs/krama-core/actions/workflows/ci.yml/badge.svg)](https://github.com/NirvyaLabs/krama-core/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/krama-core.svg)](https://pypi.org/project/krama-core/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Installation

```bash
pip install krama-core
```

Optional integrations:

```bash
pip install "krama-core[ai]"
pip install "krama-core[whatsapp]"
```

For local development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

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

## Supported Bundles

Krama Core supports three ABDM care contexts through convenience functions:

- `create_op_consult_bundle()` for outpatient consultation records
- `create_prescription_bundle()` for prescription records
- `create_discharge_summary_bundle()` for inpatient discharge summaries

Each bundle is returned as a JSON-serializable Python dictionary.

## FHIR Builder API

For richer workflows, Krama Core includes resource builders and fluent document
builders:

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

The builder layer currently supports `OPConsultBuilder` and
`PrescriptionBuilder`, plus reusable FHIR resources for Patient, Practitioner,
Encounter, Condition, Observation, MedicationRequest, DiagnosticReport,
AllergyIntolerance, Procedure, Organization, and Composition.

## Encryption

Krama Core includes tested ECDH and AES-GCM helpers for secure health data
transfer flows:

```python
from krama.crypto import AESGCMCipher, ECDHKeyExchange

sender_private, sender_public = ECDHKeyExchange.generate_key_pair()
receiver_private, receiver_public = ECDHKeyExchange.generate_key_pair()

sender_secret = ECDHKeyExchange.derive_shared_secret(sender_private, receiver_public)
receiver_secret = ECDHKeyExchange.derive_shared_secret(receiver_private, sender_public)

sender_key = AESGCMCipher.derive_key(sender_secret)
receiver_key = AESGCMCipher.derive_key(receiver_secret)

ciphertext, nonce = AESGCMCipher.encrypt(b"clinical payload", sender_key)
plaintext = AESGCMCipher.decrypt(ciphertext, receiver_key, nonce)
```

## SDK Client

Krama Core also includes a secure async client foundation for ABDM workflows:

```python
from krama import KramaClient

async with KramaClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
) as krama:
    result = await krama.abha.create_via_mobile("+91 98765 43210")
    print(result.transaction_id)
```

Security defaults:

- Client secrets use Pydantic secret types and are redacted from repr/errors
- Gateway URLs must use HTTPS unless targeting localhost for tests
- Access tokens are cached and refreshed behind an async lock
- Gateway errors avoid echoing request payloads or secrets
- Tests use mock transports only; no real ABDM requests are made in CI

## HIP And HIU

HIP discovery callbacks should acknowledge immediately and defer all work:

```python
from krama.hip import DiscoveryHandler, DiscoveryMatch


async def find_care_contexts(request):
    return DiscoveryMatch(patient_abha=request.patient_abha, care_contexts=[])


handler = DiscoveryHandler(http_client=krama.http, processor=find_care_contexts)
ack = await handler.handle(callback_body)  # return this from your web handler

# Run outside the request path, for example in a background worker.
await handler.process_next()
```

Publishing validates the FHIR document bundle, creates and links a care context,
then notifies the gateway:

```python
await krama.hip.publish(
    patient_abha="ravi.kumar@abdm",
    bundle=bundle,
    care_context_reference="visit-2026-05-06",
    care_context_display="OP consultation, 6 May 2026",
)
```

HIU helpers cover consent, data requests, and encrypted payload receive/decrypt:

```python
from krama.hiu import ConsentRequest, DataRequest

consent = await krama.hiu.consents.request_consent(
    ConsentRequest(
        patient_abha="ravi.kumar@abdm",
        purpose="Care management",
        hiu_id="nirvya-hiu",
        date_range_from="2026-01-01",
        date_range_to="2026-12-31",
    )
)

await krama.hiu.data_requests.request_data(DataRequest(consent_id=consent.consent_id))
```

## Clinical Templates

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

Custom templates can be registered with the same Pydantic models:

```python
from krama.templates import ClinicalTemplate, TemplateSection

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

## Gateway Resilience

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

## WhatsApp

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

## AI

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

## Country Adapters

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
```

India delegates to Krama ABHA, HIP, and HIU modules. Australia and US adapters
currently expose accurate metadata and raise `NotImplementedError` for network
operations until their national integrations are added.

## What Krama Handles

- `Bundle.type = "document"`
- `Composition` as the first bundle entry
- Internal `urn:uuid:` references between resources
- Patient, practitioner, organization, encounter, diagnosis, and medication resources
- SNOMED CT coding fields for diagnoses and medications
- Pydantic validation for required inputs and FHIR gender values

## Development

Run the checks:

```bash
pytest -v --cov=krama
ruff check src/ tests/ examples/
bandit -r src/
pip-audit
python examples/basic_usage.py
```

Build and validate package artifacts:

```bash
python -m build
twine check dist/*
```

## Status

`1.0.0-alpha`. The SDK now covers the planned core layers, but provider-specific
integrations and national adapters will keep evolving before a stable `1.0.0`.

## Roadmap

- Local mock ABDM gateway for offline development
- Async webhook handler with callback reliability helpers
- Diagnostic Report and Immunization bundle types
- FHIR R4 bundle validator
- FastAPI integration examples

## Why "Krama"?

Krama means order, sequence, or method. ABDM integration is a strict sequence of
care contexts, callbacks, consent flows, and clinical records. Krama exists to
make that sequence easier to build and reason about.

## License

MIT
