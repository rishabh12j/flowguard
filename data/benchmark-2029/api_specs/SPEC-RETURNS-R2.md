---
document_id: SPEC-RETURNS-R2
document_type: api_spec
title: returns-partner-api limits
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-partner-api limits

The returns-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
