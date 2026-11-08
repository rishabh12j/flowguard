---
document_id: SPEC-INVENTORY-S1
document_type: api_spec
title: inventory-processor ingestion contract
system: inventory
service: inventory-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-processor ingestion contract

The inventory-processor ingestion contract contract.

## Fields

Every record must include item_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
