---
document_id: SPEC-INVOICING-C1
document_type: api_spec
title: invoicing-worker settings
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-worker settings

The invoicing-worker settings contract.

## Required

SERVICE_REGION is required. Without it, invoicing-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
