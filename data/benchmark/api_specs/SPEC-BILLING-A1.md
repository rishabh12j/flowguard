---
document_id: SPEC-BILLING-A1
document_type: api_spec
title: billing-partner-api API
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api API

The billing-partner-api API contract.

## Authentication

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
