---
document_id: SPEC-CLAIMS-R2
document_type: api_spec
title: claims-partner-api limits
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api limits

The claims-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
