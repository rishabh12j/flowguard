---
document_id: RB-PRICING-A2
document_type: runbook
title: pricing-worker can't authenticate to pricing-partner-api
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-worker can't authenticate to pricing-partner-api

## When to use

Use this runbook when pricing-partner-api answers 401 to pricing-worker.

## Procedure

1. Check whether a recent release of pricing-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with pricing-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
