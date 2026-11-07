---
document_id: RB-PAYMENTS-R2
document_type: runbook
title: Quota changes at payments-partner-api
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Quota changes at payments-partner-api

## When to use

Use this runbook when payments-partner-api answers 429 after a quota change.

## Procedure

1. Check the new quota.
2. Limit payments-worker to it, after approval, then retry the failures.

## Warnings

- Do not retry immediately.
