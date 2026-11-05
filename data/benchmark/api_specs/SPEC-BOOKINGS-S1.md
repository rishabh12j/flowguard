---
document_id: SPEC-BOOKINGS-S1
document_type: api_spec
title: bookings-processor ingestion contract
system: bookings
service: bookings-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-processor ingestion contract

The bookings-processor ingestion contract contract.

## Fields

Every record must include supplier_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
