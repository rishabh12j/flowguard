---
document_id: SPEC-BILLING-T2
document_type: api_spec
title: billing-db schema
system: billing
service: billing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-db schema

The billing-db schema contract.

## Indexes

billing-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
