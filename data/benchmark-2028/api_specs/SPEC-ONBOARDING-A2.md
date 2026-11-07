---
document_id: SPEC-ONBOARDING-A2
document_type: api_spec
title: onboarding-partner-api API
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-partner-api API

The onboarding-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
