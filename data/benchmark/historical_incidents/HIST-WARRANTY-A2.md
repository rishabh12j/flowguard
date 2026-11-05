---
document_id: HIST-WARRANTY-A2
document_type: historical_incident
title: warranty-partner-api rejected a new key
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api rejected a new key

## Symptoms

Calls failed with 401 just after a release.

## Root cause

The release used a key that hadn't been registered with warranty-partner-api.

## Resolution

The release was rolled back after approval.

## Follow-up

The review recommended registering keys before releases. It was not implemented.
