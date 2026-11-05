---
document_id: RB-PRICING-S2
document_type: runbook
title: Type mismatches in incoming records
system: pricing
service: pricing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Type mismatches in incoming records

## When to use

Use this runbook when pricing-processor rejects a field's type.

## Procedure

1. Find which field's type changed, and in which release.
2. Update pricing-processor's mapping to convert it, after approval.
3. Replay the failed records after the fix.

## Warnings

- Do not disable payload validation.
