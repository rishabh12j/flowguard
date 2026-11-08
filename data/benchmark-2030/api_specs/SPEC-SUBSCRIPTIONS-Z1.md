---
document_id: SPEC-SUBSCRIPTIONS-Z1
document_type: api_spec
title: subscriptions-partner-api permissions
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api permissions

The subscriptions-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
