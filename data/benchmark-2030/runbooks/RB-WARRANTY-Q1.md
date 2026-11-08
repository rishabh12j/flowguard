---
document_id: RB-WARRANTY-Q1
document_type: runbook
title: Amounts out of range
system: warranty
service: warranty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Amounts out of range

## When to use

Use this runbook when warranty-processor reports amounts out of range.

## Procedure

1. Check whether a source release changed the amounts' units.
2. Roll that release back, after approval, then replay the failures.

## Warnings

- Do not remove the range check.
