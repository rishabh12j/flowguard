---
document_id: HIST-RETURNS-Q1
document_type: historical_incident
title: Amounts a hundred times too large
system: returns
service: returns-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Amounts a hundred times too large

## Symptoms

returns-processor rejected most records.

## Root cause

A source sent cents instead of units.

## Resolution

The release was rolled back after approval.

## Follow-up

A contract test for units was recommended. It was not implemented.
