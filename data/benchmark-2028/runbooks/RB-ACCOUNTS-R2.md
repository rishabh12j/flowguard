---
document_id: RB-ACCOUNTS-R2
document_type: runbook
title: Quota changes at accounts-partner-api
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Quota changes at accounts-partner-api

## When to use

Use this runbook when accounts-partner-api answers 429 after a quota change.

## Procedure

1. Check the new quota.
2. Limit accounts-worker to it, after approval, then retry the failures.

## Warnings

- Do not retry immediately.
