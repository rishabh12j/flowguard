---
document_id: HIST-PRICING-C1
document_type: historical_incident
title: pricing-worker crash loop after a settings change
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-worker crash loop after a settings change

## Symptoms

Work stopped while pricing-worker restarted repeatedly.

## Root cause

A release dropped a required setting.

## Resolution

The release was rolled back after approval.

## Follow-up

A restart alert was recommended. It was not implemented.
