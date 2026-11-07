---
document_id: SPEC-PAYMENTS-R2
document_type: api_spec
title: payments-partner-api limits
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-partner-api limits

The payments-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
