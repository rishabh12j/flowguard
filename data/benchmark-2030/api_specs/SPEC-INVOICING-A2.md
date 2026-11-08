---
document_id: SPEC-INVOICING-A2
document_type: api_spec
title: invoicing-partner-api API
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api API

The invoicing-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
