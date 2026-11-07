---
document_id: SPEC-CATALOGUE-Z1
document_type: api_spec
title: catalogue-partner-api permissions
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api permissions

The catalogue-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
