---
document_id: SPEC-SUBSCRIPTIONS-T2
document_type: api_spec
title: subscriptions-db schema
system: subscriptions
service: subscriptions-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-db schema

The subscriptions-db schema contract.

## Indexes

subscriptions-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
