---
name: Bug report
about: Report incorrect behavior, validation failures, or integration problems
title: "[BUG] "
labels: bug
assignees: ""
---

## Summary

Describe the bug clearly in one or two sentences.

## Affected Area

Select the area that best matches the issue:

- [ ] FHIR bundles or resources
- [ ] Patient identifiers
- [ ] Clinical templates
- [ ] Compliance engine
- [ ] Crypto / encryption
- [ ] ABDM / ABHA
- [ ] HIP
- [ ] HIU
- [ ] Gateway retry / circuit breaker
- [ ] WhatsApp
- [ ] AI helpers
- [ ] Country adapters
- [ ] Documentation
- [ ] Other

## Reproduction

Please provide the smallest code sample that reproduces the bug.

```python
from krama import KramaClient

# Minimal reproduction here
```

Steps:

1. Install version `...`
2. Run the code above
3. Observe the error

## Expected Behavior

What should have happened?

## Actual Behavior

What happened instead? Include the full traceback if available.

```text
Paste traceback here
```

## Environment

- OS:
- Python version:
- Krama Core version:
- Installation method: `pip`, editable install, source checkout, other

## Safety Check

- [ ] This report does not include real patient data.
- [ ] This report does not include API keys, tokens, or credentials.

## Additional Context

Add screenshots, logs, FHIR snippets, ABDM callback examples, or links to
relevant documentation if helpful. Use synthetic data only.
