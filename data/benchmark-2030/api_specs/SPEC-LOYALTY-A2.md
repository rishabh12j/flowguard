---
document_id: SPEC-LOYALTY-A2
document_type: api_spec
title: loyalty-partner-api API
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api API

The loyalty-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
