---
document_id: RB-REWARDS-S1
document_type: runbook
title: Payload validation failures after a source release
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Payload validation failures after a source release

## When to use

Use this runbook when rewards-processor reports SchemaValidationError.

## Procedure

1. Compare the received fields with the contract.
2. Update rewards-processor's mapping, after approval.
3. Replay the failed records once the mapping is fixed.

## Warnings

- Do not disable payload validation.
- Do not replay before the fix.
