---
document_id: RB-PRICING-T2
document_type: runbook
title: Database queries timing out
system: pricing
service: pricing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Database queries timing out

## When to use

Use this runbook when pricing-processor's queries time out.

## Procedure

1. Check for a recent change to pricing-db's schema or indexes.
2. Roll back that change, after approval.

## Warnings

- Do not just raise the timeout.
