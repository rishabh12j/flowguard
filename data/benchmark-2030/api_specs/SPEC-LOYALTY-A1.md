---
document_id: SPEC-LOYALTY-A1
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

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
