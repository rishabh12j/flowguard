---
document_id: SPEC-SUBSCRIPTIONS-A2
document_type: api_spec
title: subscriptions-partner-api API
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api API

The subscriptions-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
