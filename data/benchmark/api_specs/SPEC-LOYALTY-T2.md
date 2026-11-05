---
document_id: SPEC-LOYALTY-T2
document_type: api_spec
title: loyalty-db schema
system: loyalty
service: loyalty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-db schema

The loyalty-db schema contract.

## Indexes

loyalty-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
