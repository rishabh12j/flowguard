---
document_id: SPEC-ACCOUNTS-A2
document_type: api_spec
title: accounts-partner-api API
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-partner-api API

The accounts-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
