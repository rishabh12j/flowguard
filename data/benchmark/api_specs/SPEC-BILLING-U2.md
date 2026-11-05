---
document_id: SPEC-BILLING-U2
document_type: api_spec
title: billing-partner-api connections
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api connections

The billing-partner-api connections contract.

## Keep-alive

Idle connections are closed after 60 seconds.

## Retries

Clients retry once.
