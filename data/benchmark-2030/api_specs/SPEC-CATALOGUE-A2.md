---
document_id: SPEC-CATALOGUE-A2
document_type: api_spec
title: catalogue-partner-api API
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api API

The catalogue-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
