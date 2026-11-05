---
document_id: SPEC-REWARDS-R2
document_type: api_spec
title: rewards-partner-api limits
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api limits

The rewards-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
