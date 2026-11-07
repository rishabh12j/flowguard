---
document_id: HIST-PAYMENTS-C1
document_type: historical_incident
title: payments-worker crash loop after a settings change
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-worker crash loop after a settings change

## Symptoms

Work stopped while payments-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
