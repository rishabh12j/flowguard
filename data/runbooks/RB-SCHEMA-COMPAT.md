---
document_id: RB-SCHEMA-COMPAT
document_type: runbook
title: Schema compatibility check after source deployments
system: invoice-processing
service: invoice-transformer
version: 1.2
effective_date: 2026-03-01
is_current: true
---

# Schema compatibility check after source deployments

## When to use

Use this runbook when `invoice-transformer` reports `SchemaValidationError` or when invoices stop reaching `invoice-workflow` after a source system deployment.

## Prerequisites

- Read access to `invoice-transformer` logs and deployment records.
- The current version of the invoice ingestion contract.
- Approval from the on-call integration engineer before any replay or mapping deployment.

## Procedure

1. Find the first `SchemaValidationError` and record its correlation ID.
2. Compare the received payload fields with the invoice ingestion contract.
3. List source system deployments that happened before the first failure, including those before the alert window.
4. Check whether other source systems are still processing successfully.
5. If only one source is failing, update that source's transformation mapping.
6. Validate the mapping against a sample of failed payloads.
7. Replay messages from `invoice-transform-dlq` after approval.

## Warnings

- Do not disable payload validation to clear the queue.
- Do not replay messages before the mapping fix is deployed, because they will fail again.

## Verification and rollback

- Confirm replayed invoices appear in `invoice-workflow` with their original correlation context.
- Confirm `invoice-transform-dlq` is empty.
- If validation of the new mapping fails, roll back the mapping and keep messages in the queue.
