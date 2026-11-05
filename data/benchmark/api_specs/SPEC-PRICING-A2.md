---
document_id: SPEC-PRICING-A2
document_type: api_spec
title: pricing-partner-api API
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-partner-api API

The pricing-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
