---
document_id: SPEC-ONBOARDING-T2
document_type: api_spec
title: onboarding-db schema
system: onboarding
service: onboarding-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-db schema

The onboarding-db schema contract.

## Indexes

onboarding-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
