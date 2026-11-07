---
document_id: RB-CLAIMS-R2
document_type: runbook
title: Quota changes at claims-partner-api
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Quota changes at claims-partner-api

## When to use

Use this runbook when claims-partner-api answers 429 after a quota change.

## Procedure

1. Check the new quota.
2. Limit claims-worker to it, after approval, then retry the failures.

## Warnings

- Do not retry immediately.
