---
document_id: SPEC-INVOICING-S1
document_type: api_spec
title: invoicing-processor ingestion contract
system: invoicing
service: invoicing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-processor ingestion contract

The invoicing-processor ingestion contract contract.

## Fields

Every record must include customer_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
