---
document_id: RB-DUPLICATE-REFUNDS
document_type: runbook
title: Duplicate refunds
system: refunds
service: refund-worker
version: 1.0
effective_date: 2026-03-15
is_current: true
---

# Duplicate refunds

## When to use

Use this runbook when `refund-ledger` reports `DuplicateRefundError`.

## Procedure

1. Check for a broker failover or consumer rebalance just before the first duplicate.
2. Pause `refund-worker`, after approval, so no more refunds are paid twice.
3. Send the list of duplicate refunds to finance for recovery.
4. Resume `refund-worker` only once it skips refunds it has already paid.

## Warnings

- Do not reverse the duplicate payments from the gateway directly. Finance recovers them.
- Do not reset the consumer offset by hand.
