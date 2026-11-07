---
document_id: RB-REWARDS-T1
document_type: runbook
title: Connection pool exhausted
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Connection pool exhausted

## When to use

Use this runbook when rewards-processor times out waiting for a database connection.

## Procedure

1. Check the connection wait metric and the configured pool size.
2. Roll back a recent change to the pool size, after approval.

## Warnings

- Do not raise the database's connection limit.
