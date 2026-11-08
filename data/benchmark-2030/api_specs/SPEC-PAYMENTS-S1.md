---
document_id: SPEC-PAYMENTS-S1
document_type: api_spec
title: payments-processor ingestion contract
system: payments
service: payments-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-processor ingestion contract

The payments-processor ingestion contract contract.

## Fields

Every record must include account_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
