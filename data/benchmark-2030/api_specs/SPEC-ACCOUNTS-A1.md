---
document_id: SPEC-ACCOUNTS-A1
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

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
