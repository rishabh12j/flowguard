---
document_id: SPEC-ACCOUNTS-Z1
document_type: api_spec
title: accounts-partner-api permissions
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-partner-api permissions

The accounts-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
