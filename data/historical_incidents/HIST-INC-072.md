---
document_id: HIST-INC-072
document_type: historical_incident
title: Payment file missed after an SFTP directory change
system: vendor-payments
service: sftp-uploader
version: 1.0
effective_date: 2026-03-22
is_current: true
---

# HIST-INC-072: Payment file missed after an SFTP directory change

## Symptoms

The bank never acknowledged the morning payment file, and supplier payments were a day late.

## Root cause

A server migration changed the uploader's remote directory, so the file landed in a directory the bank does not read.

## Resolution

The directory setting was corrected and the file was redelivered to `/inbound/payments` after approval.

## Follow-up

The review recommended a check that fails the upload when the directory is not `/inbound/payments`. It was not implemented.
