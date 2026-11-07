---
document_id: RB-ONBOARDING-A2
document_type: runbook
title: onboarding-worker can't authenticate to onboarding-partner-api
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-worker can't authenticate to onboarding-partner-api

## When to use

Use this runbook when onboarding-partner-api answers 401 to onboarding-worker.

## Procedure

1. Check whether a recent release of onboarding-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with onboarding-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
