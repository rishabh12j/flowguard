---
document_id: RB-RETURNS-Q1
document_type: runbook
title: Amounts out of range
system: returns
service: returns-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Amounts out of range

## When to use

Use this runbook when returns-processor reports amounts out of range.

## Procedure

1. Check whether a source release changed the amounts' units.
2. Roll that release back, after approval, then replay the failures.

## Warnings

- Do not remove the range check.
