---
document_id: HIST-CATALOGUE-T2
document_type: historical_incident
title: Timeouts after an index change
system: catalogue
service: catalogue-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Timeouts after an index change

## Symptoms

Lookups timed out after a database change.

## Root cause

An index the main query used was removed.

## Resolution

The index was restored after approval.

## Follow-up

Index changes now need a query review.
