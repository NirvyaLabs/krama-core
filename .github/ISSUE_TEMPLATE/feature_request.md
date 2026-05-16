---
name: Feature Request
about: Suggest a new feature or bundle type
title: "[FEATURE] "
labels: enhancement
assignees: ''
---

## Summary

One-line description of the feature.

## ABDM Use Case

Describe the ABDM integration scenario this feature addresses.
Which ABDM milestone (M1/M2/M3) does it relate to?
Which FHIR profile or care context does it involve?

## Proposed Solution

How you think this should work. Include example API usage if possible:

```python
# How a developer would use this feature
from krama.fhir import create_diagnostic_report_bundle

bundle = create_diagnostic_report_bundle(
    patient=...,
    lab_results=[...],
)
```

## Alternatives Considered

Any other approaches you've thought about.

## Additional Context

Links to relevant ABDM docs, FHIR profiles, or related issues.
