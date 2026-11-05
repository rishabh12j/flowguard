---
document_id: SPEC-REWARDS-A1
document_type: api_spec
title: rewards-partner-api API
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api API

The rewards-partner-api API contract.

## Authentication

Clients use a client credential that is valid for 90 days. An expired credential is rejected with 401 Unauthorized.

## Requests

Each request carries one record. A successful request returns 201 Created.
