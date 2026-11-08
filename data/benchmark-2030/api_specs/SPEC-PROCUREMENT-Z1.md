---
document_id: SPEC-PROCUREMENT-Z1
document_type: api_spec
title: procurement-partner-api permissions
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-partner-api permissions

The procurement-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
