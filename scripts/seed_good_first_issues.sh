#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required. Install it from https://cli.github.com/ and run gh auth login."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run gh auth login first."
  exit 1
fi

ensure_label() {
  local name="$1"
  local color="$2"
  local description="$3"

  gh label create "$name" --color "$color" --description "$description" >/dev/null 2>&1 || true
}

create_issue() {
  local title="$1"
  local labels="$2"
  local body="$3"

  gh issue create --title "$title" --label "$labels" --body "$body"
}

ensure_label "good first issue" "7057ff" "Good for new contributors"
ensure_label "fhir" "0e8a16" "FHIR resources, bundles, or validation"
ensure_label "hip" "1d76db" "Health Information Provider workflows"
ensure_label "templates" "5319e7" "Clinical templates and registry"
ensure_label "security" "b60205" "Security, privacy, or compliance hardening"
ensure_label "examples" "bfd4f2" "Runnable examples"
ensure_label "translation" "fbca04" "Documentation translation"
ensure_label "test" "d4c5f9" "Test coverage"

create_issue "Add basic FHIR resource validators" "good first issue,enhancement,fhir" \
"Krama currently builds many FHIR R4 resources and bundles. Add lightweight validators for the most common structural mistakes before a bundle is returned or published.

Scope:
- Add validators for required resource fields such as \`resourceType\`, \`id\`, and references.
- Validate that document bundles have \`type == \"document\"\`.
- Validate that the first Bundle entry is a \`Composition\`.
- Validate that internal references use \`urn:uuid:\` when appropriate.
- Add focused tests with valid and invalid examples.

Non-goals:
- Do not build a full official FHIR validator.
- Do not add a heavy dependency unless clearly justified.

Suggested files:
- \`src/krama/fhir/\`
- \`tests/test_fhir_builders.py\`
- \`tests/test_fhir_resources.py\`"

create_issue "Add FHIR bundle validation before HIP publish" "good first issue,enhancement,fhir,hip" \
"HIP publishing should reject obviously invalid FHIR bundles before attempting to notify a gateway.

Scope:
- Add a validation step in the HIP publish flow.
- Reuse or introduce a small internal FHIR bundle validator.
- Return a clear Krama exception when validation fails.
- Add tests that verify invalid bundles do not trigger mocked gateway calls.

Non-goals:
- No real ABDM gateway calls.
- No full external FHIR validator integration in this issue.

Suggested files:
- \`src/krama/hip/publish.py\`
- \`src/krama/fhir/\`
- \`tests/test_hip.py\`"

create_issue "Add a cardiology clinical template" "good first issue,enhancement,templates" \
"Add a cardiology clinical template to Krama's built-in clinical template registry.

Scope:
- Create a cardiology domain template with clinically useful sections.
- Include fields for chest pain history, cardiovascular exam, ECG review, risk factors, assessment, plan, medications, and follow-up.
- Register the template so \`TemplateRegistry\` loads it automatically.
- Add tests confirming the template parses and is discoverable.

Suggested files:
- \`src/krama/templates/domains/\`
- \`src/krama/templates/domains/__init__.py\`
- \`tests/test_templates.py\`"

create_issue "Add a physiotherapy clinical template" "good first issue,enhancement,templates" \
"Add a physiotherapy template for musculoskeletal and rehabilitation workflows.

Scope:
- Create a physiotherapy domain template.
- Include sections for presenting problem, pain score, functional limitations, range of motion, strength, special tests, treatment plan, exercises, and follow-up goals.
- Register it in the template registry.
- Add tests confirming it loads and has expected sections.

Suggested files:
- \`src/krama/templates/domains/\`
- \`src/krama/templates/domains/__init__.py\`
- \`tests/test_templates.py\`"

create_issue "Improve test coverage for compliance edge cases" "good first issue,test,security" \
"Add more tests for compliance edge cases across countries.

Scope:
- Test missing consent or lawful basis.
- Test unsupported identifier types per country.
- Test data residency mismatch warnings.
- Test missing audit metadata warnings.
- Test minimum-necessary behavior for US and non-US policies.
- Keep all data synthetic.

Suggested files:
- \`tests/test_compliance.py\`
- \`tests/test_global_adaptability_security.py\`"

create_issue "Improve crypto test coverage for failure paths" "good first issue,test,security" \
"Add additional crypto tests focused on invalid input and tamper detection.

Scope:
- Test decrypting with the wrong key fails.
- Test modified ciphertext fails.
- Test modified nonce or associated metadata fails, if supported.
- Test invalid public/private key input.
- Ensure tests use synthetic data only.

Suggested files:
- \`src/krama/crypto/\`
- \`tests/test_crypto.py\`"

create_issue "Add a Flask example app" "good first issue,documentation,examples" \
"Add a minimal Flask example that shows how a developer can use Krama Core in a small web app.

Scope:
- Add an example Flask app under \`examples/\`.
- Include one endpoint that creates a sample OP consult FHIR bundle.
- Include one endpoint that runs a compliance check with synthetic data.
- Add comments explaining this is not production auth or deployment code.
- Update README or example docs to point to the Flask example.

Non-goals:
- No database.
- No real patient data.
- No real ABDM gateway calls.

Suggested files:
- \`examples/flask_app.py\`
- \`README.md\`"

create_issue "Add Telugu documentation translations" "good first issue,documentation,translation" \
"Add Telugu translations for starter documentation so more Indian healthcare developers can understand Krama Core.

Scope:
- Add a Telugu quick-start document.
- Translate the project summary, installation steps, and first ABDM bundle example explanation.
- Keep code snippets unchanged.
- Mention that APIs and package names remain in English.

Suggested files:
- \`docs/te/README.md\`
- \`README.md\`"

