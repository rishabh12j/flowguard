---
document_id: SPEC-INVENTORY-T2
document_type: api_spec
title: inventory-db schema
system: inventory
service: inventory-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-db schema

The inventory-db schema contract.

## Indexes

inventory-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
