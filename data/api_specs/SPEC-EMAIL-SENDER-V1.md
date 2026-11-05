---
document_id: SPEC-EMAIL-SENDER-V1
document_type: api_spec
title: Email sender configuration
system: customer-notifications
service: email-sender
version: 5.0
effective_date: 2026-09-01
is_current: true
---

# Email sender configuration

`email-sender` reads messages from `notification-queue` and sends each one through `smtp-relay`.

## Required settings

`SMTP_RELAY_HOST` and `SMTP_RELAY_PORT` are required. Without them, `email-sender` refuses to start and exits with a configuration error, so it never connects to the queue.

## Optional settings

`SENDER_BATCH_SIZE` defaults to 50, and `SENDER_RETRY_LIMIT` defaults to 3.
