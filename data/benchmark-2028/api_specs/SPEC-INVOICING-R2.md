---
document_id: SPEC-INVOICING-R2
document_type: api_spec
title: invoicing-partner-api limits
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api limits

The invoicing-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
