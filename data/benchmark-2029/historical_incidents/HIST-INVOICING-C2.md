---
document_id: HIST-INVOICING-C2
document_type: historical_incident
title: invoicing-processor down after a flag change
system: invoicing
service: invoicing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-processor down after a flag change

## Symptoms

invoicing-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
