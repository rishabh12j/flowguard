---
document_id: RB-INVOICING-R1
document_type: runbook
title: invoicing-partner-api rate limiting
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api rate limiting

## When to use

Use this runbook when invoicing-partner-api answers 429.

## Procedure

1. Check invoicing-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit invoicing-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
