---
document_id: RB-SFTP-DELIVERY
document_type: runbook
title: Payment file not acknowledged
system: vendor-payments
service: sftp-uploader
version: 1.1
effective_date: 2026-04-10
is_current: true
---

# Payment file not acknowledged

## When to use

Use this runbook when `bank-ack-poller` reports no acknowledgement for a payment file.

## Procedure

1. Find the upload log for the file and check its remote directory.
2. Compare it with the file drop contract: files must go to `/inbound/payments`.
3. If a recent change moved the upload directory, roll that change back, after approval.
4. Redeliver the file to `/inbound/payments`, after approval, and confirm the bank acknowledges it.

## Warnings

- Before redelivering, check that the bank has not already picked the file up, or vendors are paid twice.
- Never email a payment file to the bank to get around the SFTP drop.
