---
document_id: SPEC-PROCUREMENT-S1
document_type: api_spec
title: procurement-processor ingestion contract
system: procurement
service: procurement-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-processor ingestion contract

The procurement-processor ingestion contract contract.

## Fields

Every record must include supplier_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
