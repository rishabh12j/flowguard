---
document_id: SPEC-REWARDS-Z1
document_type: api_spec
title: rewards-partner-api permissions
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api permissions

The rewards-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
