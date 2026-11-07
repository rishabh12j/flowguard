---
document_id: SPEC-SUBSCRIPTIONS-S1
document_type: api_spec
title: subscriptions-processor ingestion contract
system: subscriptions
service: subscriptions-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-processor ingestion contract

The subscriptions-processor ingestion contract contract.

## Fields

Every record must include supplier_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
