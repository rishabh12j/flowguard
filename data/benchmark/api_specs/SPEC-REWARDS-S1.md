---
document_id: SPEC-REWARDS-S1
document_type: api_spec
title: rewards-processor ingestion contract
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-processor ingestion contract

The rewards-processor ingestion contract contract.

## Fields

Every record must include item_id, in snake_case.

## Validation

A record missing a required field is rejected with SchemaValidationError.
