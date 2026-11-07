---
document_id: SPEC-PRICING-S1
document_type: api_spec
title: pricing-processor ingestion contract
system: pricing
service: pricing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-processor ingestion contract

The pricing-processor ingestion contract contract.

## Fields

Every record must include customer_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
