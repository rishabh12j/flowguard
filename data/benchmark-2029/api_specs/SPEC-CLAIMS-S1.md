---
document_id: SPEC-CLAIMS-S1
document_type: api_spec
title: claims-processor ingestion contract
system: claims
service: claims-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-processor ingestion contract

The claims-processor ingestion contract contract.

## Fields

Every record must include order_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
