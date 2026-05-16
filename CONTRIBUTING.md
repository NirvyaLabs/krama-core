# Contributing to Krama Core

Thank you for your interest in contributing! Krama Core is maintained by
[Nirvya Labs](https://github.com/NirvyaLabs) and we welcome contributions
from anyone who wants to improve ABDM integration tooling.

## Getting Started

```bash
# Fork and clone
git clone git@github.com:YOUR_USERNAME/Krama-Core.git
cd Krama-Core

# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Verify
pytest -v
ruff check src/ tests/ examples/
```

## Development Workflow

1. Create a branch from `main`: `git checkout -b feat/your-feature`
2. Make changes
3. Run checks before committing:
   ```bash
   pytest -v
   ruff check src/ tests/ examples/
   ruff format src/ tests/ examples/
   ```
4. Use conventional commit messages:
   - `feat:` new features
   - `fix:` bug fixes
   - `docs:` documentation
   - `test:` test changes
   - `chore:` maintenance
5. Push and open a Pull Request against `main`

## What Can I Contribute?

**New bundle types** — We need Diagnostic Report, Immunization Record,
Wellness Record, and Health Document Record bundles.

**Tests** — Edge cases, FHIR validation, integration tests with the ABDM
sandbox.

**Documentation** — Docstrings, usage guides, translations (Hindi and Telugu
especially welcome).

Look for issues tagged `good first issue` for scoped starter tasks.

## Code Style

- **ruff** for linting and formatting (line length: 88)
- Type hints encouraged
- All public functions need docstrings
- Keep dependencies minimal — every new one needs justification

## Testing

- Every new feature must include tests
- Tests live in `tests/` and mirror source structure
- Aim for descriptive names: `test_prescription_bundle_links_medication_to_patient`

## Pull Request Guidelines

- One feature or fix per PR
- Clear description of what changed and why
- Reference related issues
- All CI checks must pass before merge

## Reporting Issues

- Use the provided issue templates
- Include Python version, OS, and Krama Core version
- For bugs: include a minimal reproducible example
- For features: describe the ABDM use case it addresses

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By
participating, you agree to uphold a welcoming and inclusive environment.
