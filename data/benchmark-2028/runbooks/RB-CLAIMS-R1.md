---
document_id: RB-CLAIMS-R1
document_type: runbook
title: claims-partner-api rate limiting
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api rate limiting

## When to use

Use this runbook when claims-partner-api answers 429.

## Procedure

1. Check claims-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit claims-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
