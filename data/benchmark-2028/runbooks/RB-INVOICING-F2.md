---
document_id: RB-INVOICING-F2
document_type: runbook
title: Export rejected by invoicing-partner-sftp
system: invoicing
service: invoicing-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Export rejected by invoicing-partner-sftp

## When to use

Use this runbook when invoicing-partner-sftp rejects a file.

## Procedure

1. Read the rejection reason.
2. Roll back the change that caused it, after approval.
3. Redeliver the file.

## Warnings

- Never email export files.
