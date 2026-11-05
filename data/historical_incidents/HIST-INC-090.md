---
document_id: HIST-INC-090
document_type: historical_incident
title: Duplicate payouts after a broker restart
system: refunds
service: refund-worker
version: 1.0
effective_date: 2026-05-30
is_current: true
---

# HIST-INC-090: Duplicate payouts after a broker restart

## Symptoms

A batch of refunds was paid twice, and finance found them in reconciliation.

## Root cause

A broker restart redelivered events after the last committed offset, and `refund-worker` paid them again because it did not check whether a refund was already paid.

## Resolution

The worker was paused, finance recovered the duplicates, and the worker resumed.

## Follow-up

The review recommended making `refund-worker` skip refunds it has already paid. It was not implemented.
