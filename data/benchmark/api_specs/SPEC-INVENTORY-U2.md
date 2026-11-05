---
document_id: SPEC-INVENTORY-U2
document_type: api_spec
title: inventory-partner-api connections
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api connections

The inventory-partner-api connections contract.

## Keep-alive

Idle connections are closed after 60 seconds.

## Retries

Clients retry once.
