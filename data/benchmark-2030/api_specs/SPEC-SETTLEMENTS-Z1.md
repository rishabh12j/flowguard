---
document_id: SPEC-SETTLEMENTS-Z1
document_type: api_spec
title: settlements-partner-api permissions
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api permissions

The settlements-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
