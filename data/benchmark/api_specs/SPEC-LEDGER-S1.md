---
document_id: SPEC-LEDGER-S1
document_type: api_spec
title: ledger-processor ingestion contract
system: ledger
service: ledger-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-processor ingestion contract

The ledger-processor ingestion contract contract.

## Fields

Every record must include account_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
