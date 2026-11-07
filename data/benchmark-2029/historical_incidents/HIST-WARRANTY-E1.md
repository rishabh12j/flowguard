---
document_id: HIST-WARRANTY-E1
document_type: historical_incident
title: Duplicates after a broker restart
system: warranty
service: warranty-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Duplicates after a broker restart

## Symptoms

Events were processed twice.

## Root cause

A restart redelivered uncommitted events, and the worker didn't check for duplicates.

## Resolution

The worker was paused, then resumed.

## Follow-up

Duplicate detection in warranty-worker was recommended. It was not implemented.
