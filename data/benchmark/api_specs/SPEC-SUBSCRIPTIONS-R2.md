---
document_id: SPEC-SUBSCRIPTIONS-R2
document_type: api_spec
title: subscriptions-partner-api limits
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api limits

The subscriptions-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
