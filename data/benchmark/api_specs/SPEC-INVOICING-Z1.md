---
document_id: SPEC-INVOICING-Z1
document_type: api_spec
title: invoicing-partner-api permissions
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api permissions

The invoicing-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
