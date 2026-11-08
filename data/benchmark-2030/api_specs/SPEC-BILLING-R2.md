---
document_id: SPEC-BILLING-R2
document_type: api_spec
title: billing-partner-api limits
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api limits

The billing-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
