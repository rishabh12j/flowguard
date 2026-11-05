---
document_id: SPEC-INVENTORY-A2
document_type: api_spec
title: inventory-partner-api API
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api API

The inventory-partner-api API contract.

## Authentication

Each client has one registered key. A key that isn't registered is rejected with 401 Unauthorized.

## Requests

Requests are idempotent by record ID.
