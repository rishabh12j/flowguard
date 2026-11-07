---
document_id: SPEC-CATALOGUE-T2
document_type: api_spec
title: catalogue-db schema
system: catalogue
service: catalogue-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-db schema

The catalogue-db schema contract.

## Indexes

catalogue-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
