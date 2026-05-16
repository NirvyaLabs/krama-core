# Changelog

All notable changes to Krama Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
