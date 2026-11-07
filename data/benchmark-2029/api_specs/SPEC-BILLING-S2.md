---
document_id: SPEC-BILLING-S2
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

## Types

amount is a number in the record's currency units.

## Validation

A field of the wrong type is rejected with SchemaValidationError.
