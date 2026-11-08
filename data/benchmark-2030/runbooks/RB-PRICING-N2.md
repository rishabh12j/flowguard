---
document_id: RB-PRICING-N2
document_type: runbook
title: pricing-partner-api outage
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-partner-api outage

## When to use

Use this runbook when connections to pricing-partner-api are refused.

## Procedure

1. Check pricing-partner-api's status page and alerts.
2. Tell the pricing-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
