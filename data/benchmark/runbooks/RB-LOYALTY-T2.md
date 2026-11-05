---
document_id: RB-LOYALTY-T2
document_type: runbook
title: Database queries timing out
system: loyalty
service: loyalty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Database queries timing out

## When to use

Use this runbook when loyalty-processor's queries time out.

## Procedure

1. Check for a recent change to loyalty-db's schema or indexes.
2. Roll back that change, after approval.

## Warnings

- Do not just raise the timeout.
