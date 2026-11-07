---
document_id: SPEC-LOYALTY-Z1
document_type: api_spec
title: loyalty-partner-api permissions
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api permissions

The loyalty-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
