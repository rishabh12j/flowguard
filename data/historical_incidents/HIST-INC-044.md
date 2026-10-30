---
document_id: HIST-INC-044
document_type: historical_incident
title: Invoice validation failures after supplier field rename
system: invoice-processing
service: invoice-transformer
version: 1.0
effective_date: 2026-01-15
is_current: true
---

# HIST-INC-044: Invoice validation failures after supplier field rename

## Symptoms

Invoices from `supplier-api` stopped reaching `invoice-workflow`. `invoice-transformer` reported `SchemaValidationError` for a missing required field, while `supplier-api` kept returning successful responses.

## Root cause

A `supplier-api` release renamed `supplier_code` to `supplier_id` without a matching update to the transformation mapping.

## Resolution

The mapping was updated and validated against failed payloads. Messages in `invoice-transform-dlq` were then replayed after approval.

## Follow-up

The review recommended contract tests in the source deployment pipeline. They were not implemented.
