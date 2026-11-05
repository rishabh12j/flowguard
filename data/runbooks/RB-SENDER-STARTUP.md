---
document_id: RB-SENDER-STARTUP
document_type: runbook
title: Email sender won't start
system: customer-notifications
service: email-sender
version: 1.1
effective_date: 2026-06-10
is_current: true
---

# Email sender won't start

## When to use

Use this runbook when `email-sender` restarts repeatedly and the notification queue grows.

## Procedure

1. Read the startup error in the latest `email-sender` logs.
2. If a recent deployment changed or removed a setting, roll that deployment back, after approval.
3. Confirm `email-sender` stays up and the queue drains.

## Warnings

- Do not purge `notification-queue`: the queued emails are still owed to customers.
- Do not set the relay address inside the code.
