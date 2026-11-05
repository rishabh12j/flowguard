---
document_id: RB-PAYROLL-E2
document_type: runbook
title: payroll-worker falling behind
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-worker falling behind

## When to use

Use this runbook when payroll-events grows and events arrive late.

## Procedure

1. Check payroll-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
