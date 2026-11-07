---
document_id: SPEC-BILLING-S1
document_type: api_spec
title: billing-processor ingestion contract
system: billing
service: billing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-processor ingestion contract

The billing-processor ingestion contract contract.

## Fields

Every record must include account_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
