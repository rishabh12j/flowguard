---
document_id: SPEC-PRICING-T2
document_type: api_spec
title: pricing-db schema
system: pricing
service: pricing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-db schema

The pricing-db schema contract.

## Indexes

pricing-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
