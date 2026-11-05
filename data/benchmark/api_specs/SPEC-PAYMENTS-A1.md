---
document_id: SPEC-PAYMENTS-A1
document_type: api_spec
title: payments-partner-api API
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-partner-api API

The payments-partner-api API contract.

## Authentication

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
