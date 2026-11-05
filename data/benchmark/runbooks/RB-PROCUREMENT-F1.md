---
document_id: RB-PROCUREMENT-F1
document_type: runbook
title: Export not acknowledged
system: procurement
service: procurement-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Export not acknowledged

## When to use

Use this runbook when procurement-partner-sftp doesn't acknowledge an export.

## Procedure

1. Check the directory in the upload log.
2. Roll back the change that moved it, after approval.
3. Redeliver the file to /inbound.

## Warnings

- Check the file wasn't picked up before redelivering.
