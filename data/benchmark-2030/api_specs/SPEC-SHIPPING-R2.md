---
document_id: SPEC-SHIPPING-R2
document_type: api_spec
title: shipping-partner-api limits
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-partner-api limits

The shipping-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
