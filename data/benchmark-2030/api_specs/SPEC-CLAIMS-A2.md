---
document_id: SPEC-CLAIMS-A2
document_type: api_spec
title: claims-partner-api API
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api API

The claims-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
