---
document_id: HIST-PROCUREMENT-A2
document_type: historical_incident
title: procurement-partner-api rejected a new key
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-partner-api rejected a new key

## Symptoms

Calls failed with 401 just after a release.

## Root cause

The release used a key that hadn't been registered with procurement-partner-api.

## Resolution

The release was rolled back after approval.

## Follow-up

The review recommended registering keys before releases. It was not implemented.
