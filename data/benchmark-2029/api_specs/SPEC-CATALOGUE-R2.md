---
document_id: SPEC-CATALOGUE-R2
document_type: api_spec
title: catalogue-partner-api limits
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api limits

The catalogue-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
