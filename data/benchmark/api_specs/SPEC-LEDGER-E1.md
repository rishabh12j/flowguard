---
document_id: SPEC-LEDGER-E1
document_type: api_spec
title: ledger-events delivery
system: ledger
service: ledger-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-events delivery

The ledger-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
