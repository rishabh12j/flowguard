---
document_id: HIST-PRICING-C2
document_type: historical_incident
title: pricing-processor down after a flag change
system: pricing
service: pricing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-processor down after a flag change

## Symptoms

pricing-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
