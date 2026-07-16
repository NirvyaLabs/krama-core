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

Krama Core v0.1 supports three ABDM care contexts:

- `create_op_consult_bundle()` for outpatient consultation records
- `create_prescription_bundle()` for prescription records
- `create_discharge_summary_bundle()` for inpatient discharge summaries

Each bundle is returned as a JSON-serializable Python dictionary.

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
