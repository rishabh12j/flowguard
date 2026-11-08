---
document_id: RB-SHIPPING-F2
document_type: runbook
title: Export rejected by shipping-partner-sftp
system: shipping
service: shipping-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Export rejected by shipping-partner-sftp

## When to use

Use this runbook when shipping-partner-sftp rejects a file.

## Procedure

1. Read the rejection reason.
2. Roll back the change that caused it, after approval.
3. Redeliver the file.

## Warnings

- Never email export files.
