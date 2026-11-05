---
document_id: RB-REWARDS-A2
document_type: runbook
title: rewards-worker can't authenticate to rewards-partner-api
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-worker can't authenticate to rewards-partner-api

## When to use

Use this runbook when rewards-partner-api answers 401 to rewards-worker.

## Procedure

1. Check whether a recent release of rewards-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with rewards-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
