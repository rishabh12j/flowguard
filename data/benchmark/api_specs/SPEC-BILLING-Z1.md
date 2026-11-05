---
document_id: SPEC-BILLING-Z1
document_type: api_spec
title: billing-partner-api permissions
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api permissions

The billing-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
