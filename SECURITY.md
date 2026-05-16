# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Krama Core, please report it
responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email **rishi@nirvyalabs.com** with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

We will acknowledge receipt within 48 hours and aim to release a patch
within 7 days for critical issues.

## Scope

This policy covers the `krama-core` Python package and its dependencies.
It does not cover third-party ABDM sandbox environments or FHIR validators.

## Security Measures

Krama Core takes the following precautions:

- **No secrets in code** — No API keys, tokens, or credentials are stored
  in the repository
- **Dependency scanning** — `pip-audit` runs on every CI build
- **Static analysis** — `bandit` scans for common Python security issues
- **Input validation** — All inputs pass through Pydantic models before
  processing
- **Minimal dependencies** — Only `pydantic` as a runtime dependency to
  reduce attack surface
