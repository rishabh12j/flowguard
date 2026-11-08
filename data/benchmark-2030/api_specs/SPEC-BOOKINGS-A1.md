---
document_id: SPEC-BOOKINGS-A1
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

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
