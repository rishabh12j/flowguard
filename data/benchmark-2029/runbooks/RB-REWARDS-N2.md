---
document_id: RB-REWARDS-N2
document_type: runbook
title: rewards-partner-api outage
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api outage

## When to use

Use this runbook when connections to rewards-partner-api are refused.

## Procedure

1. Check rewards-partner-api's status page and alerts.
2. Tell the rewards-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
