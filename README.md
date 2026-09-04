<div align="center">

# Krama Core

**Open, FHIR-native, ABDM-native healthcare interoperability foundation.**

*The developer platform for building compliant digital health applications in India - and, in time, Australia.*

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Status: Early Development](https://img.shields.io/badge/status-early_development-orange.svg)
![FHIR R4](https://img.shields.io/badge/FHIR-R4-red.svg)

</div>

---

## What is Krama Core

Krama Core is an open-source, FHIR R4-native backend for building healthcare applications on top of India's Ayushman Bharat Digital Mission (ABDM). Think of it as a healthcare developer platform - a FHIR datastore, APIs, auth, access control, and automation - with ABDM/ABHA and NRCeS FHIR profiles built in, so you don't rebuild that foundation for every app.

It exists because healthcare software is too often built on proprietary data models and closed integration layers that make interoperability hard. Krama Core keeps the interoperability foundation **open** - you can download it, run it, modify it, and deploy it in your own infrastructure without lock-in.

> **Not a replacement for healthcare product engineering.** Krama Core removes the undifferentiated infrastructure work. It does not remove clinical data modelling, security hardening, or compliance - those remain real work, and where we (Nirvya Labs) offer managed services.

## Core capabilities (target)

| Capability | Description |
|---|---|
| **FHIR R4 datastore** | Clinical data stored natively as FHIR resources (PostgreSQL) |
| **REST + GraphQL APIs** | Standards-based access to resources, search, and operations |
| **ABDM / ABHA integration** | ABHA-based identity, consent artifacts, ABDM HI-Type endpoints |
| **NRCeS FHIR profiles** | Prescription, Consultation/OP note, Diagnostic Report, Discharge Summary - validated against NRCeS R4 profiles |
| **Auth** | OAuth 2.0 / OpenID Connect / SMART-on-FHIR |
| **Consent-driven access policies** | Declarative, consent-artifact-driven access control (DPDP-aligned) |
| **Automation (Bots)** | Serverless custom logic - the voice-scribe pipeline runs here |
| **Subscriptions** | Event-driven notifications on resource changes |
| **Self-hostable** | Containerised; deployable on MeitY-empanelled cloud environments |

## Architecture

Krama Core is **Python-first**.

- **Platform (FHIR, APIs, ABDM/consent, auth, automation):** Python + FastAPI, PostgreSQL, Redis. Python is chosen for its maturity in FHIR (`fhir.resources`), its first-class fit with the AI/voice stack, and contributor accessibility.
- **AI / voice pipeline:** Python (open-weight ASR + clinical NLP). Integrates as a Bot.
- **Performance-critical modules (future, optional):** where profiling proves a real bottleneck - e.g. high-throughput FHIR validation, audio-stream ingestion, or consent verification - a **Rust** module may be introduced behind a Python binding (PyO3) or as a small standalone service. Rust is a targeted optimisation layer, **not** a second implementation of the platform. We do not maintain two parallel codebases.

```
┌──────────────────────────────────────────────────────┐
│  Applications (Nirvya Health HMS, patient apps, ...)  │
├──────────────────────────────────────────────────────┤
│                    Krama Core                         │
│  FHIR R4 API · ABDM/ABHA · Consent · Auth · Bots      │
│                  (Python / FastAPI)                   │
│        └─ optional Rust modules for hot paths ─┘      │
├──────────────────────────────────────────────────────┤
│              PostgreSQL  ·  Redis                     │
└──────────────────────────────────────────────────────┘
```

## Getting started

> Early development - APIs and setup are changing. These steps are indicative.

```bash
# Prerequisites: Python 3.11+, PostgreSQL, Redis, Docker
git clone https://github.com/nirvya/krama-core.git
cd krama-core

# Configuration
cp .env.example .env        # set DB, Redis, ABDM sandbox credentials

# Run with Docker
docker compose up

# API available at http://localhost:8000
# FHIR endpoint:   http://localhost:8000/fhir/R4
```

See `docs/` for the ABDM sandbox setup and the first round-trip (ABHA link → consent artifact → write a NRCeS-valid FHIR bundle → read it back).

## The open / paid / proprietary boundary

Krama Core is deliberately open. To keep that boundary clean:

- **Open (this repo, Apache 2.0):** the interoperability foundation - FHIR, APIs, ABDM/consent integration, auth, automation. We do **not** make the essential interoperability layer proprietary.
- **Paid (Nirvya Labs services):** managed deployment, integration, security hardening, audit evidence, offline sync, SLAs, training, field implementation - what you can't get merely by downloading the code.
- **Proprietary (separate, not in this repo):** Nirvya's dialect-adapted voice models and the clinical-speech data behind them. This repo may reference an **open-weight** reference voice pipeline; the tuned models are not part of the open core.

## Roadmap

- [ ] ABDM sandbox round-trip: ABHA → consent → NRCeS-valid FHIR bundle → read back
- [ ] Core FHIR R4 datastore + REST API
- [ ] ABHA-based auth + consent-artifact access policies
- [ ] NRCeS profile validation (Prescription, Consultation, Diagnostic Report, Discharge Summary)
- [ ] Bots/automation runtime (hosts the voice scribe)
- [ ] Self-host deployment profile for MeitY-empanelled cloud
- [ ] GraphQL API · Subscriptions
- [ ] (Future) Australia: My Health Record / AU-Core profiles

## Contributing

Early-stage - contribution guidelines are being written. If you're working on ABDM/FHIR interoperability and want to help, open an issue to start a conversation.

## License

Apache License 2.0 - see [LICENSE](LICENSE). You may use, modify, and deploy Krama Core freely, including in your own infrastructure.

---

<div align="center">
<sub>Part of <a href="https://github.com/nirvya">Nirvya Labs</a> · Open rails for digital health.</sub>
</div>
