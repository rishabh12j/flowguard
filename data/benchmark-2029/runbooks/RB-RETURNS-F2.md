---
document_id: RB-RETURNS-F2
document_type: runbook
title: Export rejected by returns-partner-sftp
system: returns
service: returns-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Export rejected by returns-partner-sftp

## When to use

Use this runbook when returns-partner-sftp rejects a file.

## Procedure

1. Read the rejection reason.
2. Roll back the change that caused it, after approval.
3. Redeliver the file.

## Warnings

- Never email export files.
