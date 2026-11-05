---
document_id: SPEC-ONBOARDING-R2
document_type: api_spec
title: onboarding-partner-api limits
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-partner-api limits

The onboarding-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
