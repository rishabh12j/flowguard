---
document_id: SPEC-ACCOUNTS-S1
document_type: api_spec
title: accounts-processor ingestion contract
system: accounts
service: accounts-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-processor ingestion contract

The accounts-processor ingestion contract contract.

## Fields

Every record must include supplier_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
