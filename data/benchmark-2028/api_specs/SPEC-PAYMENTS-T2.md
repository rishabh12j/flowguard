---
document_id: SPEC-PAYMENTS-T2
document_type: api_spec
title: payments-db schema
system: payments
service: payments-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-db schema

The payments-db schema contract.

## Indexes

payments-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
