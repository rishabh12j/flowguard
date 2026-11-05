---
document_id: SPEC-PROCUREMENT-A2
document_type: api_spec
title: procurement-partner-api API
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-partner-api API

The procurement-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
