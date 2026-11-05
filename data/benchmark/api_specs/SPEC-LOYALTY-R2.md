---
document_id: SPEC-LOYALTY-R2
document_type: api_spec
title: loyalty-partner-api limits
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api limits

The loyalty-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
