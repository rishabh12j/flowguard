---
document_id: HIST-PROCUREMENT-C1
document_type: historical_incident
title: procurement-worker crash loop after a settings change
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-worker crash loop after a settings change

## Symptoms

Work stopped while procurement-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
