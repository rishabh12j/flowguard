---
document_id: SPEC-REWARDS-T2
document_type: api_spec
title: rewards-db schema
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-db schema

The rewards-db schema contract.

## Indexes

rewards-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
