---
document_id: SPEC-BOOKINGS-A2
document_type: api_spec
title: bookings-partner-api API
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-partner-api API

The bookings-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
