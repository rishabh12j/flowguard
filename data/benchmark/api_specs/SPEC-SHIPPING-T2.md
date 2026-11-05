---
document_id: SPEC-SHIPPING-T2
document_type: api_spec
title: shipping-db schema
system: shipping
service: shipping-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-db schema

The shipping-db schema contract.

## Indexes

shipping-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
