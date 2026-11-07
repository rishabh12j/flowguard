---
document_id: HIST-INVOICING-R2
document_type: historical_incident
title: Throttled after a quota cut
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Throttled after a quota cut

## Symptoms

Calls failed with 429 after the partner's change.

## Root cause

The partner lowered the quota below normal traffic.

## Resolution

invoicing-worker was rate-limited and the failures retried.

## Follow-up

Quota alerts were added.
