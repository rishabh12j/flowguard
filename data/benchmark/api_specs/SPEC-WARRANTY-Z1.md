---
document_id: SPEC-WARRANTY-Z1
document_type: api_spec
title: warranty-partner-api permissions
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api permissions

The warranty-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
