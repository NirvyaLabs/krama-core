# Contributing to Krama Core

Thank you for helping improve Krama Core. This project is maintained by
[Nirvya Labs](https://github.com/NirvyaLabs) and welcomes contributions from
developers, clinicians, implementers, and documentation writers.

Krama Core is a Python SDK for secure healthcare interoperability. It includes
FHIR R4 builders, ABDM workflows, country-aware patient identifiers, compliance
guardrails, encryption, clinical templates, gateway resilience, WhatsApp
integrations, and AI-assisted clinical workflow helpers.

## Development Setup

Fork and clone the repository:

```bash
git clone git@github.com:YOUR_USERNAME/krama-core.git
cd krama-core
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Krama Core in editable mode with development tools:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest -v
pytest -v --cov=krama
```

Run linting:

```bash
ruff check src/ tests/ examples/
```

Run security checks before larger PRs:

```bash
bandit -r src/ -ll
pip-audit
```

Build and validate package metadata:

```bash
python -m build
twine check dist/*
```

## Branch Workflow

Create a focused branch from `main`:

```bash
git checkout main
git pull
git checkout -b feat/short-description
```

Use a branch name that reflects the change:

- `feat/fhir-validator`
- `fix/patient-identifier-validation`
- `docs/template-guide`
- `test/crypto-edge-cases`

## Commit Style

Use concise conventional commits:

- `feat:` new behavior
- `fix:` bug fixes
- `docs:` documentation-only changes
- `test:` tests only
- `refactor:` internal cleanup without behavior changes
- `chore:` maintenance

Examples:

```text
feat: add FHIR patient identifier validator
docs: explain compliance engine flow
test: cover AES-GCM tamper detection
```

## Pull Request Guidelines

Before opening a pull request:

- Keep the PR focused on one feature, fix, or documentation area.
- Add or update tests for behavior changes.
- Update documentation when public APIs change.
- Run `pytest -v`, `ruff check src/ tests/ examples/`, and relevant security
  checks.
- Make sure no real patient data, tokens, credentials, or sandbox secrets are
  committed.

Every PR should include:

- What changed.
- Why the change is needed.
- How it was tested.
- Any remaining limitations or follow-up work.

## Healthcare And Security Expectations

Krama handles healthcare-adjacent data structures, so contributions must be
careful by default.

Do:

- Use Pydantic models for structured input and validation.
- Keep FHIR output deterministic and JSON-serializable.
- Avoid real patient data in tests, examples, docs, and fixtures.
- Mock network calls in tests.
- Add failure-path tests for security-sensitive behavior.
- Treat AI output as suggestions requiring clinician review.

Do not:

- Hardcode API keys, bearer tokens, patient identifiers, or credentials.
- Add network calls to unit tests.
- Swallow cryptography or compliance errors silently.
- Present compliance checks as legal advice.
- Present AI suggestions as diagnosis, prescription, or clinical authority.

## Areas That Need Help

Good starter areas include:

- FHIR validators for common resource and bundle errors.
- New specialty templates such as physiotherapy, cardiology, radiology, and
  nutrition.
- More test coverage for edge cases and failure paths.
- Flask and FastAPI example apps.
- Documentation improvements and diagrams.
- Telugu, Hindi, and other Indian language translations.
- Country adapter metadata and policy expansion.

Look for issues tagged `good first issue`.

## Reporting Bugs

Use the bug report template and include:

- Krama Core version.
- Python version.
- Operating system.
- Minimal code to reproduce the issue.
- Full traceback if there is an exception.
- Whether the bug affects FHIR output, crypto, compliance, templates, gateway
  calls, AI, WhatsApp, HIP, or HIU.

## Requesting Features

Use the feature request template and include:

- The healthcare workflow or developer problem.
- The country or compliance context, if relevant.
- The FHIR resources or clinical templates involved.
- Example API usage if you have a preferred design.

## Code Of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By
participating, you agree to help keep Krama Core welcoming, respectful, and
useful for the healthcare developer community.
