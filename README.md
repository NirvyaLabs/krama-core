# Krama Core

> Python-first ABDM/FHIR bundle generation for Indian healthcare products.

**Built by [Nirvya Labs](https://github.com/NirvyaLabs).**

Krama Core helps developers generate ABDM-compliant FHIR R4 document bundles
without hand-assembling every resource and reference. It is intentionally small:
Pydantic for input validation, plain Python dictionaries for output, and no
runtime dependency beyond `pydantic`.

[![CI](https://github.com/NirvyaLabs/krama-core/actions/workflows/ci.yml/badge.svg)](https://github.com/NirvyaLabs/krama-core/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/krama-core.svg)](https://pypi.org/project/krama-core/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Installation

```bash
pip install krama-core
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
pytest -v
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

Alpha. The API is small and usable, but still expected to evolve as ABDM
integration coverage expands.

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
