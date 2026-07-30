# GitHub Issue Seeds

These issues are intended to be created on
`NirvyaLabs/krama-core` and labeled `good first issue`.

If GitHub CLI is installed and authenticated, create them with:

```bash
gh issue create --title "..." --label "good first issue" --body-file /tmp/body.md
```

Recommended additional labels are listed per issue.

## 1. Add basic FHIR resource validators

Labels: `good first issue`, `enhancement`, `fhir`

```text
Krama currently builds many FHIR R4 resources and bundles. Add lightweight
validators for the most common structural mistakes before a bundle is returned
or published.

Scope:
- Add validators for required resource fields such as `resourceType`, `id`, and
  references.
- Validate that document bundles have `type == "document"`.
- Validate that the first Bundle entry is a `Composition`.
- Validate that internal references use `urn:uuid:` when appropriate.
- Add focused tests with valid and invalid examples.

Non-goals:
- Do not build a full official FHIR validator.
- Do not add a heavy dependency unless clearly justified.

Suggested files:
- `src/krama/fhir/`
- `tests/test_fhir_builders.py`
- `tests/test_fhir_resources.py`
```

## 2. Add FHIR bundle validation before HIP publish

Labels: `good first issue`, `enhancement`, `fhir`, `hip`

```text
HIP publishing should reject obviously invalid FHIR bundles before attempting to
notify a gateway.

Scope:
- Add a validation step in the HIP publish flow.
- Reuse or introduce a small internal FHIR bundle validator.
- Return a clear Krama exception when validation fails.
- Add tests that verify invalid bundles do not trigger mocked gateway calls.

Non-goals:
- No real ABDM gateway calls.
- No full external FHIR validator integration in this issue.

Suggested files:
- `src/krama/hip/publish.py`
- `src/krama/fhir/`
- `tests/test_hip.py`
```

## 3. Add a cardiology clinical template

Labels: `good first issue`, `enhancement`, `templates`

```text
Add a cardiology clinical template to Krama's built-in clinical template
registry.

Scope:
- Create a cardiology domain template with clinically useful sections.
- Include fields for chest pain history, cardiovascular exam, ECG review,
  risk factors, assessment, plan, medications, and follow-up.
- Register the template so `TemplateRegistry` loads it automatically.
- Add tests confirming the template parses and is discoverable.

Suggested files:
- `src/krama/templates/domains/`
- `src/krama/templates/domains/__init__.py`
- `tests/test_templates.py`
```

## 4. Add a physiotherapy clinical template

Labels: `good first issue`, `enhancement`, `templates`

```text
Add a physiotherapy template for musculoskeletal and rehabilitation workflows.

Scope:
- Create a physiotherapy domain template.
- Include sections for presenting problem, pain score, functional limitations,
  range of motion, strength, special tests, treatment plan, exercises, and
  follow-up goals.
- Register it in the template registry.
- Add tests confirming it loads and has expected sections.

Suggested files:
- `src/krama/templates/domains/`
- `src/krama/templates/domains/__init__.py`
- `tests/test_templates.py`
```

## 5. Improve test coverage for compliance edge cases

Labels: `good first issue`, `test`, `security`

```text
Add more tests for compliance edge cases across countries.

Scope:
- Test missing consent or lawful basis.
- Test unsupported identifier types per country.
- Test data residency mismatch warnings.
- Test missing audit metadata warnings.
- Test minimum-necessary behavior for US and non-US policies.
- Keep all data synthetic.

Suggested files:
- `tests/test_compliance.py`
- `tests/test_global_adaptability_security.py`
```

## 6. Improve crypto test coverage for failure paths

Labels: `good first issue`, `test`, `security`

```text
Add additional crypto tests focused on invalid input and tamper detection.

Scope:
- Test decrypting with the wrong key fails.
- Test modified ciphertext fails.
- Test modified nonce or associated metadata fails, if supported.
- Test invalid public/private key input.
- Ensure tests use synthetic data only.

Suggested files:
- `src/krama/crypto/`
- `tests/test_crypto.py`
```

## 7. Add a Flask example app

Labels: `good first issue`, `documentation`, `examples`

```text
Add a minimal Flask example that shows how a developer can use Krama Core in a
small web app.

Scope:
- Add an example Flask app under `examples/`.
- Include one endpoint that creates a sample OP consult FHIR bundle.
- Include one endpoint that runs a compliance check with synthetic data.
- Add comments explaining this is not production auth or deployment code.
- Update README or example docs to point to the Flask example.

Non-goals:
- No database.
- No real patient data.
- No real ABDM gateway calls.

Suggested files:
- `examples/flask_app.py`
- `README.md`
```

## 8. Add Telugu documentation translations

Labels: `good first issue`, `documentation`, `translation`

```text
Add Telugu translations for starter documentation so more Indian healthcare
developers can understand Krama Core.

Scope:
- Add a Telugu quick-start document.
- Translate the project summary, installation steps, and first ABDM bundle
  example explanation.
- Keep code snippets unchanged.
- Mention that APIs and package names remain in English.

Suggested files:
- `docs/te/README.md`
- `README.md`
```

