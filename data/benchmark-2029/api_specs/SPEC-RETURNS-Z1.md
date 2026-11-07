---
document_id: SPEC-RETURNS-Z1
document_type: api_spec
title: returns-partner-api permissions
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-partner-api permissions

The returns-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
