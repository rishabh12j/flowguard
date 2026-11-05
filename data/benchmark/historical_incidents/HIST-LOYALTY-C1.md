---
document_id: HIST-LOYALTY-C1
document_type: historical_incident
title: loyalty-worker crash loop after a settings change
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-worker crash loop after a settings change

## Symptoms

Work stopped while loyalty-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
