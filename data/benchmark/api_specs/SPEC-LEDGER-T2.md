---
document_id: SPEC-LEDGER-T2
document_type: api_spec
title: ledger-db schema
system: ledger
service: ledger-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-db schema

The ledger-db schema contract.

## Indexes

ledger-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
