---
document_id: SPEC-INVOICING-U2
document_type: api_spec
title: invoicing-partner-api connections
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api connections

The invoicing-partner-api connections contract.

## Keep-alive

Idle connections are closed after 60 seconds.

## Retries

Clients retry once.
