---
document_id: HIST-INVOICING-Z1
document_type: historical_incident
title: Writes refused after a scope change
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Writes refused after a scope change

## Symptoms

invoicing-partner-api refused writes with 403.

## Root cause

A release requested fewer scopes than the integration needed.

## Resolution

The release was rolled back after approval.

## Follow-up

The review recommended a test for required scopes. It was not implemented.
