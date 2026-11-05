---
document_id: HIST-REWARDS-C2
document_type: historical_incident
title: rewards-processor down after a flag change
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-processor down after a flag change

## Symptoms

rewards-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
