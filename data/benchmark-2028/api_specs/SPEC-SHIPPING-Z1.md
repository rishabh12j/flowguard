---
document_id: SPEC-SHIPPING-Z1
document_type: api_spec
title: shipping-partner-api permissions
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-partner-api permissions

The shipping-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
