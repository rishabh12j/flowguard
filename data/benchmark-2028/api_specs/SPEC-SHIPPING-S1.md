---
document_id: SPEC-SHIPPING-S1
document_type: api_spec
title: shipping-processor ingestion contract
system: shipping
service: shipping-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-processor ingestion contract

The shipping-processor ingestion contract contract.

## Fields

Every record must include customer_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
