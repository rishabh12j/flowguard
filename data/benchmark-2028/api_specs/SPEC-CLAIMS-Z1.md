---
document_id: SPEC-CLAIMS-Z1
document_type: api_spec
title: claims-partner-api permissions
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api permissions

The claims-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
