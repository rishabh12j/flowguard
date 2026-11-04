---
document_id: HIST-INC-051
document_type: historical_incident
title: Settlement import failed after the bank credential expired
system: payment-reconciliation
service: settlement-importer
version: 1.0
effective_date: 2026-05-04
is_current: true
---

# HIST-INC-051: Settlement import failed after the bank credential expired

## Symptoms

The morning settlement import failed with `401 Unauthorized`, and the reconciliation report was incomplete.

## Root cause

The bank client credential reached its 90-day expiry. The expiry alert fired at midnight, but nobody was on call for it.

## Resolution

A new credential was issued and stored in the secrets manager, and the import was re-run for the missed day after approval.

## Follow-up

The review recommended an alert 14 days before expiry. It was not implemented.
