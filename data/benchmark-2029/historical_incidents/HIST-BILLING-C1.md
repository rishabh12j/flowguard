---
document_id: HIST-BILLING-C1
document_type: historical_incident
title: billing-worker crash loop after a settings change
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-worker crash loop after a settings change

## Symptoms

Work stopped while billing-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
