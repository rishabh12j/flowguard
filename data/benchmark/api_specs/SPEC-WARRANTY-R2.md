---
document_id: SPEC-WARRANTY-R2
document_type: api_spec
title: warranty-partner-api limits
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api limits

The warranty-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
