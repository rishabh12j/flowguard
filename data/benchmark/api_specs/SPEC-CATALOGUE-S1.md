---
document_id: SPEC-CATALOGUE-S1
document_type: api_spec
title: catalogue-processor ingestion contract
system: catalogue
service: catalogue-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-processor ingestion contract

The catalogue-processor ingestion contract contract.

## Fields

Every record must include account_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
