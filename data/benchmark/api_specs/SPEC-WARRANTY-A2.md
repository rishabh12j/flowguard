---
document_id: SPEC-WARRANTY-A2
document_type: api_spec
title: warranty-partner-api API
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api API

The warranty-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
