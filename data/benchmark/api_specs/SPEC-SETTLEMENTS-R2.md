---
document_id: SPEC-SETTLEMENTS-R2
document_type: api_spec
title: settlements-partner-api limits
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api limits

The settlements-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
