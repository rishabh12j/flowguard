---
document_id: SPEC-RETURNS-T2
document_type: api_spec
title: returns-db schema
system: returns
service: returns-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-db schema

The returns-db schema contract.

## Indexes

returns-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
