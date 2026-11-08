---
document_id: SPEC-CLAIMS-T2
document_type: api_spec
title: claims-db schema
system: claims
service: claims-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-db schema

The claims-db schema contract.

## Indexes

claims-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
