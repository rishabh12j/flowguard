---
document_id: HIST-INC-101
document_type: historical_incident
title: Services unreachable after a DNS migration
system: ledger-sync
service: ledger-sync
version: 1.0
effective_date: 2026-07-12
is_current: true
---

# HIST-INC-101: Services unreachable after a DNS migration

## Symptoms

Several jobs failed overnight with "Name or service not known".

## Root cause

A DNS zone migration skipped records that had been added by hand, so their names stopped resolving.

## Resolution

The missing records were restored, and the failed jobs were re-run after approval.

## Follow-up

The review recommended comparing every record before and after a zone migration. It was not implemented.
