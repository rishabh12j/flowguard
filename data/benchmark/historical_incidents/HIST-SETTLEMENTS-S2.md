---
document_id: HIST-SETTLEMENTS-S2
document_type: historical_incident
title: Records rejected after a type change
system: settlements
service: settlements-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Records rejected after a type change

## Symptoms

settlements-processor rejected records after a release.

## Root cause

A numeric field started arriving as text.

## Resolution

The mapping was updated and records replayed after approval.

## Follow-up

Contract tests were recommended. They were not implemented.
