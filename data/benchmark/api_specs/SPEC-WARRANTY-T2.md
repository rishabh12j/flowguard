---
document_id: SPEC-WARRANTY-T2
document_type: api_spec
title: warranty-db schema
system: warranty
service: warranty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-db schema

The warranty-db schema contract.

## Indexes

warranty-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
