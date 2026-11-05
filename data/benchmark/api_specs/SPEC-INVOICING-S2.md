---
document_id: SPEC-INVOICING-S2
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

## Types

amount is a number in the record's currency units.

## Validation

A field of the wrong type is rejected with SchemaValidationError.
