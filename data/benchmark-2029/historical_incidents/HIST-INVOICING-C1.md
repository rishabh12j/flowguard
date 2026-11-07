---
document_id: HIST-INVOICING-C1
document_type: historical_incident
title: invoicing-worker crash loop after a settings change
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-worker crash loop after a settings change

## Symptoms

Work stopped while invoicing-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
