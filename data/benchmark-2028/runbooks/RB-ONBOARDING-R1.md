---
document_id: RB-ONBOARDING-R1
document_type: runbook
title: onboarding-partner-api rate limiting
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-partner-api rate limiting

## When to use

Use this runbook when onboarding-partner-api answers 429.

## Procedure

1. Check onboarding-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit onboarding-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
