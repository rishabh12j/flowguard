---
document_id: HIST-BILLING-C2
document_type: historical_incident
title: billing-processor down after a flag change
system: billing
service: billing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-processor down after a flag change

## Symptoms

billing-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
