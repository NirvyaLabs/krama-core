# Krama Core

> Python-first ABDM/FHIR bundle generation for Indian healthcare products.

**Built by [Nirvya Labs](https://github.com/NirvyaLabs).**

Krama Core helps developers generate ABDM-compliant FHIR R4 document bundles
without hand-assembling every resource and reference. It is intentionally small:
Pydantic for input validation, plain Python dictionaries for output, and no
runtime dependency beyond `pydantic`.

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
